"""
plecs_connector.py  —  Adaptador de Simulação de Bateria

Responsabilidade: fornecer a interface de simulação mensal para o SimulationManager.
Roteia a chamada para o backend escolhido pelo usuário no menu inicial:

  backend = "python"  →  Simulador Python puro (battery_simulator.py)
  backend = "plecs"   →  PLECS via XML-RPC (requer servidor PLECS aberto)

A assinatura pública de run_monthly_simulation() é a mesma em ambos os backends,
garantindo compatibilidade total com simulation.py.
"""

import pandas as pd
import numpy as np
import xmlrpc.client
from scipy.io import savemat

from besx.config import BateriaConfig, Settings, ROOT_DIR
from besx.infrastructure.logging.logger import logger
from besx.domain.models.battery_simulator import simular_soc_mes


# ------------------------------------------------------------------ #
#  Interface pública                                                   #
# ------------------------------------------------------------------ #

def run_monthly_simulation(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
    backend: str = "python",
) -> pd.DataFrame:
    """
    Simula um mês de operação da bateria e retorna o perfil de SOC.

    Args:
        df_mes (pd.DataFrame):
            Perfil de potência do mês — colunas [Tempo (min), Potencia_kW].
        soh_atual (float):
            State of Health no início do mês (fração 0–1).
        SOC_0 (float):
            SOC inicial do mês (fração 0–1).
        ctt (int):
            Número sequencial do mês (logging / debug).
        config (Settings):
            Objeto de configuração da simulação (Pydantic).
        backend (str):
            "python"  → simulador Python interno
            "plecs"   → PLECS via XML-RPC

    Returns:
        pd.DataFrame: colunas ['Tempo' (s), 'SOC' (fração 0-1)].
    """
    if backend == "plecs":
        return _run_plecs(df_mes, soh_atual, SOC_0, ctt, config)
    else:
        return _run_python(df_mes, soh_atual, SOC_0, ctt, config)


def extrair_soc_final(df_soc: pd.DataFrame) -> float:
    """
    Extrai o SOC final da simulação mensal como fração 0–1.

    Args:
        df_soc: DataFrame com colunas ['Tempo', 'SOC']

    Returns:
        float: SOC final (0–1)
    """
    if df_soc is None or df_soc.empty:
        raise ValueError("DataFrame de SOC vazio ou inválido.")

    df_soc = df_soc.sort_values('Tempo')
    soc_final = float(df_soc['SOC'].iloc[-1])  # Já está em fração no novo padrão

    if not 0.0 <= soc_final <= 1.0:
        raise ValueError(f"SOC final fora do intervalo físico: {soc_final:.4f}")

    return soc_final


def close_plecs_server() -> None:
    """
    Tenta fechar o servidor PLECS (no-op se backend Python estiver em uso).
    """
    try:
        plecs_server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2")
        plecs_server.plecs.quit()
        logger.info("Comando para fechar o servidor PLECS enviado com sucesso.")
    except Exception as e:
        logger.info(f"close_plecs_server(): sem servidor ativo ({e})")


# ------------------------------------------------------------------ #
#  Backend Python                                                      #
# ------------------------------------------------------------------ #

def _run_python(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
) -> pd.DataFrame:
    """Delega ao simulador Python de integração de Coulomb."""
    cfg_bat = config.bateria
    logger.info(
        f"[Python] Mês {ctt} | SOC_0={SOC_0*100:.1f}% | SOH={soh_atual*100:.1f}%"
    )

    cols = df_mes.columns.tolist()
    col_t = next((c for c in cols if 'tempo' in c.lower() or 'timestamp' in c.lower()), cols[0])
    col_p = next((c for c in cols if 'pot' in c.lower() and c != col_t), cols[1] if len(cols)>1 else cols[0])
    
    # Standardized column name from Step 1 Normalization
    q_col_name = 'Potencia_Reativa_Bateria_VAr'
    
    t_min = df_mes[col_t].min()
    t_max = df_mes[col_t].max()
    
    novo_tempo = np.arange(t_min, t_max + 0.1, 1.0) # 1.0 minute interval
    nova_potencia = np.interp(novo_tempo, df_mes[col_t].values, df_mes[col_p].values)
    
    data_upsampled = {
        col_t: novo_tempo,
        col_p: nova_potencia
    }

    if q_col_name in df_mes.columns:
        df_mes_upsampled_q = np.interp(novo_tempo, df_mes[col_t].values, df_mes[q_col_name].values)
        data_upsampled[q_col_name] = df_mes_upsampled_q
        logger.info(f"[Python] Standardized reactive column found and interpolated: {q_col_name}")
    else:
        # Fallback for manual uploads or partial data
        col_q_guess = next((c for c in cols if 'reativa' in c.lower() or 'var' in c.lower()), None)
        if col_q_guess:
             nova_potencia_reativa = np.interp(novo_tempo, df_mes[col_t].values, df_mes[col_q_guess].values)
             data_upsampled[q_col_name] = nova_potencia_reativa
             logger.info(f"[Python] Guessed reactive column '{col_q_guess}' used as {q_col_name}")
        else:
             data_upsampled[q_col_name] = 0.0
             logger.warning(f"No reactive column found (Standard: {q_col_name}). Defaulting to 0.0 VAr.")

    df_mes_upsampled = pd.DataFrame(data_upsampled)

    return simular_soc_mes(
        df_mes=df_mes_upsampled,
        soh_atual=soh_atual,
        soc_inicial=SOC_0,
        cfg_bat=cfg_bat, 
        n_unidades=config.simulacao.n_unidades
    )


