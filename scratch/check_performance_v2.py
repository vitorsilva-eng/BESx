
import pandas as pd
import numpy as np
import time
from besx.config import CONFIGURACAO
from besx.domain.models.battery_simulator import simular_soc_mes
from besx.domain.models.degradation_engine import DegradationEngine, DamageResult

def run_performance_test():
    # Carregar dados mockados (1 mês em minutos)
    n_pontos = 44640 
    df_mes = pd.DataFrame({
        'timestamp': np.arange(n_pontos),
        'pot_w': np.sin(np.linspace(0, 4*np.pi, n_pontos)) * 100000 
    })
    
    cfg = CONFIGURACAO
    soh = 1.0
    soc_init = 0.5
    
    print("--- Aquecendo JIT (1a execução) ---")
    _ = simular_soc_mes(df_mes, soh, soc_init, cfg.bateria)
    
    print("--- Iniciando Teste de Performance (Média de 10 execuções) ---")
    
    n_exec = 10
    total_sim = 0
    total_deg = 0
    
    for i in range(n_exec):
        start_exec = time.time()
        df_soc = simular_soc_mes(df_mes, soh, soc_init, cfg.bateria)
        sim_time = time.time() - start_exec
        
        engine = DegradationEngine(100.0, cfg)
        start_deg = time.time()
        res = engine.calculate_degradation(df_soc, df_mes, 1, "debug/")
        deg_time = time.time() - start_deg
        
        total_sim += sim_time
        total_deg += deg_time
    
    avg_sim = total_sim / n_exec
    avg_deg = total_deg / n_exec
    total_avg = avg_sim + avg_deg
    
    print(f"Tempo Médio (1 mês): {total_avg:.64}s")
    print(f"  - Simulação (Coulomb JIT): {avg_sim:.6f}s")
    print(f"  - Degradação (Vetorizada/Passo Único): {avg_deg:.6f}s")
    print(f"Velocidade Projetada: {1.0/total_avg:.2f} meses/s")
    print("-" * 50)
    
    if 1.0/total_avg > 5:
        print(f"RESULTADO: SUCESSO ({1.0/total_avg:.2f} meses/s)")
    else:
        print(f"RESULTADO: ABAIXO DA META ({1.0/total_avg:.2f} meses/s)")

if __name__ == "__main__":
    run_performance_test()
