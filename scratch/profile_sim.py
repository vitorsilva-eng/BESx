
import time
import numpy as np
import pandas as pd
from besx.domain.models.battery_simulator import simular_soc_mes
from besx.domain.models.degradation_engine import DegradationEngine
from besx.config import CONFIGURACAO

def profile_one_month():
    # 1 month = 43200 minutes
    n_steps = 43200
    df_mes = pd.DataFrame({
        'timestamp_min': np.arange(n_steps),
        'pot_w': np.random.uniform(-50000, 50000, n_steps)
    })
    
    soh_atual = 1.0
    soc_inicial = 0.5
    
    start = time.time()
    # Mocking config for simplicity where necessary or using global CONFIGURACAO
    res_sim = simular_soc_mes(df_mes, soh_atual, soc_inicial, CONFIGURACAO.bateria)
    end_sim = time.time()
    print(f"Simulation (Coulomb) took: {end_sim - start:.4f}s")
    
    engine = DegradationEngine(soh_inicial_perc=100.0, config=CONFIGURACAO)
    
    start_deg = time.time()
    damage = engine.calculate_degradation(res_sim, df_mes, 1, "scratch")
    end_deg = time.time()
    print(f"Degradation analysis took: {end_deg - start_deg:.4f}s")
    print(f"Total time per month: {end_deg - start:.4f}s")

if __name__ == "__main__":
    profile_one_month()
