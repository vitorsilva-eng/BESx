import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from besx.application.ems.ems_engine import BessEMS
from besx.application.ems.ems_manager import EMSManager, CombinedStrategyLSPS

def test_combined_ems_priority_and_logic():
    """
    Unit test to verify combined Peak Shaving and Load Shifting logic:
    1. Peak Shaving takes priority over Load Shifting at all times.
    2. Headroom capacity for charging is respected in charging windows.
    3. Normal Load Shifting discharges in peak windows.
    4. Weekends and holidays disable Load Shifting but NOT Peak Shaving.
    """
    bess_ems = BessEMS()
    
    # 1. Create telemetry DataFrame
    # 2026-06-01 is a Monday (Weekday)
    # We will test 4 key timestamps:
    # t0: 02:00 (Weekday, Inside charge window, load = 60kW, limit = 100kW) -> Should charge at +40kW (headroom)
    # t1: 12:00 (Weekday, Idle window, load = 150kW, limit = 100kW) -> Should discharge at -50kW (peak shaving)
    # t2: 19:00 (Weekday, Inside discharge window, load = 80kW, limit = 100kW) -> Should discharge at -80kW (load shifting)
    # t3: 12:00 (Saturday 2026-06-06, Idle window, load = 150kW, limit = 100kW) -> Should discharge at -50kW (peak shaving on weekend)
    # t4: 19:00 (Saturday 2026-06-06, Inside discharge window, load = 80kW, limit = 100kW) -> Should be IDLE 0kW (no arbitrage on weekend)
    
    timestamps = [
        datetime(2026, 6, 1, 2, 0, 0),
        datetime(2026, 6, 1, 12, 0, 0),
        datetime(2026, 6, 1, 19, 0, 0),
        datetime(2026, 6, 6, 12, 0, 0),
        datetime(2026, 6, 6, 19, 0, 0),
    ]
    
    loads_w = [
        60000.0,
        150000.0,
        80000.0,
        150000.0,
        80000.0
    ]
    
    df_carga = pd.DataFrame({
        'Time': pd.to_datetime(timestamps),
        'Carga_W': loads_w
    })
    
    # Executing Strategy
    strategy = CombinedStrategyLSPS()
    
    # Setup parameters
    kwargs = {
        'limite_demanda_kw': 100.0,
        'hora_inicio_carga': 22,
        'hora_fim_carga': 17,
        'hora_inicio_descarga': 18,
        'hora_fim_descarga': 21,
        'faixa_seguranca_kw': 0.0,
        'faixa_seguranca_pct': 0.0,
        'ignorar_fins_de_semana': True,
        'feriados': [],
        'time_col': 'Time',
        'load_col': 'Carga_W'
    }
    
    # Execute dispatch logic
    df_out = strategy.execute(df_carga, bess_ems, **kwargs)
    
    # Assertions
    powers = df_out['Potencia_Bateria_W'].values
    
    # t0: 02:00 Monday -> Charge with headroom (100kW - 60kW = 40kW)
    assert np.isclose(powers[0], 40000.0), f"Expected 40kW charge at 02:00, got {powers[0]/1000}kW"
    
    # t1: 12:00 Monday -> Peak shaving outside discharge window (100kW - 150kW = -50kW)
    assert np.isclose(powers[1], -50000.0), f"Expected -50kW peak shaving at 12:00, got {powers[1]/1000}kW"
    
    # t2: 19:00 Monday -> Load Shifting discharge on peak hours (-80kW)
    assert np.isclose(powers[2], -80000.0), f"Expected -80kW load shifting at 19:00, got {powers[2]/1000}kW"
    
    # t3: 12:00 Saturday -> Peak shaving on weekend (100kW - 150kW = -50kW)
    assert np.isclose(powers[3], -50000.0), f"Expected -50kW peak shaving on Saturday, got {powers[3]/1000}kW"
    
    # t4: 19:00 Saturday -> Idle on weekend discharge window (0kW)
    assert np.isclose(powers[4], 0.0), f"Expected 0kW (idle) on Saturday discharge window, got {powers[4]/1000}kW"