# ------------------------------------------------------------------ #
#  Backend PLECS                                                       #
# ------------------------------------------------------------------ #

def _run_plecs(
    df_mes: pd.DataFrame,
    soh_atual: float,
    SOC_0: float,
    ctt: int,
    config: Settings,
) -> pd.DataFrame | None:
    """Executa a simulação via XML-RPC no PLECS."""
    plecs_server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2")
    cfg_plecs    = config.plecs
    cfg_bat      = config.bateria

    # Identifica as colunas independentemente da ordem (Tempo, Potência)
    col_vagas = df_mes.columns.tolist()
    # Procura coluna de tempo (contendo 'Tempo' ou 'timestamp')
    col_t = next((c for c in col_vagas if 'tempo' in c.lower() or 'timestamp' in c.lower()), col_vagas[0])
    # Procura coluna de potência (contendo 'pot' ou 'potencia')
    col_p = next((c for c in col_vagas if 'pot' in c.lower() and c != col_t), col_vagas[1] if len(col_vagas)>1 else col_vagas[0])

    df_tmp = df_mes[[col_t, col_p]].copy()
    
    # --- 1. Cálculo dinâmico do tempo de simulação (TimeSpan) ---
    if len(df_mes) > 1:
        dt = float(df_mes[col_t].iloc[1] - df_mes[col_t].iloc[0])
    else:
        dt = config.dados_entrada.dt_minutos
        
    if not isinstance(dt, (int, float)) or dt <= 0:
        dt = 5.0 # Fallback 5 min
    
    sim_duration_sec = len(df_mes) * dt * 60
    logger.info(f"[PLECS] Auditoria Sincronismo: len(df)={len(df_mes)}, dt_ext={dt}, sim_duration={sim_duration_sec}s")
    
    # --- 2. Preparação do arquivo .mat (Normalização para t=0 e min->s) ---
    t_zero = df_tmp[col_t].iloc[0]
    df_tmp[col_t] = (df_tmp[col_t] - t_zero) * 60.0
    
    # [UNIDADES] O PLECS espera Potência em Watts. Multiplicamos se for kW.
    if 'kw' in col_p.lower():
        df_tmp[col_p] = df_tmp[col_p] * 1000.0
        logger.info("[PLECS] Convertendo Potência de kW para Watts para o .mat")

    # [ALINHAMENTO] Conforme análise ponto-a-ponto, P > 0 já corresponde a carga no PLECS.
    # Removida inversão de sinal.
    
    matriz_dados_plecs = df_tmp.to_numpy().T

    try:
        entrada_pot_path = str(ROOT_DIR / cfg_plecs.ARQUIVO_ENTRADA_POT)
        logger.info(f"[PLECS] Salvando {entrada_pot_path} ({sim_duration_sec}s)")
        savemat(entrada_pot_path, {'Pot_Input': matriz_dados_plecs})
    except Exception as e:
        logger.error(f"[PLECS] Erro ao criar arquivo .mat: {e}")
        with open(".gsd/last_plecs_error.log", "a") as f:
            f.write(f"[PLECS] Erro ao criar arquivo .mat: {e}\n")
        return None

    # Monta ModelVars e executa
    model_vars = _montar_model_vars_bateria(cfg_bat, SOC_0, soh_atual)
    model_vars['TimeSpan'] = sim_duration_sec

    try:
        # Tenta abrir o Scope2 no PLECS para visualização em tempo real
        try:
            scope_path = f"{cfg_plecs.MODELO_PLECS}/Scope2"
            plecs_server.plecs.scope(scope_path, 'Open')
            logger.info(f"[PLECS] Scope2 aberto para visualização.")
        except Exception as scope_e:
            logger.debug(f"[PLECS] Skip openScope (método 'scope' pode não estar exposto): {scope_e}")
        
        opts = {
            'ModelVars': model_vars,
            'TimeSpan': sim_duration_sec
        }
        plecs_server.plecs.simulate(cfg_plecs.MODELO_PLECS, opts)
        logger.info(f"[PLECS] Simulação concluída ({sim_duration_sec}s) — mês {ctt}")
    except Exception as e:
        logger.error(f"[PLECS] Erro durante a simulação: {e}")
        with open(".gsd/last_plecs_error.log", "a") as f:
            f.write(f"[PLECS] Erro durante a simulação: {e}\n")
        return None

    # Lê o CSV de saída
    try:
        # Lê Arquivo com novo Formato de exportacao forçado para a raiz do projeto
        out_file = str(ROOT_DIR / "dadosnovos.csv")
        # O PLECS Scope exporta o header diretamente na linha 0.
        df_plecs = pd.read_csv(out_file)
        
        # O Plecs exporta na ordem fixa das portas do Scope:
        # 0: Time -> Tempo da Simulação em Segundos
        # 1: Vm1:Measured voltage -> Tensão do Banco
        # 2: Gain1 -> Potência
        # 3: C-Script:2 -> Estado (Carregando ou Descarregando)
        # 4: C-Script:1 -> Corrente do Banco
        # 5: Gain1.1 (ou Integrator) -> SOC
        
        cols = df_plecs.columns
        
        df_plecs.rename(columns={
            cols[0]: "Tempo",
            cols[1]: "Tensao_Term_V",
            cols[4]: "Corrente_A",
            cols[5]: "SOC"
        }, inplace=True)
        
        # [ALINHAMENTO] Removida inversão de sinal da corrente.
        # A análise ponto-a-ponto confirmou que o sinal nativo do PLECS (Negativo para Descarga)
        # já está em harmonia com o motor Python.
        df_plecs['Corrente_A'] = pd.to_numeric(df_plecs['Corrente_A'], errors='coerce')
        
        # Garantir que os dados sejam numericos
        df_plecs['Tempo'] = pd.to_numeric(df_plecs['Tempo'], errors='coerce')
        df_plecs['Tensao_Term_V'] = pd.to_numeric(df_plecs['Tensao_Term_V'], errors='coerce')
        df_plecs['Corrente_A'] = pd.to_numeric(df_plecs['Corrente_A'], errors='coerce')
        df_plecs['SOC'] = pd.to_numeric(df_plecs['SOC'], errors='coerce')
        
        df_soc_mes = df_plecs[['Tempo', 'Tensao_Term_V', 'Corrente_A', 'SOC']].dropna()
        
        # O PLECS geralmente exporta em %, convertemos para fração (0-1) para o padrão do Backend.
        # Check robusto: se o valor máximo for > 1.1, dividimos por 100.
        if df_soc_mes['SOC'].max() > 1.1:
            df_soc_mes['SOC'] = df_soc_mes['SOC'] / 100.0
        
        return df_soc_mes
        
        
    except Exception as e:
        logger.error(f"[PLECS] Erro ao ler arquivo de saída: {e}")
        with open(".gsd/last_plecs_error.log", "a") as f:
            f.write(f"[PLECS] Erro ao ler arquivo de saída: {e} - PATH TENTATIVO: {str(ROOT_DIR / 'dadosnovos.csv')}\n")
        return None


