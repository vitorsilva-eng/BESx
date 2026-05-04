
import pandas as pd
import numpy as np
from besx.config import CONFIGURACAO, SimulacaoConfig
from besx.domain.models.degradation_engine import DegradationEngine
from besx.infrastructure.logging.logger import logger

def test_c_rate_parity():
    """
    Valida se o C-Rate é calculado corretamente para 1 vs N unidades.
    """
    logger.info("Iniciando teste de paridade de C-Rate...")
    
    # 1. Configuração Base (1 unidade)
    config_1 = CONFIGURACAO.model_copy(deep=True)
    config_1.simulacao.n_unidades = 1
    config_1.bateria.capacidade_nominal_wh = 50000  # 50 kWh
    config_1.bateria.Ah = 100
    config_1.bateria.Ns = 140 # ~500V
    config_1.bateria.Np = 1
    
    # Perfil de 1 hora a 10kW constante (0.2C)
    tempo = np.arange(0, 61, 1) # 61 minutos
    potencia_1 = np.ones(len(tempo)) * -10000 # -10kW
    df_mes_1 = pd.DataFrame({'Tempo': tempo * 60, 'Potencia_CA_W': potencia_1})
    perfil_soc_1 = pd.DataFrame({
        'Tempo': tempo * 60, 
        'SOC': np.linspace(1.0, 0.8, len(tempo)),
        'Potencia_CA_kW': potencia_1 / 1000.0
    })
    
    engine_1 = DegradationEngine(soh_inicial_perc=100.0, config=config_1)
    res_1 = engine_1.calculate_degradation(perfil_soc_1, df_mes_1, 1, "debug")
    
    c_rate_1 = res_1.stats_ops.C_Rate_Max
    logger.info(f"C-Rate (1 unid, 10kW/50kWh): {c_rate_1:.4f}")
    
    # 2. Configuração Paralela (2 unidades)
    config_2 = CONFIGURACAO.model_copy(deep=True)
    config_2.simulacao.n_unidades = 2
    config_2.bateria.capacidade_nominal_wh = 50000
    config_2.bateria.Ah = 100
    config_2.bateria.Ns = 140
    config_2.bateria.Np = 1
    
    # Perfil de 1 hora a 20kW constante (0.2C do conjunto de 100kWh)
    potencia_2 = np.ones(len(tempo)) * -20000 # -20kW
    df_mes_2 = pd.DataFrame({'Tempo': tempo * 60, 'Potencia_CA_W': potencia_2})
    perfil_soc_2 = pd.DataFrame({
        'Tempo': tempo * 60, 
        'SOC': np.linspace(1.0, 0.8, len(tempo)), # SOC cai igual
        'Potencia_CA_kW': potencia_2 / 1000.0
    })
    
    engine_2 = DegradationEngine(soh_inicial_perc=100.0, config=config_2)
    res_2 = engine_2.calculate_degradation(perfil_soc_2, df_mes_2, 1, "debug")
    
    c_rate_2 = res_2.stats_ops.C_Rate_Max
    logger.info(f"C-Rate (2 unid, 20kW/100kWh): {c_rate_2:.4f}")
    
    # Validação
    assert abs(c_rate_1 - c_rate_2) < 0.001, f"DISCREPÂNCIA: 1u={c_rate_1}, 2u={c_rate_2}"
    
    logger.info("SUCESSO: Paridade de C-Rate validada!")

if __name__ == "__main__":
    test_c_rate_parity()
