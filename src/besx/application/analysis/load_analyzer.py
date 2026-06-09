import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional
import holidays
from besx.infrastructure.logging.logger import logger

@dataclass
class LoadMetrics:
    # Integridade
    dt_min: float
    duration_days: float
    total_records: int
    data_quality_score: float
    
    # Potência
    p_max_w: float
    p_min_w: float
    p_avg_w: float
    p95_w: float
    p90_w: float
    load_factor: float
    
    # Energia
    total_energy_kwh: float
    avg_daily_energy_kwh: float
    est_monthly_energy_kwh: float
    
    # Tarifário (Ponta)
    p_max_ponta_w: float
    energy_ponta_kwh: float
    energy_fora_ponta_kwh: float
    pct_energy_ponta: float
    
    # Estatísticas de Energia e Potência Diária na Ponta
    daily_energy_peak_mean: float
    daily_energy_peak_max: float
    daily_energy_peak_p95: float
    daily_energy_peak_p90: float
    daily_energy_peak_std: float
    power_peak_max_w: float
    power_peak_mean_w: float
    power_peak_p95_w: float
    df_daily_peak: pd.DataFrame

class LoadAnalyzer:
    """
    Motor de análise avançada de perfis de carga para BESS.
    """
    
    def __init__(self, df: pd.DataFrame, time_col: str, load_col: str = 'Carga_W'):
        self.df = df.copy()
        self.time_col = time_col
        self.load_col = load_col
        
        # Garantir datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df[self.time_col]):
            self.df[self.time_col] = pd.to_datetime(self.df[self.time_col])
            
        self.df = self.df.sort_values(by=self.time_col).reset_index(drop=True)

    def analyze(self, peak_start_hour: int = 18, peak_end_hour: int = 21, holidays_list: List = None) -> LoadMetrics:
        """
        Executa a análise completa do perfil.
        """
        # 1. Cálculos de Tempo
        diffs = self.df[self.time_col].diff().dropna().dt.total_seconds() / 60.0
        dt_median = diffs.median() if not diffs.empty else 0.0
        duration = self.df[self.time_col].iloc[-1] - self.df[self.time_col].iloc[0]
        duration_days = duration.total_seconds() / 86400.0
        
        if duration_days < 0.99: # < 24h
             logger.warning(f"Duração insuficiente detectada: {duration_days:.2f} dias.")

        # 2. Cálculos de Potência
        p_data = self.df[self.load_col]
        p_max = p_data.max()
        p_min = p_data.min()
        p_avg = p_data.mean()
        p95 = np.percentile(p_data, 95)
        p90 = np.percentile(p_data, 90)
        load_factor = p_avg / p_max if p_max > 0 else 0.0
        
        # 3. Cálculos de Energia
        # Integral: Sum (W * (dt_min/60)) / 1000 = kWh
        energy_kwh_vec = (p_data * (dt_median / 60.0)) / 1000.0
        total_energy_kwh = energy_kwh_vec.sum()
        avg_daily_energy = total_energy_kwh / duration_days if duration_days > 0 else 0.0
        est_monthly_energy = avg_daily_energy * 30.0
        
        # 4. Inteligência Tarifária (Ponta vs Fora Ponta)
        # Regra: Ignorar Finais de Semana e Feriados na Ponta
        df_temp = self.df.copy()
        df_temp['hour'] = df_temp[self.time_col].dt.hour
        df_temp['day_of_week'] = df_temp[self.time_col].dt.dayofweek
        df_temp['date'] = df_temp[self.time_col].dt.date
        
        # Máscara de Dia Útil (0=Segunda, 4=Sexta)
        is_weekday = df_temp['day_of_week'] < 5
        
        # Máscara de Feriado
        is_holiday = pd.Series([False] * len(df_temp), index=df_temp.index)
        if holidays_list:
             is_holiday = df_temp['date'].isin(holidays_list)
             
        # Janela de Ponta: Dia util + Não feriado + Dentro do Horário
        if peak_start_hour < peak_end_hour:
            is_peak_hour = (df_temp['hour'] >= peak_start_hour) & (df_temp['hour'] < peak_end_hour)
        else:
            # Caso a ponta cruze a meia-noite (raro, mas possível logicamente)
            is_peak_hour = (df_temp['hour'] >= peak_start_hour) | (df_temp['hour'] < peak_end_hour)
            
        mask_ponta = is_weekday & (~is_holiday) & is_peak_hour
        
        df_ponta = df_temp[mask_ponta]
        df_fora_ponta = df_temp[~mask_ponta]
        
        p_max_ponta = df_ponta[self.load_col].max() if not df_ponta.empty else 0.0
        
        # Energia na ponta vs fora ponta (apenas para o período da planilha)
        e_ponta = (df_ponta[self.load_col].sum() * (dt_median / 60.0)) / 1000.0
        e_fora_ponta = (df_fora_ponta[self.load_col].sum() * (dt_median / 60.0)) / 1000.0
        pct_ponta = e_ponta / total_energy_kwh if total_energy_kwh > 0 else 0.0

        # Análise detalhada diária do horário de ponta
        df_temp['is_peak'] = mask_ponta
        df_peak_only = df_temp[mask_ponta].copy()
        
        if not df_peak_only.empty:
            df_peak_only['energy_kwh'] = (df_peak_only[self.load_col] * (dt_median / 60.0)) / 1000.0
            
            df_daily_peak = df_peak_only.groupby('date').agg(
                energy_peak_kwh=('energy_kwh', 'sum'),
                power_max_peak_w=(self.load_col, 'max'),
                power_avg_peak_w=(self.load_col, 'mean')
            ).reset_index()
            
            daily_energy_peak_mean = float(df_daily_peak['energy_peak_kwh'].mean())
            daily_energy_peak_max = float(df_daily_peak['energy_peak_kwh'].max())
            daily_energy_peak_p95 = float(np.percentile(df_daily_peak['energy_peak_kwh'], 95))
            daily_energy_peak_p90 = float(np.percentile(df_daily_peak['energy_peak_kwh'], 90))
            daily_energy_peak_std = float(df_daily_peak['energy_peak_kwh'].std()) if len(df_daily_peak) > 1 else 0.0
            
            power_peak_max_w = float(df_daily_peak['power_max_peak_w'].max())
            power_peak_mean_w = float(df_daily_peak['power_avg_peak_w'].mean())
            power_peak_p95_w = float(np.percentile(df_daily_peak['power_max_peak_w'], 95))
        else:
            df_daily_peak = pd.DataFrame(columns=['date', 'energy_peak_kwh', 'power_max_peak_w', 'power_avg_peak_w'])
            daily_energy_peak_mean = 0.0
            daily_energy_peak_max = 0.0
            daily_energy_peak_p95 = 0.0
            daily_energy_peak_p90 = 0.0
            daily_energy_peak_std = 0.0
            power_peak_max_w = 0.0
            power_peak_mean_w = 0.0
            power_peak_p95_w = 0.0
        
        return LoadMetrics(
            dt_min=dt_median,
            duration_days=duration_days,
            total_records=len(self.df),
            data_quality_score=1.0, # Placeholder para lógica futura
            p_max_w=p_max,
            p_min_w=p_min,
            p_avg_w=p_avg,
            p95_w=p95,
            p90_w=p90,
            load_factor=load_factor,
            total_energy_kwh=total_energy_kwh,
            avg_daily_energy_kwh=avg_daily_energy,
            est_monthly_energy_kwh=est_monthly_energy,
            p_max_ponta_w=p_max_ponta,
            energy_ponta_kwh=e_ponta,
            energy_fora_ponta_kwh=e_fora_ponta,
            pct_energy_ponta=pct_ponta,
            daily_energy_peak_mean=daily_energy_peak_mean,
            daily_energy_peak_max=daily_energy_peak_max,
            daily_energy_peak_p95=daily_energy_peak_p95,
            daily_energy_peak_p90=daily_energy_peak_p90,
            daily_energy_peak_std=daily_energy_peak_std,
            power_peak_max_w=power_peak_max_w,
            power_peak_mean_w=power_peak_mean_w,
            power_peak_p95_w=power_peak_p95_w,
            df_daily_peak=df_daily_peak
        )
