
import math
import pandas as pd
import numpy as np
import rainflow

from besx.config import DegradacaoCicloConfig, DegradacaoCalendarioConfig, CONFIGURACAO, ModeloDegradacaoConfig
from besx.infrastructure.logging.logger import logger

def acumular_dano(Ccal_total_mes: float, acum_cal_global: float, exp_tempo: float) -> float:
    """
    Acumula o dano de acordo com a exponencial.
    """
    return (Ccal_total_mes**exp_tempo + acum_cal_global**exp_tempo)**(1/exp_tempo)

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
    dano_total_acumulado: float, 
    meses_simulados: float, 
    dias_por_ano_avg: float
) -> float:
    """
    Projeta o Remaining Useful Life (RUL) em anos.
    Assume morte da bateria em 80% do SOH.
    """
    if meses_simulados <= 0:
        return 999.0
        
    dias_simulados = meses_simulados * (dias_por_ano_avg / 12)
    dano_diario = dano_total_acumulado / dias_simulados if dias_simulados > 0 else 0.0
    dano_anual = dano_diario * 365.25
    
    perda_restante = soh_atual_perc - 80.0
    rul_anos = perda_restante / dano_anual if dano_anual > 0 else 999.0
    return float(rul_anos)

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

def calcular_estatisticas_operacionais(df_soc_saida: pd.DataFrame, df_potencia_entrada: pd.DataFrame, cap_kwh: float, lista_periodos_idle: list = None) -> dict:
    """
    Analisa o comportamento do mês: Ciclos (Rainflow), C-Rates e Energia Utilizada.
    """
    # --- 1. Preparação (SOC e Potência) ---
    soc_series = df_soc_saida['SOC']
    
    # Usamos a potência real do simulador (se disponível) ou a solicitada como fallback
    if 'Potencia_CA_kW' in df_soc_saida.columns:
        p_ca_kw = df_soc_saida['Potencia_CA_kW'].values
    else:
        # Fallback: Assume coluna 1 como potência (Entrada em Watts)
        p_ca_kw = df_potencia_entrada.iloc[:, 1].values / 1000.0

    # Delta T em horas para integração de energia
    if len(df_soc_saida) > 1:
        dt_h = (df_soc_saida['Tempo'].iloc[1] - df_soc_saida['Tempo'].iloc[0]) / 3600.0
    else:
        dt_h = 1.0 / 60.0 # 1 minuto padrão
        
    # --- 2. Cálculos de Energia (Integração de Riemann) ---
    # P > 0: Bateria carregando (Energia entra)
    # P < 0: Bateria descarregando (Energia sai)
    energia_carga_kwh = np.sum(p_ca_kw[p_ca_kw > 0]) * dt_h
    energia_descarga_kwh = np.abs(np.sum(p_ca_kw[p_ca_kw < 0])) * dt_h

    # --- 3. Análise de C-Rate ---
    c_rates = np.abs(p_ca_kw) / cap_kwh
    max_c_rate = c_rates.max()
    avg_c_rate = c_rates.mean()

    # --- 4. Análise de Ciclos (Rainflow) ---
    from besx.domain.models.battery_simulator import picos_e_vales
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    soc_series_simp = picos_e_vales(soc_series, prominence=prominence)
    ciclos_rf = list(rainflow.extract_cycles(soc_series_simp))

    num_ciclos = len(ciclos_rf)

    # DOD Médio
    dods = [x[0] for x in ciclos_rf]
    avg_dod = np.mean(dods) if dods else 0

    # --- 5. Análise de Throughput (EFC via Rainflow) ---
    # Cada ciclo completo (1.0 DOD) = 1 EFC.
    efc = sum([(range_val * count) for range_val, mean, count, start, end in ciclos_rf])

    # --- 6. Análise de Stress / Severidade ---
    media_soc = soc_series.mean()
    tempo_alto_soc = (soc_series > 0.9).sum()
    tempo_baixo_soc = (soc_series < 0.1).sum()

    total_amostras = len(soc_series)
    pct_alto = (tempo_alto_soc / total_amostras) * 100
    pct_baixo = (tempo_baixo_soc / total_amostras) * 100

    # --- 7. SOC Médio em Repouso ---
    if lista_periodos_idle:
        t_total_idle = sum(p['t'] for p in lista_periodos_idle)
        if t_total_idle > 0:
            soc_idle_avg = sum(p['SOC'] * p['t'] for p in lista_periodos_idle) / t_total_idle
        else:
            soc_idle_avg = np.nan
    else:
        idle_mask = p_ca_kw == 0.0        
        if idle_mask.any():
            soc_idle_avg = soc_series[idle_mask].mean()
        else:
            soc_idle_avg = np.nan

    return {
        "Ciclos_Contagem": num_ciclos,
        "EFC_Ciclos_Equivalentes": round(float(efc), 2),
        "DOD_Medio_Perc": round(float(avg_dod), 4),
        "C_Rate_Max": round(float(max_c_rate), 2), 
        "C_Rate_Medio": round(float(avg_c_rate), 3),
        "SOC_Medio": round(float(media_soc), 4),
        "SOC_Medio_Idle": round(float(soc_idle_avg), 4),
        "Tempo_SOC_Alto_Perc": round(float(pct_alto), 1),
        "Tempo_SOC_Baixo_Perc": round(float(pct_baixo), 1),
        "Energia_Carga_kWh": round(float(energia_carga_kwh), 2),
        "Energia_Descarga_kWh": round(float(energia_descarga_kwh), 2),
        "Rainflow_Cycles": ciclos_rf 
    }
