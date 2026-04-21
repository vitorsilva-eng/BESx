
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
    # PARÂMETROS DE REFERÊNCIA
    T_REF_K = 25 + 273.15
    SOC_REF = 0.5
    DOD_REF = 0.1
    N_CICLOS_MES = 30
    
    # 1. Dano Cíclico Nominal
    c_params = model_params.ciclo
    cf_soc = c_params.a * np.exp(c_params.b * SOC_REF * 100.0)
    cf_temp = c_params.c * np.exp(c_params.d * T_REF_K)
    cf_depth = c_params.g * ((DOD_REF * 100.0)**c_params.h)
    
    dano_unit_cyc = cf_depth * cf_soc * cf_temp
    # Acúmulo quadrático de 30 ciclos idênticos
    dano_cyc_mes = np.sqrt(N_CICLOS_MES * (dano_unit_cyc**2))
    
    # 2. Dano Calendário Nominal
    cal_params = model_params.calendario
    ccal_temp = cal_params.k_T * np.exp(cal_params.exp_T * T_REF_K)
    ccal_soc = cal_params.k_soc * np.exp(cal_params.exp_soc * SOC_REF * 100.0)
    exp_cal = cal_params.exp_cal
    
    # Dano de 1 mês (t=1)
    dano_cal_mes = ccal_temp * ccal_soc * (1.0**exp_cal)
    
    # Dano Total de Referência (mês)
    return float(dano_cyc_mes + dano_cal_mes)

def calcular_fator_severidade(dano_total_mes: float, model_params: ModeloDegradacaoConfig) -> float:
    """
    Calcula o Fator de Severidade (Is) comparando o dano real com o nominal.
    """
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
    """
    Projeta o Remaining Useful Life (RUL) de forma não-linear usando busca binária.
    
    A projeção assume que os meses futuros terão um 'stress' bruto igual à média 
    do histórico (dano_ciclo_medio e dano_cal_medio) e os acumula geometricamente.
    
    Args:
        soh_atual_perc (float): SOH atual (ex: 98.5).
        dano_ciclo_medio (float): Média aritmética dos danos brutos por ciclo.
        dano_cal_medio (float): Média aritmética dos danos brutos de calendário.
        acum_ciclo_atual (float): Total de dano cíclico acumulado (norma L2).
        acum_cal_atual (float): Total de dano calendário acumulado (norma Ln).
        exp_cal (float): Expoente n da regra de potência do calendário.
        dias_por_ano_avg (float): Constante de dias por ano para conversão de tempo.
        
    Returns:
        float: RUL em anos. Retorna 50.0 se o limite não for atingido em 50 anos.
    """
    if soh_atual_perc <= 80.0:
        return 0.0

    # Se não há dano algum detectado, evitamos cálculos
    if dano_ciclo_medio <= 0 and dano_cal_medio <= 0:
        return 50.0

    target_loss = 20.0 # Bateria morre em 80% SOH (perda de 20%)
    
    def projetar_perda(meses_futuros: float) -> float:
        """Calcula a perda total após N meses no futuro baseado no estado atual."""
        # Acúmulo Quadrático (Ciclo)
        fut_ciclo = np.sqrt(acum_ciclo_atual**2 + meses_futuros * (dano_ciclo_medio**2))
        # Acúmulo de Potência (Calendário)
        fut_cal = (acum_cal_atual**exp_cal + meses_futuros * (dano_cal_medio**exp_cal))**(1/exp_cal)
        return float(fut_ciclo + fut_cal)

    # Busca Binária para encontrar o mês do EOL (End of Life)
    # Procuramos entre 0 e 600 meses (50 anos)
    low = 0.0
    high = 600.0
    
    # Se em 50 anos ainda não atingiu o limite, retornamos o teto
    if projetar_perda(high) < target_loss:
        return 50.0
        
    # Iterações de busca binária (15 passos garantem precisão de ~0.02 meses)
    for _ in range(15):
        mid = (low + high) / 2
        if projetar_perda(mid) < target_loss:
            low = mid
        else:
            high = mid
            
    rul_meses = (low + high) / 2
    return float(rul_meses / 12.0)


