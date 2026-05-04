
import math
import pandas as pd
import numpy as np
import rainflow

from besx.config import DegradacaoCicloConfig, DegradacaoCalendarioConfig, CONFIGURACAO, ModeloDegradacaoConfig
from besx.infrastructure.logging.logger import logger
from pydantic import BaseModel
from typing import List, Any

class EstatisticasOperacionais(BaseModel):
    """Modelo Pydantic estruturando as estatísticas operacionais de um mês."""
    Ciclos_Contagem: int
    EFC_Ciclos_Equivalentes: float
    DOD_Medio_Perc: float
    C_Rate_Max: float
    C_Rate_Medio: float
    SOC_Medio: float
    SOC_Medio_Idle: float
    Tempo_SOC_Alto_Perc: float
    Tempo_SOC_Baixo_Perc: float
    Energia_Carga_kWh: float
    Energia_Descarga_kWh: float
    Rainflow_Cycles: List[Any]

def calcular_dano_referencia_serrao(model_params: ModeloDegradacaoConfig) -> float:
    """
    Calcula o dano nominal de referência conforme Serrão et al.
    Referência: T = 25°C, SOC = 50%, DOD = 10%.
    Considerando 30 ciclos de 10% DOD por mês.
    """
    T_REF_K = 25 + 273.15
    SOC_REF = 0.5
    DOD_REF = 0.1
    N_CICLOS_MES = 30
    
    c_params = model_params.ciclo
    cf_soc = c_params.a * np.exp(c_params.b * SOC_REF * 100.0)
    cf_temp = c_params.c * np.exp(c_params.d * T_REF_K)
    cf_depth = c_params.g * ((DOD_REF * 100.0)**c_params.h)
    
    dano_unit_cyc = cf_depth * cf_soc * cf_temp
    dano_cyc_mes = np.sqrt(N_CICLOS_MES * (dano_unit_cyc**2))
    
    cal_params = model_params.calendario
    ccal_temp = cal_params.k_T * np.exp(cal_params.exp_T * T_REF_K)
    ccal_soc = cal_params.k_soc * np.exp(cal_params.exp_soc * SOC_REF * 100.0)
    exp_cal = cal_params.exp_cal
    
    dano_cal_mes = ccal_temp * ccal_soc * (1.0**exp_cal)
    
    return float(dano_cyc_mes + dano_cal_mes)

def calcular_fator_severidade(dano_total_mes: float, model_params: ModeloDegradacaoConfig) -> float:
    """Calcula o Fator de Severidade (Is) comparando o dano real com o nominal."""
    d_nom = calcular_dano_referencia_serrao(model_params)
    return float(dano_total_mes / d_nom) if d_nom > 0 else 0.0

def calcular_rul(
    soh_atual_perc: float, 
    dano_ciclo_medio: float,
    dano_cal_medio: float,
    acum_ciclo_atual: float,
    acum_cal_atual: float,
    exp_cal: float,
    dias_por_ano_avg: float
) -> float:
    """Projeta o Remaining Useful Life (RUL) de forma não-linear usando busca binária."""
    if soh_atual_perc <= 80.0:
        return 0.0

    if dano_ciclo_medio <= 0 and dano_cal_medio <= 0:
        return 50.0

    target_loss = 20.0 # Bateria morre em 80% SOH (perda de 20%)
    
    def projetar_perda(meses_futuros: float) -> float:
        fut_ciclo = np.sqrt(acum_ciclo_atual**2 + meses_futuros * (dano_ciclo_medio**2))
        fut_cal = (acum_cal_atual**exp_cal + meses_futuros * (dano_cal_medio**exp_cal))**(1/exp_cal)
        return float(fut_ciclo + fut_cal)

    low = 0.0
    high = 600.0
    
    if projetar_perda(high) < target_loss:
        return 50.0
        
    for _ in range(15):
        mid = (low + high) / 2
        if projetar_perda(mid) < target_loss:
            low = mid
        else:
            high = mid
            
    rul_meses = (low + high) / 2
    return float(rul_meses / 12.0)


