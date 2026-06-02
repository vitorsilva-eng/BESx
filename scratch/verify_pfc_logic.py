
import pandas as pd
import numpy as np
from besx.application.ems.ems_engine import BessEMS
from besx.application.ems.ems_manager import EMSManager, PowerFactorCorrectionStrategy

def test_pfc():
    # Create dummy data: 1kW Ativa, 500VAr Reativa
    df = pd.DataFrame({
        'Time': pd.date_range('2024-01-01', periods=5, freq='h'),
        'Carga_W': [1000.0] * 5,
        'Carga_VAr': [500.0] * 5
    })

    # Setup EMS with PFC Strategy
    # Inverter S_max = 1500 VA
    pfc = PowerFactorCorrectionStrategy()
    manager = EMSManager(
        strategies=[pfc], 
        p_bess_max_w=2000, 
        capacidade_nominal_wh=5000, 
        s_inversor_va=1500
    )

    # Run with Target PF = 1.0 (means Q_rede should be 0, so BESS must dispatch -500VAr)
    df_res = manager.run(df, 'Time', 'Carga_W', pf_target=1.0)

    p_bat = df_res["Potencia_Bateria_W"].iloc[0]
    q_bat = df_res["Potencia_Reativa_Bateria_VAr"].iloc[0]
    q_carga = df_res["Carga_VAr"].iloc[0]
    
    print(f"--- Test PFC Result ---")
    print(f"Potencia Ativa Bateria (P): {p_bat} W")
    print(f"Potencia Reativa Bateria (Q): {q_bat} VAr")
    print(f"Carga Reativa Inicial: {q_carga} VAr")
    print(f"Q Rede Final (Carga + Bateria): {q_carga + q_bat} VAr")
    
    # Assertions
    assert p_bat == 0.0, "Active power should be zero for pure PFC"
    assert q_bat == -500.0, "Should have dispatched -500VAr to cancel +500VAr load"
    print("Test Passed!")

def test_pfc_clipping():
    # Create dummy data: 1kW Ativa, 2000VAr Reativa
    df = pd.DataFrame({
        'Time': pd.date_range('2024-01-01', periods=5, freq='h'),
        'Carga_W': [1000.0] * 5,
        'Carga_VAr': [2000.0] * 5
    })

    # Inverter S_max = 1500 VA
    pfc = PowerFactorCorrectionStrategy()
    manager = EMSManager(strategies=[pfc], p_bess_max_w=2000, capacidade_nominal_wh=5000, s_inversor_va=1500)

    # Target PF = 1.0 -> Req = -2000VAr. But S_max = 1500. So should clip to -1500.
    df_res = manager.run(df, 'Time', 'Carga_W', pf_target=1.0)
    q_bat = df_res["Potencia_Reativa_Bateria_VAr"].iloc[0]
    
    print(f"--- Test PFC Clipping Result ---")
    print(f"Potencia Reativa Bateria (Q): {q_bat} VAr")
    
    assert q_bat == -1500.0, f"Should have clipped to -1500VAr, got {q_bat}"
    print("Clipping Test Passed!")

if __name__ == '__main__':
    test_pfc()
    test_pfc_clipping()
