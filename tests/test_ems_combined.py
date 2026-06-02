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

def test_ems_manager_unit_conversions():
    """
    Unit test to verify that the EMSManager correctly converts:
    1. W -> verbatim Watts
    2. kW -> scales by 1000
    3. Wh -> divides by dt
    4. kWh -> scales by 1000 and divides by dt
    """
    timestamps = [
        datetime(2026, 6, 1, 0, 0, 0),
        datetime(2026, 6, 1, 0, 15, 0), # 15 minutes dt = 0.25h
    ]
    
    # 1. Test W (verbatim)
    df_w = pd.DataFrame({'Time': pd.to_datetime(timestamps), 'Load': [100.0, 200.0]})
    manager = EMSManager(strategies=[], p_bess_max_w=100.0, capacidade_nominal_wh=100.0)
    df_out = manager.validate_and_prepare_input(df_w, time_col='Time', load_col='Load', unit='W')
    assert np.allclose(df_out['Carga_W'].values, [100.0, 200.0])
    
    # 2. Test kW (x1000)
    df_kw = pd.DataFrame({'Time': pd.to_datetime(timestamps), 'Load': [1.5, 2.5]})
    df_out = manager.validate_and_prepare_input(df_kw, time_col='Time', load_col='Load', unit='kW')
    assert np.allclose(df_out['Carga_W'].values, [1500.0, 2500.0])
    
    # 3. Test Wh (/dt = /0.25 = x4)
    df_wh = pd.DataFrame({'Time': pd.to_datetime(timestamps), 'Load': [10.0, 20.0]})
    df_out = manager.validate_and_prepare_input(df_wh, time_col='Time', load_col='Load', unit='Wh')
    assert np.allclose(df_out['Carga_W'].values, [40.0, 80.0])
    
    # 4. Test kWh (x1000 /dt = x4000)
    df_kwh = pd.DataFrame({'Time': pd.to_datetime(timestamps), 'Load': [10.0, 20.0]})
    df_out = manager.validate_and_prepare_input(df_kwh, time_col='Time', load_col='Load', unit='kWh')
    assert np.allclose(df_out['Carga_W'].values, [40000.0, 80000.0])

