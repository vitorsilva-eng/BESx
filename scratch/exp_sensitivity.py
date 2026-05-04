
import pandas as pd
import numpy as np
from besx.config import CONFIGURACAO
from besx.domain.models.degradation_engine import DegradationEngine
from besx.domain.models.battery_simulator import simular_soc_mes
from besx.infrastructure.logging.logger import logger

def experiment_parallel_sensitivity():
    logger.info("--- Experimento de Sensibilidade: Dano vs N_Unidades ---")
    
    # 1. Configuração (Sany 314Ah)
    cfg = CONFIGURACAO.model_copy(deep=True)
    bat = cfg.bateria
    
    # 2. Perfil de 1 dia (Descarrega 50% de uma unidade)
    # Energia total base = bat.capacidade_nominal_wh * 0.5
    energia_req_wh = bat.capacidade_nominal_wh * 0.5
    
    tempo = np.arange(0, 1441, 1) # 1 dia em minutos
    # Potência constante de descarga para tirar a energia em 4 horas (240 min)
    potencia_w = np.zeros(len(tempo))
    potencia_w[100:340] = energia_req_wh / (240/60) # Watts
    
    df_pot = pd.DataFrame({'Tempo': tempo * 60, 'Potencia_W': potencia_w})
    
    resultados = []
    
    for n in [2, 3, 4]:
        cfg.simulacao.n_unidades = n
        
        # Simula SOC
        df_soc = simular_soc_mes(
            df_mes=df_pot.copy(),
            soh_atual=1.0,
            soc_inicial=1.0,
            cfg_bat=bat,
            n_unidades=n
        )
        
        # Calcula Degradação
        engine = DegradationEngine(soh_inicial_perc=100.0, config=cfg)
        res = engine.calculate_degradation(df_soc, df_pot, 1, "debug")
        
        resultados.append({
            'n': n,
            'dod_max': (df_soc['SOC'].max() - df_soc['SOC'].min()) * 100,
            'dano_ciclo': res.Ccyc,
            'dano_cal': res.Ccal,
            'dano_total': res.Ccyc + res.Ccal,
            'soh': res.soh_atual * 100
        })

    df_res = pd.DataFrame(resultados)
    print("\n--- RESULTADOS DO EXPERIMENTO ---")
    print(df_res.to_string(index=False))

if __name__ == "__main__":
    import os
    os.environ['PYTHONPATH'] = "src"
    experiment_parallel_sensitivity()