def dano_ciclo(lista_ciclos: Any, Temp_kelvin: float, model_params: DegradacaoCicloConfig, perfil_simp: np.ndarray = None) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano cíclico de forma vetorizada (Otimizado).
    """
    if perfil_simp is None:
        from besx.domain.models.battery_simulator import picos_e_vales
        prominence = model_params.peak_prominence
        soc_series = pd.Series(lista_ciclos)
        perfil_simp = picos_e_vales(soc_series, prominence=prominence)

    rainflow_mes = rainflow.extract_cycles(perfil_simp)
    df_rainflow = pd.DataFrame(rainflow_mes, columns=["Range", "Mean", "Count", "Start", "End"])

    if df_rainflow.empty:
        return 0.0, df_rainflow

    # Vetorização
    dods = df_rainflow['Range'].values
    socs = df_rainflow['Mean'].values
    counts = df_rainflow['Count'].values

    cf_soc = model_params.a * np.exp(model_params.b * socs * 100.0)
    cf_temp = model_params.c * np.exp(model_params.d * Temp_kelvin)
    cf_depth = model_params.g * ((dods * 100.0)**model_params.h)
    
    dano_unitario = cf_depth * cf_soc * cf_temp
    
    # Dano por ciclo ponderado pelo 'Count' (meios ciclos vs ciclos completos)
    # Regra de Palmgren-Miner modificada para acúmulo quadrático
    dano_contribuicao = (dano_unitario**2) * counts
    Ccyc_total_mes = np.sqrt(np.sum(dano_contribuicao))

    # Log para auditoria (mesmo formato da anterior)
    df_rainflow['range_rounded'] = df_rainflow['Range'].round(model_params.range_round_dp)
    df_rainflow['mean_rounded'] = df_rainflow['Mean'].round(model_params.mean_round_dp)
    df_rainflow['CFade_soc'] = cf_soc
    df_rainflow['CFade_temp'] = cf_temp
    df_rainflow['CFade_depth'] = cf_depth
    df_rainflow['dano_unitario'] = dano_unitario
    
    return float(Ccyc_total_mes), df_rainflow

def dano_calendar(lista_periodos_idle: list, Tbat_kelvin: float, model_params: DegradacaoCalendarioConfig, dt_minutos: float, dias_por_ano_avg: int) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano de calendário de forma vetorizada (Otimizado).
    """
    if not lista_periodos_idle:
        return 0.0, pd.DataFrame()

    socs = np.array([p['SOC'] for p in lista_periodos_idle])
    t_meses = np.array([p['t_meses'] for p in lista_periodos_idle])
    exp_tempo = model_params.exp_cal

    ccal_temp = model_params.k_T * np.exp(model_params.exp_T * Tbat_kelvin)
    ccal_soc = model_params.k_soc * np.exp(model_params.exp_soc * socs * 100.0)
    ccal_time = t_meses**exp_tempo

    dano_periodos = ccal_temp * ccal_soc * ccal_time
    # Acúmulo de Potência (L-n norm)
    Ccal_total_mes = (np.sum(dano_periodos**exp_tempo))**(1/exp_tempo)

    df_calculos_calendario = pd.DataFrame({
        'SOC': socs,
        't_meses': t_meses,
        'CCal_temperature': ccal_temp,
        'Ccal_soc': ccal_soc,
        'Ccal_time': ccal_time,
        'dano_periodo': dano_periodos
    })

    return float(Ccal_total_mes), df_calculos_calendario

def _processar_balanco_energetico(p_ca_kw: np.ndarray, dt_h: float) -> tuple[float, float]:
    """Integra as potências de carga e descarga para obter o balanço em kWh."""
    # Vetorizado
    carga_mask = p_ca_kw > 0
    descarga_mask = p_ca_kw < 0
    energia_carga_kwh = np.sum(p_ca_kw[carga_mask]) * dt_h
    energia_descarga_kwh = np.abs(np.sum(p_ca_kw[descarga_mask])) * dt_h
    return float(energia_carga_kwh), float(energia_descarga_kwh)

def _analisar_c_rates(p_ca_kw: np.ndarray, cap_kwh: float) -> tuple[float, float]:
    """Calcula as taxas de C-Rate máxima e média do período."""
    c_rates = np.abs(p_ca_kw) / cap_kwh
    return float(c_rates.max()), float(c_rates.mean())

