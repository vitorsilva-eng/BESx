import pandas as pd
import numpy as np
from besx.application.analysis.load_analyzer import LoadAnalyzer

def test_load_analyzer_basic_metrics():
    # Create 2 days of constant 1000W (1kW) load every 15 min
    times = pd.date_range("2024-01-01", periods=192, freq="15min") # 24*4*2 = 192
    df = pd.DataFrame({
        "time": times,
        "Carga_W": [1000.0] * 192
    })
    
    analyzer = LoadAnalyzer(df, "time", "Carga_W")
    # Janela de ponta 18h-21h (3h)
    metrics = analyzer.analyze(peak_start_hour=18, peak_end_hour=21)
    
    # 1. Integridade
    assert metrics.dt_min == 15.0
    # 191 intervals of 15min = 2865 min = 1.98958 days
    assert abs(metrics.duration_days - 1.9895) < 0.001
    
    # 2. Potência
    assert metrics.p_max_w == 1000.0
    assert metrics.p_avg_w == 1000.0
    assert metrics.p95_w == 1000.0
    assert metrics.load_factor == 1.0
    
    # 3. Energia
    assert metrics.total_energy_kwh == 48.0
    
    # 4. Ponta
    assert metrics.energy_ponta_kwh == 6.0
    assert abs(metrics.pct_energy_ponta - (6.0 / 48.0)) < 0.0001
    
    # 5. Novas Métricas de Ponta Diárias
    assert metrics.daily_energy_peak_mean == 3.0
    assert metrics.daily_energy_peak_max == 3.0
    assert metrics.daily_energy_peak_p95 == 3.0
    assert metrics.power_peak_max_w == 1000.0
    assert metrics.power_peak_mean_w == 1000.0
    assert metrics.power_peak_p95_w == 1000.0
    assert not metrics.df_daily_peak.empty
    assert len(metrics.df_daily_peak) == 2

def test_load_analyzer_duration_block():
    # Only 10 points (2.5 hours)
    times = pd.date_range("2024-01-01", periods=10, freq="15min")
    df = pd.DataFrame({"time": times, "Carga_W": [1000.0]*10})
    
    analyzer = LoadAnalyzer(df, "time", "Carga_W")
    metrics = analyzer.analyze()
    
    assert metrics.duration_days < 1.0

if __name__ == "__main__":
    test_load_analyzer_basic_metrics()
    test_load_analyzer_duration_block()
    print("All tests passed!")
