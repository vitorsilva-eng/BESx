"""
battery_simulator.py  —  Simulador de SOC por Integração de Coulomb

Substitui o PLECS na simulação mensal do comportamento da bateria.
Dado um perfil de potência mensal, calcula o perfil de SOC passo a passo.

Método: Integração de Coulomb
  SOC(t+dt) = SOC(t) + I(t) * dt / Q_efetivo
  I(t) = P(t) / V_ocv(SOC(t))

Saída compatível com o CSV que o PLECS produzia:
  DataFrame com colunas ['Tempo', 'SOC']
    - Tempo em segundos
    - SOC em % (0–100)
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from besx.config import BateriaConfig
from besx.infrastructure.logging.logger import logger

def _interpolar_ocv(soc_frac: float, soc_prof: list, ocv_prof: list) -> float:
    """
    Interpola a tensão OCV do banco para um dado SOC (fração 0-1).

    Args:
        soc_frac: SOC atual em fração (0–1)
        soc_prof: Lista de pontos de SOC da curva OCV (0–1)
        ocv_prof: Lista de tensões OCV correspondentes (V)

    Returns:
        Tensão OCV interpolada em Volts
    """
    return float(np.interp(soc_frac, soc_prof, ocv_prof))

def simular_soc_mes(df_mes: pd.DataFrame, soh_atual: float, soc_inicial: float, cfg_bat) -> pd.DataFrame:
    """
    Simula o perfil de SOC e Tensão de um mês usando integração de Coulomb e Modelo Rint.
    
    df_mes: DataFrame contendo ['timestamp_min', 'pot_w'] (Potência CA solicitada)
    cfg_bat: Objeto/dataclass com (Ns, Np, Ah, Rs, rendimento_pcs, soc_min_pct, soc_max_pct, v_max_celula, v_min_celula, soc_prof, ocv_prof)
    """
    # Identificador dinâmico de colunas para suportar diferentes fontes de dados (CSV, MAT)
    cols = df_mes.columns.tolist()
    col_t = next((c for c in cols if 'tempo' in c.lower() or 'timestamp' in c.lower()), cols[0])
    col_p = next((c for c in cols if 'pot' in c.lower() and c != col_t), cols[1] if len(cols)>1 else cols[0])

    # 1. Extração para arrays NumPy (Acelera o loop for em mais de 50x)
    pot_w_arr = df_mes[col_p].astype(float).values
    tempos_min_arr = df_mes[col_t].astype(float).values
    n_passos = len(pot_w_arr)
    
    # 2. Inicialização dos vetores de saída
    soc_out = np.zeros(n_passos)
    corrente_out = np.zeros(n_passos)
    tensao_term_out = np.zeros(n_passos)
    pot_ca_out = np.zeros(n_passos)
    
    soc_out[0] = soc_inicial
    
    # Parâmetros do Banco
    q_efetivo_celula = cfg_bat.Ah * soh_atual
    rs_banco = (cfg_bat.Rs * cfg_bat.Ns) / cfg_bat.Np if cfg_bat.Rs else 0.0
    v_max_banco = cfg_bat.v_max_celula * cfg_bat.Ns
    v_min_banco = cfg_bat.v_min_celula * cfg_bat.Ns
    
    soc_min_clip = cfg_bat.soc_min 
    soc_max_clip = cfg_bat.soc_max
    
    logger.info(f"[BatterySim] Config: Rs_cel={cfg_bat.Rs}, Rend={cfg_bat.rendimento_pcs}, SOH={soh_atual:.2f}, SOC=[{soc_min_clip*100:.1f}-{soc_max_clip*100:.1f}]%")
    
    for k in range(n_passos - 1):
        # Delta T em horas
        dt_h = (tempos_min_arr[k + 1] - tempos_min_arr[k]) / 60.0
        
        # Interpolação da Tensão OCV atual
        v_ocv_celula = _interpolar_ocv(soc_out[k], cfg_bat.soc_prof, cfg_bat.ocv_prof)
        v_ocv_banco = v_ocv_celula * cfg_bat.Ns
        
        # Potência CA limitida pelo PCS
        p_bess_limite = float(cfg_bat.P_bess) if cfg_bat.P_bess else float('inf')
        p_ca_w = np.clip(pot_w_arr[k], -p_bess_limite, p_bess_limite)
        
        # Potência DC na Bateria (P > 0: Carga | P < 0: Descarga)
        if p_ca_w > 0:
            p_bateria_w = p_ca_w * cfg_bat.rendimento_pcs
        elif p_ca_w < 0:
            p_bateria_w = p_ca_w / cfg_bat.rendimento_pcs
        else:
            p_bateria_w = 0.0
            
        # Cálculo da Corrente
        # rs_banco^2 * I^2 + V_ocv * I - P_bateria = 0
        if rs_banco > 0.0:
            # O Valor é positivo pois na equação p_bateria_w é negativo
            delta = v_ocv_banco**2 + 4 * rs_banco * p_bateria_w 
            if delta < 0: 
                # Delta negativo, então a potência solicitada seria maior que a máxima que a bateria pode fornecer
                # Para evitar um erro de raiz negativa, usamos a fórmula de Bhaskara com delta = 0, achando o maior valor
                corrente_banco = -v_ocv_banco / (2 * rs_banco) 
            else:
                corrente_banco = (-v_ocv_banco + np.sqrt(delta)) / (2 * rs_banco)
        else: #rs_banco == 0 ou negativa, vira equação simples de 1 grau
            corrente_banco = p_bateria_w / v_ocv_banco
            
        # --- NOVO: LIMITAÇÃO FÍSICA DE TENSÃO (BMS Cut-off) ---
        # V_term = V_ocv + I * R_s
        if rs_banco > 1e-7:
            v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)
            
            if v_term_estimada > v_max_banco:
                # Força a corrente para o máximo que a tensão limite permite
                corrente_banco = (v_max_banco - v_ocv_banco) / rs_banco
                v_term_estimada = v_max_banco
            elif v_term_estimada < v_min_banco:
                corrente_banco = (v_min_banco - v_ocv_banco) / rs_banco
                v_term_estimada = v_min_banco
        else:
            v_term_estimada = v_ocv_banco
            
        # Coulomb Counting Inicial (na célula)
        corrente_celula = corrente_banco / cfg_bat.Np
        delta_soc_req = (corrente_celula * dt_h / q_efetivo_celula)  # [0-1]
        
        # Atualiza e clipa o SOC
        soc_novo = np.clip(soc_out[k] + delta_soc_req, soc_min_clip, soc_max_clip)
        delta_soc_real = soc_novo - soc_out[k]

        # Se o SOC bateu no limite (bateria cheia ou vazia), a corrente real foi menor
        if abs(delta_soc_real) < abs(delta_soc_req) and abs(delta_soc_req) > 1e-9:
            corrente_celula_real = delta_soc_real * q_efetivo_celula / dt_h
            corrente_banco = corrente_celula_real * cfg_bat.Np
            
            # Recalcula a tensão terminal real com a corrente reduzida
            if rs_banco > 1e-7:
                 v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)
            else:
                 v_term_estimada = v_ocv_banco

        # Registra valores reais finais
        corrente_out[k] = corrente_banco
        tensao_term_out[k] = v_term_estimada
        
        # Potência CA Real Aplicada (após limitações de Tensão/BMS e SOC_max)
        # P_ca = P_dc / rendimento (se I > 0 / Carga) ou P_ca = P_dc * rendimento (se I < 0 / Descarga)
        p_dc_real = v_term_estimada * corrente_banco
        if corrente_banco > 0:
            pot_ca_out[k] = p_dc_real / cfg_bat.rendimento_pcs
        elif corrente_banco < 0:
            pot_ca_out[k] = p_dc_real * cfg_bat.rendimento_pcs
        else:
            pot_ca_out[k] = 0.0

        soc_out[k + 1] = soc_novo
        
    # Salva o último passo de corrente/tensão (mantém o valor anterior para não zerar)
    corrente_out[-1] = corrente_out[-2]
    tensao_term_out[-1] = tensao_term_out[-2]
    pot_ca_out[-1] = pot_ca_out[-2]
        
    # 3. Reconstrói o DataFrame de Saída para a Análise de Degradação
    df_resultado = pd.DataFrame({
        'Tempo': tempos_min_arr * 60.0,
        'SOC': soc_out,
        'Corrente_A': corrente_out,
        'Tensao_Term_V': tensao_term_out,
        'Potencia_CA_kW': pot_ca_out / 1000.0
    })
    
    return df_resultado

def old_simular_soc_mes(
    df_mes: pd.DataFrame,
    soh_atual: float,
    soc_inicial: float,
    cfg_bat: BateriaConfig,
) -> pd.DataFrame:
    """
    Simula o perfil de SOC de um mês usando integração de Coulomb.

    Reproduz o comportamento do modelo de bateria do PLECS:
    - Limita a potência a ±P_bess
    - Limita o SOC ao intervalo [SOCmin, SOCmax]
    - Usa a curva OCV×SOC para estimar a tensão instantânea
    - Aplica carga limitada quando os limites de SOC são atingidos

    Args:
        df_mes (pd.DataFrame):
            Perfil de potência do mês.
            Colunas esperadas: [Tempo (min), Potencia_kW]
        soh_atual (float):
            State of Health atual — fração 0–1. Escala a capacidade.
        soc_inicial (float):
            SOC inicial do mês — fração 0–1.
        cfg_bat (BateriaConfig):
            Configuração da bateria (atributo CONFIGURACAO.bateria).
            Campos usados:
              - 'Ah'      : Capacidade nominal do módulo (Ah)
              - 'Ns'      : Número de módulos em série
              - 'Np'      : Número de strings em paralelo
              - 'soc_prof': Lista SOC fracionário para curva OCV
              - 'ocv_prof': Lista de tensões OCV (V)
              - 'soc_min' : SOC mínimo (fração 0–1)
              - 'soc_max' : SOC máximo (fração 0–1)
              - 'P_bess'  : Potência máxima do BESS (W)

    Returns:
        pd.DataFrame:
            DataFrame com colunas ['Tempo', 'SOC']:
              - 'Tempo': tempo em segundos (float)
              - 'SOC'  : SOC em % (float, 0–100)
            Estrutura idêntica ao CSV gerado pelo PLECS.
    """
    # ------------------------------------------------------------------ #
    #  1.  Leitura de parâmetros                                           #
    # ------------------------------------------------------------------ #
    Ah       = float(cfg_bat.Ah)
    Ns       = int(cfg_bat.Ns)
    Np       = int(cfg_bat.Np)
    soc_prof = cfg_bat.soc_prof
    ocv_prof = cfg_bat.ocv_prof
    soc_min  = float(cfg_bat.soc_min)
    soc_max  = float(cfg_bat.soc_max)
    p_bess   = float(cfg_bat.P_bess)
    rendimento_pcs = float(getattr(cfg_bat, 'rendimento_pcs', 0.88))

    Q_efetivo_Ah = Ah * Np * soh_atual #provocando o dano do SOH
    soc_frac = float(soc_inicial)

    col_tempo    = df_mes.columns[0]
    col_potencia = df_mes.columns[1]

    tempos_min = df_mes[col_tempo].to_numpy(dtype=float)
    pot_w      = df_mes[col_potencia].to_numpy(dtype=float)

    n_passos = len(tempos_min)

    # ------------------------------------------------------------------ #
    #  3.  Pré-alocação dos arrays de saída                               #
    # ------------------------------------------------------------------ #
    tempos_s = tempos_min * 60.0          # minutos → segundos
    soc_out  = np.empty(n_passos, dtype=float)
    soc_out[0] = soc_pct

    # ------------------------------------------------------------------ #
    #  4.  Integração de Coulomb passo a passo                            #
    # ------------------------------------------------------------------ #
    soc_min_frac = soc_min
    soc_max_frac = soc_max

    for k in range(n_passos - 1):
        # Intervalo de tempo em horas
        dt_h = (tempos_min[k + 1] - tempos_min[k]) / 60.0

        # Tensão OCV atual (V) por célula
        v_ocv_celula = _interpolar_ocv(soc_out[k], soc_prof, ocv_prof)
        if v_ocv_celula <= 0.0:
            v_ocv_celula = ocv_prof[0] if ocv_prof[0] > 0 else 1.0
            
        # Tensão real do banco
        v_ocv_banco = v_ocv_celula * Ns

        # 1. Potência solicitada pelo lado CA (W) — limitada à potência máxima do BESS
        p_ca_w = np.clip(pot_w[k], -p_bess, p_bess)
        
        # 2. Potência efetiva na Bateria DC (Aplicando o Rendimento)
        #  Convenção de sinal:
        #    P > 0  →  carga (lado CA injeta energia no BESS). Bateria recebe menos energia.
        #    P < 0  →  descarga (BESS injeta na rede). Bateria precisa entregar mais energia.
        if p_ca_w > 0:
            p_bateria_w = p_ca_w * rendimento_pcs
        elif p_ca_w < 0:
            p_bateria_w = p_ca_w / rendimento_pcs
        else:
            p_bateria_w = 0.0
            
        # 3. Resistência do Banco
        # Rs fornecido no config é por célula.
        # R_banco = Rs_celula * Ns / Np
        if cfg_bat.Rs is not None:
            rs_banco = float(cfg_bat.Rs) * Ns / Np
        else:
            rs_banco = 0.0

        # 4. Corrente do banco (Resolvendo a Malha do PLECS)
        # O PLECS divide a Potência pela Tensão NOS TERMINAIS do bloco da Bateria.
        # A Tensão nos terminais é: V_term = V_ocv_banco + I_banco * rs_banco
        # E sabemos que: P_bateria_w = V_term * I_banco 
        # Substituindo: P_bateria_w = (V_ocv_banco + I_banco * rs_banco) * I_banco 
        #               P_bateria_w = I_banco^2 * rs_banco + V_ocv_banco * I_banco
        #               0           = rs_banco * I_banco^2 + V_ocv_banco * I_banco - P_bateria_w
        if rs_banco > 0.0:
            delta = v_ocv_banco**2 + 4 * rs_banco * p_bateria_w # + por que a corrente é negativa quando a bateria está descarregando
            if delta < 0:
                # Caso limite teórico excedido (ex: forçando potência excessiva numa bateria morta)
                corrente_banco = -v_ocv_banco / (2 * rs_banco)
            else:
                corrente_banco = (-v_ocv_banco + np.sqrt(delta)) / (2 * rs_banco)
        else:
            # Caso ideal (sem resistência interna)
            corrente_banco = p_bateria_w / v_ocv_banco
        
        # 4. Corrente que flui por uma célula / string individual (dividindo pelos paralelos)
        corrente_celula = corrente_banco / Np
            
        # 5. Variação de SOC (Integradora):
        #    Cálculo na Célula: ΔSOC = (I_cel / (Ah_celula * SOH)) * dt_h * 100 %
        #    Q_efetivo da célula individual = Ah * soh_atual
        q_efetivo_celula = Ah * soh_atual
        
        delta_soc  = (corrente_celula * dt_h / q_efetivo_celula)  # [0-1]

        soc_novo = soc_out[k] + delta_soc

        # Clamp físico e operacional
        soc_novo = float(np.clip(soc_novo, soc_min_frac, soc_max_frac))
        soc_out[k + 1] = soc_novo

    # ------------------------------------------------------------------ #
    #  5.  Monta DataFrame de saída (idêntico ao CSV do PLECS)            #
    # ------------------------------------------------------------------ #
    df_resultado = pd.DataFrame({
        'Tempo': tempos_s,
        'SOC':   soc_out,
    })

    logger.info(
        f"   [BattSim] SOC inicial={soc_out[0]*100:.1f}% | "
        f"SOC final={soc_out[-1]*100:.1f}% | "
        f"min={soc_out.min()*100:.1f}% | max={soc_out.max()*100:.1f}%"
    )

    return df_resultado

def picos_e_vales(profile_series: pd.Series, prominence: float = 1.0) -> np.ndarray:
    """
    Extrai picos e vales de uma Série de SOC.
    """
    profile_array = profile_series.to_numpy()

    picos, _ = find_peaks(profile_array, prominence=prominence)
    vales, _ = find_peaks(-profile_array, prominence=prominence)

    # Usa os ÍNDICES da Série original
    indices_combinados = np.concatenate((
        [profile_series.index[0]],
        profile_series.index[picos],
        profile_series.index[vales],
        [profile_series.index[-1]]
    ))
    indices_ordenados = np.sort(np.unique(indices_combinados))

    soc_profile_simp = profile_series.loc[indices_ordenados].to_numpy()
    return soc_profile_simp

def ciclos_idle(profile: list, dt_minutos_soc: float, minutos_por_mes: float) -> list:
    """
    Encontra períodos 'idle' (SOC constante) em um perfil de SOC.
    """
    cont = 0
    idle_cycles = []
    
    for i in range(len(profile)-1):
        if profile[i] == profile[i+1]:
            cont += 1
        else:
            if cont > 0:
                num_amostras_idle = cont + 1
                tempo_total_minutos = num_amostras_idle * dt_minutos_soc
                
                data = {
                    't': num_amostras_idle,
                    't_meses': tempo_total_minutos / minutos_por_mes,
                    'SOC': profile[i],
                    'index': i
                }
                idle_cycles.append(data)
            cont = 0
    
    if cont > 0:
        num_amostras_idle = cont + 1
        tempo_total_minutos = num_amostras_idle * dt_minutos_soc
        data = {
            't': num_amostras_idle,
            't_meses': tempo_total_minutos / minutos_por_mes,
            'SOC': profile[len(profile)-1],
            'index': len(profile)-1
        }
        idle_cycles.append(data)
            
    return idle_cycles
