import pandas as pd
import numpy as np
import os
import holidays
from besx.application.ems.ems_manager import EMSManager, CombinedStrategyLSPS

path = r"C:\Users\Ledax\OneDrive - LEDAX\Área de Trabalho\BESx\_ref\MEMÓRIAS DE MASSA\CINDACTA - Memória de massa 7029467468.xlsx"

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

try:
    print("Loading full Excel telemetry data from CINDACTA...")
    df_raw = pd.read_excel(path)
    print(f"Loaded {len(df_raw)} rows.")
    
    # 1. Formatting columns defensively
    df_clean = pd.DataFrame()
    df_clean['datetime'] = pd.to_datetime(df_raw['Data'])
    
    # Clean string decimals like '0,00' if any
    def clean_numeric(val):
        if pd.isna(val):
            return 0.0
        if isinstance(val, str):
            val = val.replace('.', '').replace(',', '.')
        return float(val)
        
    df_clean['kWh_fornecido'] = df_raw['kWh fornecido'].apply(clean_numeric)
    
    # Median dt calculation
    df_clean = df_clean.sort_values(by='datetime').reset_index(drop=True)
    dts_hours = df_clean['datetime'].diff().dt.total_seconds() / 3600.0
    dt_median = dts_hours.median()
    print(f"Detected median time-step (dt): {dt_median * 60:.1f} minutes ({dt_median:.4f} hours).")
    
    # Convert Energy (kWh) in 15min interval to average Power (Watts)
    # Power (W) = Energy (kWh) * 1000 / dt (hours)
    df_clean['Carga_W'] = (df_clean['kWh_fornecido'] * 1000.0) / dt_median
    
    max_load_w = df_clean['Carga_W'].max()
    print(f"Original Max Active Power (Pmax): {max_load_w/1000:.2f} kW")
    
    # Let's set a contract demand limit at 85% of Pmax to enforce peak shaving
    contract_limit_kw = (max_load_w * 0.85) / 1000.0
    print(f"Setting target contract demand limit to 85% of Pmax: {contract_limit_kw:.2f} kW")
    
    # Initialize EMSManager with the Combined strategy
    # A realistic 1.5MW / 3.0MWh battery for huge CINDACTA site peak shaving
    ems_manager = EMSManager(
        strategies=[CombinedStrategyLSPS()],
        p_bess_max_w=1500000.0,
        capacidade_nominal_wh=3000000.0
    )
    
    # Get holidays for DF
    years = df_clean['datetime'].dt.year.unique().tolist()
    try:
        feriados_br = holidays.BR(years=years, state="DF")
    except TypeError:
        feriados_br = holidays.BR(years=years)
    lista_feriados = list(feriados_br.keys())
    
    # Setup combined parameters (no time_col or load_col in kwargs to avoid duplication error)
    kwargs = {
        'limite_demanda_kw': contract_limit_kw,
        'hora_inicio_carga': 22,
        'hora_fim_carga': 17,
        'hora_inicio_descarga': 18,
        'hora_fim_descarga': 21,
        'faixa_seguranca_kw': 0.0,
        'faixa_seguranca_pct': 0.0,
        'ignorar_fins_de_semana': True,
        'feriados': lista_feriados
    }
    
    print("Running combined Peak Shaving & Load Shifting dispatcher...")
    df_result = ems_manager.run(df_clean, time_col='datetime', load_col='Carga_W', **kwargs)
    
    # Calculate performance metrics
    p_orig = df_result['Carga_W'].values
    p_bess = df_result['Potencia_Bateria_W'].values
    p_grid = df_result['Carga_Ajustada_W'].values
    
    max_orig_kw = p_orig.max() / 1000.0
    max_grid_kw = p_grid.max() / 1000.0
    shaved_kw = max_orig_kw - max_grid_kw
    
    charged_kwh = (p_bess[p_bess > 0].sum() * dt_median) / 1000.0
    discharged_kwh = (np.abs(p_bess[p_bess < 0]).sum() * dt_median) / 1000.0
    
    print("\n" + "="*50)
    print("           EMS COMBINED DISPATCH ANALYSIS")
    print("="*50)
    print(f"Consumer: CINDACTA (Telemetry Real)")
    print(f"Data points count: {len(df_result)} records")
    print(f"Original Peak Load: {max_orig_kw:.2f} kW")
    print(f"Target Demand Limit: {contract_limit_kw:.2f} kW")
    print(f"Adjusted Grid Peak: {max_grid_kw:.2f} kW")
    print(f"Peak Shaved successfully: {shaved_kw:.2f} kW")
    print(f"Total BESS Energy Charged: {charged_kwh:.2f} kWh")
    print(f"Total BESS Energy Discharged: {discharged_kwh:.2f} kWh")
    
    # Check exceedances
    limit_w = contract_limit_kw * 1000.0
    exceeded_count = np.sum(p_grid > limit_w + 1.0)
    print(f"Exceedances above limit: {exceeded_count} records")
    
    if exceeded_count == 0:
        print("SUCCESS: Demand limit was strictly protected at all times!")
    else:
        print("INFO: Some points exceeded limit (physical constraints/headroom limitations may apply, though EMS is unconstrained).")
    print("="*50)
    
except Exception as e:
    import traceback
    print(f"Critical error during execution: {e}")
    traceback.print_exc()