def _extrair_ciclos_rainflow(soc_series: Any, perfil_simp: np.ndarray = None) -> tuple[list, float, float]:
    """Extração Rainflow otimizada."""
    if perfil_simp is None:
        from besx.domain.models.battery_simulator import picos_e_vales
        prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
        soc_array = soc_series.to_numpy() if isinstance(soc_series, pd.Series) else soc_series
        perfil_simp = picos_e_vales(pd.Series(soc_array), prominence=prominence)
    
    ciclos_rf = list(rainflow.extract_cycles(perfil_simp))
    
    if not ciclos_rf:
        return [], 0.0, 0.0
        
    dods = np.array([x[0] for x in ciclos_rf])
    counts = np.array([x[2] for x in ciclos_rf])
    
    avg_dod = np.mean(dods)
    efc = np.sum(dods * counts)
    
    return ciclos_rf, float(efc), float(avg_dod)

def _analisar_distribuicao_soc(soc_array: np.ndarray) -> tuple[float, float, float]:
    """Analisa a média e o tempo gasto em extremos de SOC (Vetorizado)."""
    media_soc = np.mean(soc_array)
    total_amostras = len(soc_array)
    
    lim_alto = CONFIGURACAO.simulacao.SOC_ALTO_LIMITE
    lim_baixo = CONFIGURACAO.simulacao.SOC_BAIXO_LIMITE
    
    pct_alto = (np.sum(soc_array > lim_alto) / total_amostras) * 100
    pct_baixo = (np.sum(soc_array < lim_baixo) / total_amostras) * 100
    
    return float(media_soc), float(pct_alto), float(pct_baixo)

def _calcular_soc_idle(soc_array: np.ndarray, p_ca_kw: np.ndarray, lista_periodos_idle: list = None) -> float:
    """Calcula o SOC médio ponderado durante os períodos de repouso."""
    if lista_periodos_idle:
        t_total_idle = sum(p['t'] for p in lista_periodos_idle)
        if t_total_idle > 0:
            return sum(p['SOC'] * p['t'] for p in lista_periodos_idle) / t_total_idle
        return 0.0
    
    idle_mask = p_ca_kw == 0.0        
    if idle_mask.any():
        return float(np.mean(soc_array[idle_mask]))
    return 0.0

def calcular_estatisticas_operacionais(
    df_soc_saida: pd.DataFrame, 
    df_potencia_entrada: pd.DataFrame, 
    cap_kwh: float, 
    lista_periodos_idle: list = None,
    perfil_simp: np.ndarray = None
) -> EstatisticasOperacionais:
    """
    Analisa o comportamento operacional de forma otimizada.
    """
    soc_array = df_soc_saida['SOC'].values
    p_ca_kw = df_soc_saida['Potencia_CA_kW'].values
    tempos = df_soc_saida['Tempo'].values

    dt_h = (tempos[1] - tempos[0]) / 3600.0 if len(tempos) > 1 else (1.0 / 60.0)

    e_carga, e_descarga = _processar_balanco_energetico(p_ca_kw, dt_h)
    max_c, avg_c = _analisar_c_rates(p_ca_kw, cap_kwh)
    ciclos_rf, efc, avg_dod = _extrair_ciclos_rainflow(soc_array, perfil_simp)
    media_soc, pct_alto, pct_baixo = _analisar_distribuicao_soc(soc_array)
    soc_idle_avg = _calcular_soc_idle(soc_array, p_ca_kw, lista_periodos_idle)

    return EstatisticasOperacionais(
        Ciclos_Contagem=len(ciclos_rf),
        EFC_Ciclos_Equivalentes=round(efc, 2),
        DOD_Medio_Perc=round(avg_dod, 4),
        C_Rate_Max=round(max_c, 2), 
        C_Rate_Medio=round(avg_c, 3),
        SOC_Medio=round(media_soc, 4),
        SOC_Medio_Idle=round(soc_idle_avg, 4),
        Tempo_SOC_Alto_Perc=round(pct_alto, 1),
        Tempo_SOC_Baixo_Perc=round(pct_baixo, 1),
        Energia_Carga_kWh=round(e_carga, 2),
        Energia_Descarga_kWh=round(e_descarga, 2),
        Rainflow_Cycles=ciclos_rf 
    )