def dano_ciclo(lista_ciclos: list, Temp_kelvin: float, model_params: DegradacaoCicloConfig) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano total de cada ciclo do mês e acumula de forma quadrática.
    
    Args:
        lista_ciclos (list): Lista de valores de SOC (perfil).
        Temp_kelvin (float): Temperatura da bateria.
        model_params (DegradacaoCicloConfig): Parâmetros do modelo de ciclo.
    """
    from besx.domain.models.battery_simulator import picos_e_vales
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    # Garante redução da série para otimização do Rainflow
    soc_series = pd.Series(lista_ciclos)
    lista_ciclos_simp = picos_e_vales(soc_series, prominence=prominence)

    rainflow_mes = rainflow.extract_cycles(lista_ciclos_simp)

    df_rainflow = pd.DataFrame(rainflow_mes,
                               columns = ["Range", "Mean", "Count", "Start", "End"])

    range_dp = model_params.range_round_dp
    mean_dp = model_params.mean_round_dp

    df_rainflow['Range'] = pd.to_numeric(df_rainflow['Range'], errors='coerce')
    df_rainflow['range_rounded'] = df_rainflow['Range'].round(range_dp)

    df_rainflow['Mean'] = pd.to_numeric(df_rainflow['Mean'], errors='coerce')
    df_rainflow['mean_rounded'] = df_rainflow['Mean'].round(mean_dp)

    Ccyc_total_mes = 0.0

    a = model_params.a
    b = model_params.b
    c = model_params.c
    d = model_params.d
    g = model_params.g
    h = model_params.h

    # Listas para armazenar cálculos intermediários
    lista_CFade_soc = []
    lista_CFade_temp = []
    lista_CFade_depth = []
    lista_dano_unitario = []
    lista_dano_acum_parcial = []

    # 2. Itera sobre a Lista
    for _, info_grupo in df_rainflow.iterrows():
        dod = info_grupo['range_rounded']
        soc = info_grupo['mean_rounded']

        # 3. Calcula o dano unitário
        CFade_soc = a * np.exp(b * soc * 100.0)
        CFade_temp = c * np.exp(d * Temp_kelvin)
        CFade_depth = g * ((dod * 100.0)**h)
        dano = CFade_depth * CFade_soc * CFade_temp

        # 4. Acumula quadraticamente
        Ccyc_total_mes = np.sqrt(Ccyc_total_mes**2 + dano**2)
        
        # Armazena os cálculos intermediários
        lista_CFade_soc.append(CFade_soc)
        lista_CFade_temp.append(CFade_temp)
        lista_CFade_depth.append(CFade_depth)
        lista_dano_unitario.append(dano)
        lista_dano_acum_parcial.append(Ccyc_total_mes)

    # Adiciona as colunas de cálculos intermediários ao DataFrame
    df_rainflow['a'] = a
    df_rainflow['b'] = b
    df_rainflow['CFade_soc'] = lista_CFade_soc
    df_rainflow['c'] = c
    df_rainflow['d'] = d
    df_rainflow['Temp_kelvin'] = Temp_kelvin
    df_rainflow['CFade_temp'] = lista_CFade_temp
    df_rainflow['g'] = g
    df_rainflow['h'] = h
    df_rainflow['CFade_depth'] = lista_CFade_depth
    df_rainflow['dano_unitario'] = lista_dano_unitario
    df_rainflow['dano_acumulado_parcial'] = lista_dano_acum_parcial

    return float(Ccyc_total_mes), df_rainflow

def dano_calendar(lista_periodos_idle: list, Tbat_kelvin: float, model_params: DegradacaoCalendarioConfig, dt_minutos: float, dias_por_ano_avg: int) -> tuple[float, pd.DataFrame]:
    """
    Calcula o dano total por calendário (%) para o mês.

    Args:
        lista_periodos_idle (list): Lista de períodos idle.
        Tbat_kelvin (float): Temperatura da bateria.
        model_params (DegradacaoCalendarioConfig): Parâmetros do modelo de calendário.
        dt_minutos (float): Intervalo de tempo entre amostras.
        dias_por_ano_avg (int): Média de dias por ano.
    """
    Ccal_total_mes = 0.0
    k_T = model_params.k_T
    exp_T = model_params.exp_T
    k_soc = model_params.k_soc
    exp_soc = model_params.exp_soc
    exp_tempo = model_params.exp_cal

    # Listas para armazenar os cálculos de cada período
    lista_soc = []
    lista_t_meses = []
    lista_CCal_temperature = []
    lista_Ccal_soc = []
    lista_Ccal_time = []
    lista_dano_periodo = []
    lista_dano_acum_parcial = []

    # Itera sobre cada período parado
    for periodo in lista_periodos_idle:
        soc_percent = periodo['SOC']
        t_meses = periodo['t_meses']

        # Calcula os fatores de dano para este período
        CCal_temperature = k_T * np.exp(exp_T * Tbat_kelvin)
        Ccal_soc = k_soc * np.exp(exp_soc * soc_percent * 100.0)
        Ccal_time = t_meses**exp_tempo

        # Calcula o dano APENAS deste período parado
        dano = CCal_temperature * Ccal_soc * Ccal_time

        Ccal_total_mes = (Ccal_total_mes**exp_tempo + dano**exp_tempo)**(1/exp_tempo)
        
        # Armazena os cálculos intermediários
        lista_soc.append(soc_percent)
        lista_t_meses.append(t_meses)
        lista_CCal_temperature.append(CCal_temperature)
        lista_Ccal_soc.append(Ccal_soc)
        lista_Ccal_time.append(Ccal_time)
        lista_dano_periodo.append(dano)
        lista_dano_acum_parcial.append(Ccal_total_mes)

    # Cria DataFrame com todos os cálculos
    df_calculos_calendario = pd.DataFrame({
        'SOC': lista_soc,
        'num_amostras': [p['t'] for p in lista_periodos_idle],
        'dt_minutos': dt_minutos,
        'tempo_total_minutos': [p['t'] * dt_minutos for p in lista_periodos_idle],
        'minutos_por_mes': (dias_por_ano_avg * 24 * 60) / 12,
        't_meses': lista_t_meses,
        'k_T': k_T,
        'exp_T': exp_T,
        'Tbat_kelvin': Tbat_kelvin,
        'CCal_temperature': lista_CCal_temperature,
        'k_soc': k_soc,
        'exp_soc': exp_soc,
        'Ccal_soc': lista_Ccal_soc,
        'exp_tempo': exp_tempo,
        'Ccal_time': lista_Ccal_time,
        'dano_periodo': lista_dano_periodo,
        'dano_acumulado_parcial': lista_dano_acum_parcial
    })

    return float(Ccal_total_mes), df_calculos_calendario

def _processar_balanco_energetico(p_ca_kw: np.ndarray, dt_h: float) -> tuple[float, float]:
    """Integra as potências de carga e descarga para obter o balanço em kWh."""
    energia_carga_kwh = np.sum(p_ca_kw[p_ca_kw > 0]) * dt_h
    energia_descarga_kwh = np.abs(np.sum(p_ca_kw[p_ca_kw < 0])) * dt_h
    return float(energia_carga_kwh), float(energia_descarga_kwh)

def _analisar_c_rates(p_ca_kw: np.ndarray, cap_kwh: float) -> tuple[float, float]:
    """Calcula as taxas de C-Rate máxima e média do período."""
    c_rates = np.abs(p_ca_kw) / cap_kwh
    return float(c_rates.max()), float(c_rates.mean())

def _extrair_ciclos_rainflow(soc_series: pd.Series) -> tuple[list, float, float]:
    """Encapsula algorimo Rainflow para extração de ciclos e cálculo de EFC/DOD."""
    from besx.domain.models.battery_simulator import picos_e_vales
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    soc_series_simp = picos_e_vales(soc_series, prominence=prominence)
    ciclos_rf = list(rainflow.extract_cycles(soc_series_simp))
    
    num_ciclos = len(ciclos_rf)
    dods = [x[0] for x in ciclos_rf]
    avg_dod = np.mean(dods) if dods else 0.0
    efc = sum([(range_val * count) for range_val, mean, count, start, end in ciclos_rf])
    
    return ciclos_rf, float(efc), float(avg_dod)

def _analisar_distribuicao_soc(soc_series: pd.Series) -> tuple[float, float, float]:
    """Analisa a média e o tempo gasto em extremos de SOC."""
    media_soc = soc_series.mean()
    total_amostras = len(soc_series)
    
    lim_alto = CONFIGURACAO.simulacao.SOC_ALTO_LIMITE
    lim_baixo = CONFIGURACAO.simulacao.SOC_BAIXO_LIMITE
    
    pct_alto = ((soc_series > lim_alto).sum() / total_amostras) * 100
    pct_baixo = ((soc_series < lim_baixo).sum() / total_amostras) * 100
    
    return float(media_soc), float(pct_alto), float(pct_baixo)

def _calcular_soc_idle(soc_series: pd.Series, p_ca_kw: np.ndarray, lista_periodos_idle: list = None) -> float:
    """Calcula o SOC médio ponderado durante os períodos de repouso."""
    if lista_periodos_idle:
        t_total_idle = sum(p['t'] for p in lista_periodos_idle)
        if t_total_idle > 0:
            return sum(p['SOC'] * p['t'] for p in lista_periodos_idle) / t_total_idle
        return 0.0
    
    idle_mask = p_ca_kw == 0.0        
    if idle_mask.any():
        return float(soc_series[idle_mask].mean())
    return 0.0

def calcular_estatisticas_operacionais(
    df_soc_saida: pd.DataFrame, 
    df_potencia_entrada: pd.DataFrame, 
    cap_kwh: float, 
    lista_periodos_idle: list = None
) -> EstatisticasOperacionais:
    """
    Analisa o comportamento operacional do mês: Ciclos, Energias e Stress de SOC.
    
    Orquestra a decomposição do perfil temporal em métricas estáticas utilizando
    funções utilitárias especializadas.
    """
    # 1. Preparação de Dados e Delta T
    soc_series = df_soc_saida['SOC']
    p_ca_kw = df_soc_saida['Potencia_CA_kW'].values if 'Potencia_CA_kW' in df_soc_saida.columns \
              else df_potencia_entrada.iloc[:, 1].values / 1000.0

    dt_h = (df_soc_saida['Tempo'].iloc[1] - df_soc_saida['Tempo'].iloc[0]) / 3600.0 \
           if len(df_soc_saida) > 1 else (1.0 / 60.0)

    # 2. Execução das Análises Modulares
    e_carga, e_descarga = _processar_balanco_energetico(p_ca_kw, dt_h)
    max_c, avg_c = _analisar_c_rates(p_ca_kw, cap_kwh)
    ciclos_rf, efc, avg_dod = _extrair_ciclos_rainflow(soc_series)
    media_soc, pct_alto, pct_baixo = _analisar_distribuicao_soc(soc_series)
    soc_idle_avg = _calcular_soc_idle(soc_series, p_ca_kw, lista_periodos_idle)

    # 3. Consolidação no DTO de Saída
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