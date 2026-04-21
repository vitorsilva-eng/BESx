import pandas as pd
import numpy as np
from besx.domain.models.battery_simulator import simular_soc_mes
from besx.config import BateriaConfig
from besx.infrastructure.logging.logger import logger

def test_parallel_logic():
    # 1. Configuração Base (LFP Generic)
    cfg = BateriaConfig(
        quimica="LFP",
        capacidade_nominal_wh=50000.0, # 50kWh
        Ah=100.0,
        Ns=100,
        Np=1,
        Rs=0.001,
        v_min_celula=2.5,
        v_max_celula=3.6,
        P_bess=10000.0,  # 10kW por unidade
        rendimento_pcs=1.0,
        soc_min=0.0,
        soc_max=1.0,
        soc_prof=[0.0, 1.0],
        ocv_prof=[3.0, 3.6]
    )

    # 2. Criar Perfil de Potência (Descarga constante de 5kW por 1 hora)
    # n_passos = 60 (1 min cada)
    df_base = pd.DataFrame({
        'Tempo': np.arange(60),
        'Potencia_W': np.full(60, 5000.0) # 5kW
    })

    logger.info("--- Iniciando Teste de Paralelismo ---")

    # 3. Simulação 1: Uma unidade, 5kW
    df_1unit = simular_soc_mes(
        df_mes=df_base.copy(),
        soh_atual=1.0,
        soc_inicial=1.0,
        cfg_bat=cfg,
        n_unidades=1
    )
    soc_final_1 = df_1unit['SOC'].iloc[-1]

    # 4. Simulação 2: Duas unidades, 10kW (dobro da carga, dobro da capacidade)
    df_2units = simular_soc_mes(
        df_mes=pd.DataFrame({
            'Tempo': np.arange(60),
            'Potencia_W': np.full(60, 10000.0) # 10kW
        }),
        soh_atual=1.0,
        soc_inicial=1.0,
        cfg_bat=cfg,
        n_unidades=2
    )
    soc_final_2 = df_2units['SOC'].iloc[-1]

    logger.info(f"SOC Final (1 Unid, 5kW): {soc_final_1:.4f}")
    logger.info(f"SOC Final (2 Unid, 10kW): {soc_final_2:.4f}")

    # Validação
    diff = abs(soc_final_1 - soc_final_2)
    if diff < 1e-6:
        logger.info("SUCCESS: O escalonamento de capacidade e potencia esta matematicamente correto.")
    else:
        logger.error(f"FAILURE: Diferenca de SOC detectada ({diff:.6f}).")

if __name__ == "__main__":
    test_parallel_logic()
