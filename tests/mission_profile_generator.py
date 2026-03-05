"""
mission_profile_generator.py

Este script gera dados sintéticos (perfis de missão) para testes do motor
de simulação de baterias.
"""

import os
import pandas as pd
from besx.config import PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

def generate_profiles(bateria_alvo: str = None):
    output_dir = os.path.join("data", "mock_profiles")
    os.makedirs(output_dir, exist_ok=True)
    
    gerados = {}
    
    logger.info(f"Iniciando a geração de perfis sintéticos em {output_dir}")
    
    for nome_perfil, cfg in PERFIS_BATERIA.items():
        if bateria_alvo and nome_perfil != bateria_alvo:
            continue
            
        # Verificação preventiva: Valores Pydantic podem ser acessados via notação de ponto
        v_min = cfg.v_min_celula if cfg.v_min_celula else 2.5
        v_max = cfg.v_max_celula if cfg.v_max_celula else 3.65
        v_nom_celula = (v_max + v_min) / 2.0
        
        ah_celula = cfg.Ah if cfg.Ah else 100.0
        ns = cfg.Ns if cfg.Ns else 1
        np_val = cfg.Np if cfg.Np else 1
        
        # Potência de 1C (Watts)
        p_1c = ah_celula * np_val * ns * v_nom_celula
        logger.info(f"[{nome_perfil}] Potência 1C calculada: {p_1c:.2f} W")
        
        # --- TC1: 1C Ideal Capacity Swing (0-100%) ---
        # Perfil 1C Constante: 60 minutos de carga e 60 minutos de descarga
        # O SOC deve ir de 0% a 100% e retornar a 0% cravado.
        tc1_time = list(range(121))
        tc1_power = [p_1c] * 60 + [-p_1c] * 61
        
        df_tc1 = pd.DataFrame({'timestamp_min': tc1_time, 'pot_w': tc1_power})
        path_tc1 = os.path.join(output_dir, f"{nome_perfil}_TC1.csv")
        df_tc1.to_csv(path_tc1, index=False)
        
        # --- TC2: Partial Cycling (Dynamic, 20% DOD) ---
        # Onda quadrada em torno de 50% SOC.
        # Para evitar corte no BMS pelas resistências altas do JSON, usaremos 0.1C (~10% da pot 1C).
        # A 0.1C, demoramos 60 minutos para subir 10% de SOC (de 50 a 60).
        # Para o ciclo de 20% DOD, demoramos 120 minutos por meia-onda.
        tc2_time = []
        tc2_power = []
        t_current = 0
        
        p_tc2 = p_1c * 0.1
        
        def add_segment(time_min, power_val):
            nonlocal t_current
            for _ in range(int(time_min)):
                tc2_time.append(t_current)
                tc2_power.append(power_val)
                t_current += 1

        add_segment(60, p_tc2) # sobe para 60%
        for _ in range(10):  # 10 ciclos
            add_segment(120, -p_tc2)  # desce para 40% (20% DOD)
            add_segment(120, p_tc2)   # sobe para 60%
            
        df_tc2 = pd.DataFrame({'timestamp_min': tc2_time, 'pot_w': tc2_power})
        path_tc2 = os.path.join(output_dir, f"{nome_perfil}_TC2.csv")
        df_tc2.to_csv(path_tc2, index=False)
        
        # --- TC3: Idle/Calendar ---
        # 0.0 W por 72 horas (4320 minutos)
        tc3_time = list(range(4321))
        tc3_power = [0.0] * 4321
        
        df_tc3 = pd.DataFrame({'timestamp_min': tc3_time, 'pot_w': tc3_power})
        path_tc3 = os.path.join(output_dir, f"{nome_perfil}_TC3.csv")
        df_tc3.to_csv(path_tc3, index=False)
        
        logger.info(f"[{nome_perfil}] Perfis TC1, TC2 e TC3 gerados.")
        
        gerados[nome_perfil] = {
            "TC1": path_tc1,
            "TC2": path_tc2,
            "TC3": path_tc3
        }

    return gerados

if __name__ == "__main__":
    generate_profiles()