from typing import Any
def _to_native_types(data: Any) -> Any:
    """Converte tipos NumPy para tipos Python nativos (compatibilidade XMLRPC)."""
    if isinstance(data, dict):
        return {k: _to_native_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_to_native_types(v) for v in data]
    elif isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return _to_native_types(data.tolist())
    return data


def _montar_model_vars_bateria(cfg_bat: BateriaConfig, soc_inicial: float, soh_atual: float) -> dict:
    """Constrói o dicionário ModelVars para o PLECS."""
    model_vars = {
        'SOC_0':     soc_inicial,
        'SOH_Input': soh_atual,
        'Rs':        cfg_bat.Rs,
        'Ah':        cfg_bat.Ah,
        'Ns':        cfg_bat.Ns,
        'Np':        cfg_bat.Np,
        'SOC':       cfg_bat.soc_prof,
        'OCV':       cfg_bat.ocv_prof,
        'SocMin':    cfg_bat.soc_min,
        'SocMax':    cfg_bat.soc_max,
        'Vbmin':     cfg_bat.v_min_celula * cfg_bat.Ns,
        'Vbmax':     cfg_bat.v_max_celula * cfg_bat.Ns,
        'P_BESS':    cfg_bat.P_bess,
        'ETA':       cfg_bat.rendimento_pcs,
        'Escala_Tempo': 1,
    }
    return _to_native_types(model_vars)
