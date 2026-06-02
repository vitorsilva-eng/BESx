"""
battery_simulator.py  —  Simulador de SOC por Integração de Coulomb (Otimizado)

Substitui o PLECS na simulação mensal do comportamento da bateria.
Dado um perfil de potência mensal, calcula o perfil de SOC passo a passo.

Versão com Numba JIT para alta performance.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from numba import njit

from besx.config import BateriaConfig
from besx.infrastructure.logging.logger import logger

@njit
def _simular_coulomb_numba(
    pot_w_arr: np.ndarray,
    pot_var_arr: np.ndarray,
    tempos_min_arr: np.ndarray,
    soc_inicial: float,
    Ah: float,
    soh_atual: float,
    rs_banco: float,
    Ns: int,
    Np: int,
    n_unidades: int,
    v_max_banco: float,
    v_min_banco: float,
    soc_min_clip: float,
    soc_max_clip: float,
    p_bess: float,
    rendimento_pcs: float,
    soc_prof: np.ndarray,
    ocv_prof: np.ndarray,
    ocv_charge_prof: np.ndarray = None,
    ocv_discharge_prof: np.ndarray = None
):
    """Loop de integração de Coulomb compilado para performance extrema."""
    n_passos = len(pot_w_arr)
    soc_out = np.zeros(n_passos)
    corrente_out = np.zeros(n_passos)
    tensao_term_out = np.zeros(n_passos)
    pot_ca_out = np.zeros(n_passos)
    
    soc_out[0] = soc_inicial
    q_efetivo_celula = Ah * soh_atual
    p_bess_limite = p_bess * n_unidades

    for k in range(n_passos - 1):
        # Delta T em horas
        dt_h = (tempos_min_arr[k + 1] - tempos_min_arr[k]) / 60.0
        
        # Potência CA limitada pelo PCS
        p_ca_w = pot_w_arr[k]
        if p_ca_w > p_bess_limite:
            p_ca_w = p_bess_limite
        elif p_ca_w < -p_bess_limite:
            p_ca_w = -p_bess_limite
        
        # Seleção da Curva OCV (Histerese)
        curva_ocv_ativa = ocv_prof
        if p_ca_w > 0 and ocv_charge_prof is not None:
            curva_ocv_ativa = ocv_charge_prof
        elif p_ca_w < 0 and ocv_discharge_prof is not None:
            curva_ocv_ativa = ocv_discharge_prof
            
        # Interpolação OCV
        v_ocv_celula = np.interp(soc_out[k], soc_prof, curva_ocv_ativa)
        v_ocv_banco = v_ocv_celula * Ns
        
        # Potência CA Reativa (VAr)
        p_var_w = pot_var_arr[k]
        
        # Potência Aparente CA (VA)
        s_ca_va = np.sqrt(p_ca_w**2 + p_var_w**2)
        
        # Cálculo das Perdas do PCS baseadas na Potência Aparente (S)
        # Se rendimento_pcs = 0.98, perdas = S * 0.02
        perdas_pcs_w = s_ca_va * (1.0 - rendimento_pcs)
        
        # Potência DC na Bateria (Watts)
        # Convenção: P > 0 (Carga), P < 0 (Descarga)
        # As perdas sempre reduzem a potência que entra na bateria (carga) 
        # ou aumentam a potência que sai da bateria (descarga).
        p_bateria_w = p_ca_w - perdas_pcs_w
            
        # Cálculo da Corrente (Rint Model)
        if rs_banco > 0.0:
            delta = v_ocv_banco**2 + 4 * rs_banco * p_bateria_w 
            if delta < 0: 
                corrente_banco = -v_ocv_banco / (2 * rs_banco) 
            else:
                corrente_banco = (-v_ocv_banco + np.sqrt(delta)) / (2 * rs_banco)
        else:
            corrente_banco = p_bateria_w / v_ocv_banco
            
        # BMS Cut-off (Tensão)
        if rs_banco > 1e-7:
            v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)          
            if v_term_estimada > v_max_banco:
                corrente_banco = (v_max_banco - v_ocv_banco) / rs_banco
                v_term_estimada = v_max_banco
            elif v_term_estimada < v_min_banco:
                corrente_banco = (v_min_banco - v_ocv_banco) / rs_banco
                v_term_estimada = v_min_banco
        else:
            v_term_estimada = v_ocv_banco
            
        # Coulomb Counting
        corrente_celula = corrente_banco / (Np * n_unidades)
        delta_soc_req = (corrente_celula * dt_h / q_efetivo_celula) 
        
        # Clip de SOC
        soc_novo = soc_out[k] + delta_soc_req
        if soc_novo > soc_max_clip:
            soc_novo = soc_max_clip
        elif soc_novo < soc_min_clip:
            soc_novo = soc_min_clip
            
        delta_soc_real = soc_novo - soc_out[k]

        # Ajuste de corrente se bateu no limite de SOC
        if abs(delta_soc_real) < abs(delta_soc_req) and abs(delta_soc_req) > 1e-9:
            corrente_celula_real = delta_soc_real * q_efetivo_celula / dt_h
            corrente_banco = corrente_celula_real * (Np * n_unidades)
            if rs_banco > 1e-7:
                 v_term_estimada = v_ocv_banco + (corrente_banco * rs_banco)
            else:
                 v_term_estimada = v_ocv_banco

        corrente_out[k] = corrente_banco
        tensao_term_out[k] = v_term_estimada
        
        # Potência CA Real
        p_dc_real = v_term_estimada * corrente_banco
        if corrente_banco > 0:
            pot_ca_out[k] = p_dc_real / rendimento_pcs
        elif corrente_banco < 0:
            pot_ca_out[k] = p_dc_real * rendimento_pcs
        else:
            pot_ca_out[k] = 0.0

        soc_out[k + 1] = soc_novo
        
    # Finalização dos vetores
    corrente_out[-1] = corrente_out[-2]
    tensao_term_out[-1] = tensao_term_out[-2]
    pot_ca_out[-1] = pot_ca_out[-2]
    
    return soc_out, corrente_out, tensao_term_out, pot_ca_out

def simular_soc_mes(df_mes: pd.DataFrame, soh_atual: float, soc_inicial: float, cfg_bat, n_unidades: int = 1) -> pd.DataFrame:
    """Interface pública para simulação de SOC, delegando o loop para Numba."""
    cols = df_mes.columns.tolist()
    col_t = next((c for c in cols if 'tempo' in c.lower() or 'timestamp' in c.lower()), cols[0])
    col_p = next((c for c in cols if 'pot' in c.lower() and c != col_t), cols[1] if len(cols)>1 else cols[0])
    
    # Busca coluna de Reativos (VAr)
    col_q = next((c for c in cols if 'reativa' in c.lower() or 'var' in c.lower()), None)

    pot_raw_arr = df_mes[col_p].astype(float).values
    tempos_min_arr = df_mes[col_t].astype(float).values
    
    if col_q:
        pot_var_arr = df_mes[col_q].astype(float).values
        logger.info(f"[Simulator] Coluna reativa detectada: {col_q} | Max VAr: {np.max(np.abs(pot_var_arr)):.1f}")
    else:
        pot_var_arr = np.zeros_like(pot_raw_arr)
        logger.info("[Simulator] Nenhuma coluna reativa detectada. Usando zero VAr.")

    if 'kw' in col_p.lower():
        pot_w_arr = pot_raw_arr * 1000.0
    else:
        pot_w_arr = pot_raw_arr

    # Parâmetros físicos
    rs_banco = (cfg_bat.Rs * cfg_bat.Ns) / (cfg_bat.Np * n_unidades) if cfg_bat.Rs else 0.0
    v_max_banco = cfg_bat.v_max_celula * cfg_bat.Ns
    v_min_banco = cfg_bat.v_min_celula * cfg_bat.Ns
    
    # Conversão de listas/objetos para arrays NumPy (Requisito Numba)
    soc_prof_np = np.array(cfg_bat.soc_prof, dtype=np.float64)
    ocv_prof_np = np.array(cfg_bat.ocv_prof, dtype=np.float64)
    
    ocv_ch = getattr(cfg_bat, 'ocv_charge_prof', None)
    ocv_charge_np = np.array(ocv_ch, dtype=np.float64) if ocv_ch is not None else None
    
    ocv_dis = getattr(cfg_bat, 'ocv_discharge_prof', None)
    ocv_discharge_np = np.array(ocv_dis, dtype=np.float64) if ocv_dis is not None else None

    # Chamada do Motor Compilado
    soc_out, corrente_out, tensao_term_out, pot_ca_out = _simular_coulomb_numba(
        pot_w_arr, pot_var_arr, tempos_min_arr, soc_inicial, cfg_bat.Ah, soh_atual,
        rs_banco, cfg_bat.Ns, cfg_bat.Np, n_unidades,
        v_max_banco, v_min_banco, cfg_bat.soc_min, cfg_bat.soc_max,
        float(cfg_bat.P_bess), cfg_bat.rendimento_pcs,
        soc_prof_np, ocv_prof_np, ocv_charge_np, ocv_discharge_np
    )
        
    df_resultado = pd.DataFrame({
        'Tempo': tempos_min_arr * 60.0,
        'SOC': soc_out,
        'Corrente_A': corrente_out,
        'Tensao_Term_V': tensao_term_out,
        'Potencia_CA_kW': pot_ca_out / 1000.0
    })
    
    return df_resultado

def picos_e_vales(profile_series: pd.Series, prominence: float = 0.01) -> np.ndarray:
    """Extrai picos e vales de uma Série de SOC de forma eficiente."""
    profile_array = profile_series.to_numpy()
    if len(profile_array) < 3:
        return profile_array

    picos, _ = find_peaks(profile_array, prominence=prominence)
    vales, _ = find_peaks(-profile_array, prominence=prominence)

    indices_combinados = np.sort(np.unique(np.concatenate((
        [0],
        picos,
        vales,
        [len(profile_array) - 1]
    ))))

    return profile_array[indices_combinados]

def ciclos_idle(profile: np.ndarray, dt_minutos_soc: float, minutos_por_mes: float) -> list:
    """Encontra períodos 'idle' utilizando vetorização NumPy para detectar mudanças."""
    if len(profile) < 2:
        return []
    
    # Detecta onde o SOC muda entre passos consecutivos
    changes = np.diff(profile) != 0
    change_indices = np.where(changes)[0] + 1
    
    # Define os limites de cada segmento constante
    start_indices = np.concatenate(([0], change_indices))
    end_indices = np.concatenate((change_indices, [len(profile)]))
    
    idle_cycles = []
    for start, end in zip(start_indices, end_indices):
        duration = end - start
        if duration > 1:
            soc_val = profile[start]
            tempo_total_minutos = duration * dt_minutos_soc
            idle_cycles.append({
                't': int(duration),
                't_meses': float(tempo_total_minutos / minutos_por_mes),
                'SOC': float(soc_val),
                'index': int(start)
            })
            
    return idle_cycles
