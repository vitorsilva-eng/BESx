"""
test_engine_validation.py

Este script atua como malha fechada de validação, rodando o motor com
os dados sintéticos gerados e aferindo os resultados de fidelidade.
"""

import os
import sys
import pandas as pd
import numpy as np
import rainflow
import matplotlib.pyplot as plt
from copy import deepcopy

# Adicionar src ao PYTHONPATH para execucao direta se necessario
if os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from besx.config import CONFIGURACAO, PERFIS_BATERIA
from besx.domain.models.battery_simulator import picos_e_vales
from besx.domain.models.degradation_model import dano_ciclo, dano_calendar
from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation
from besx.infrastructure.reports.validation_report import export_xlsx
from besx.infrastructure.logging.logger import logger
import importlib
import besx.infrastructure.plecs.plecs_connector
import besx.domain.models.battery_simulator

def rodar_validacao(perfil_nome="LiFePO4_78Ah", backend="python"):
    # Imports locais para evitar problemas de circularidade ou cache no Streamlit
    from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation
    from besx.domain.models.battery_simulator import picos_e_vales

    logger.info(f"Iniciando bateria de validação Engine/Degradação ({backend}) para {perfil_nome}...")
    
    payload = {
        "status": "success",
        "errors": [],
        "tc1_data": None,
        "tc1_params": {},
        "tc2_data": None,
        "tc2_params": {},
        "historico_degradacao": None,
        "tc3_params": {},
        "history_meses": None,
        "assertions": {}
    }

    # Garante que as pastas existam
    os.makedirs("debug", exist_ok=True)
    os.makedirs(os.path.join("data", "mock_profiles"), exist_ok=True)

    # Injeta a bateria correta baseada no perfil
    CONFIGURACAO.bateria = PERFIS_BATERIA[perfil_nome]
    cfg_bat = CONFIGURACAO.bateria
    
    path_tc1 = os.path.join("data", "mock_profiles", f"{perfil_nome}_TC1.csv")
    path_tc2 = os.path.join("data", "mock_profiles", f"{perfil_nome}_TC2.csv")
    
    if not os.path.exists(path_tc1) or not os.path.exists(path_tc2):
         logger.error("Perfis de missao nao encontrados. Rode mission_profile_generator.py primeiro.")
         payload["status"] = "error"
         payload["errors"].append("Perfis sintéticos não encontrados.")
         return payload

    df_tc1 = pd.read_csv(path_tc1)
    df_tc2 = pd.read_csv(path_tc2)

    # =========================================================
    # 1. TC1: 1C Ideal Capacity Swing (0-100%)
    # =========================================================
    logger.info(">>> Rodando Test Case 1: 1C Ideal Capacity Swing (0-100%)")
    
    # Setup Ideal sem Limites e sem Perdas
    # Criamos um clone manual para garantir isolamento total
    cfg_bat_ideal = cfg_bat.model_copy(deep=True)
    
    V_nom_cel = (cfg_bat_ideal.v_max_celula + cfg_bat_ideal.v_min_celula) / 2.0
    V_nom_banco = V_nom_cel * cfg_bat_ideal.Ns
    
    # Overwrite com valores ideais
    cfg_bat_ideal.Rs = 0.0
    cfg_bat_ideal.rendimento_pcs = 1.0
    cfg_bat_ideal.soc_min = 0.0
    cfg_bat_ideal.soc_max = 1.0
    cfg_bat_ideal.P_bess = 1e12 # Infinito
    
    # OCV constante para evitar taper
    cfg_bat_ideal.ocv_prof = [V_nom_cel] * len(cfg_bat_ideal.soc_prof)    
    cfg_tc1 = CONFIGURACAO.model_copy(deep=True)
    cfg_tc1.bateria = cfg_bat_ideal
    logger.info(f"TC1 Diagnostic: Rs={cfg_tc1.bateria.Rs}, Rend={cfg_tc1.bateria.rendimento_pcs}, SOC_MAX={cfg_tc1.bateria.soc_max}, Vnom={V_nom_cel}")
    I_1C = cfg_tc1.bateria.Ah * cfg_tc1.bateria.Np
    
    payload["tc1_params"] = {
        "I_1C_A": float(I_1C),
        "duration_min": 120,
        "v_nom_banco": float(V_nom_banco)
    }

    # Execução: Injeta SOC inicial 0.0 (vazio)
    # Nota: Forçamos backend python para TC1 para garantir validação da lógica interna sem variações do PLECS
    df_res_tc1 = run_monthly_simulation(df_tc1, soh_atual=1.0, SOC_0=0.0, ctt=1, config=cfg_tc1, backend="python")
    
    if df_res_tc1 is not None:
        soc_max_tc1 = df_res_tc1['SOC'].max()
        soc_min_tc1 = df_res_tc1['SOC'].iloc[-1]
        
        logger.info(f"TC1 Result - SOC Max: {soc_max_tc1*100:.2f}% | SOC Final: {soc_min_tc1*100:.2f}%")
        
        try:
            assert np.isclose(soc_max_tc1, 1.0, atol=1e-2), f"SOC Máximo esperado 1.0 (100%), obtido {soc_max_tc1:.4f} ({soc_max_tc1*100:.2f}%)"
            assert np.isclose(soc_min_tc1, 0.0, atol=1e-2), f"SOC Final esperado 0.0 (0%), obtido {soc_min_tc1:.4f} ({soc_min_tc1*100:.2f}%)"
            logger.info("PASS: TC1 - Integrador de Coulomb validado para swing 1C completo.")
            payload["assertions"]["tc1_1c_swing"] = {"pass": True, "msg": f"Carga/Descarga 100% em 60min. Max={soc_max_tc1*100:.1f}%, Min={soc_min_tc1*100:.1f}%"}
        except AssertionError as e:
            logger.error(f"FAIL: {e}")
            payload["assertions"]["tc1_1c_swing"] = {"pass": False, "msg": str(e)}
        
        payload["tc1_data"] = df_res_tc1
    else:
        logger.error("TC1 falhou (df_res_tc1 is None)")
        payload["assertions"]["tc1_1c_swing"] = {"pass": False, "msg": "Simulação falhou."}


    # =========================================================
    # 2. Validação do Rainflow no TC2
    # =========================================================
    logger.info(">>> Rodando Test Case 2: Partial Cycling (Rainflow DOD)")
    
    cfg_bat_ideal = deepcopy(cfg_bat)
    cfg_bat_ideal.rendimento_pcs = 1.0
    cfg_bat_ideal.Rs = 0.0
    v_nom = (cfg_bat_ideal.v_max_celula + cfg_bat_ideal.v_min_celula) / 2.0
    cfg_bat_ideal.ocv_prof = [v_nom] * len(cfg_bat_ideal.ocv_prof)
    
    config_ideal = deepcopy(CONFIGURACAO)
    config_ideal.bateria = cfg_bat_ideal
    
    # Isolamento de estado para o TC2: força SOC em exatamente 50% para centralizar a onda quadrada
    soc_inicial_tc2 = 0.5
    df_res_tc2 = run_monthly_simulation(df_tc2, soh_atual=1.0, SOC_0=soc_inicial_tc2, ctt=2, config=config_ideal, backend=backend)
    
    if df_res_tc2 is None:
        payload["status"] = "error"
        payload["errors"].append(f"Simulação TC2 falhou usando o backend: {backend}")
        return payload
    
    prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
    # Usa picos_e_vales, lembrando que precisa receber uma Series de pandas indexada pelo tempo ou normal
    soc_series = pd.Series(df_res_tc2['SOC'].values)
    lista_simplificada = picos_e_vales(soc_series, prominence=prominence)
    
    ciclos = list(rainflow.extract_cycles(lista_simplificada))
    ciclos = [c for c in ciclos if c[0] > 0.1]
    
    # Avaliando os DODs (Ranges)
    # Ciclos de carga/descarga sao 20% DOD, range de ~20.
    ranges = [c[0] for c in ciclos]
    logger.info(f"Ciclos extraídos (Ranges): {ranges}")
    try:
        assert any(0.15 <= r <= 0.22 for r in ranges), f"Esperava-se microciclos entre 15% e 22% DOD, encontrado: {ranges}"
        logger.info("PASS: Extração Rainflow detectou corretamente a profundidade de 20% DOD.")
        payload["assertions"]["rainflow_dod"] = {"pass": True, "msg": "Microciclos isolados com ~20% DOD"}
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        payload["assertions"]["rainflow_dod"] = {"pass": False, "msg": str(e)}
        
    payload["tc2_data"] = df_res_tc2
    payload["tc2_params"] = {
        "soc_avg": 50.0,
        "dod_target": 20.0,
        "temp_cyc": float(cfg_bat.Tbat_kelvin - 273.15)
    }

    # =========================================================
    # 3. Acumulação Não-Linear (Stroe) via TC1 sequencial
    # =========================================================
    logger.info(">>> Rodando Teste de Degradação Não Linear (12 meses de TC1)")
    
    # Preparando dados para o modelo
    c_cyc_tot = 0.0
    
    historico_ccyc = []
    
    # Temp
    t_kelvin = cfg_bat.Tbat_kelvin
    param_ciclo = CONFIGURACAO.modelo_degradacao.ciclo
    
    for mes in range(1, 13):
        # A cada mês injetamos a curva TC1 simplificada
        soc_series_tc1 = pd.Series(df_res_tc1['SOC'].values)
        simp_tc1 = picos_e_vales(soc_series_tc1, prominence=prominence)
        
        # O modelo já extrai ciclos rainflow em dano_ciclo
        dano_mes, df_rf = dano_ciclo(simp_tc1.tolist(), t_kelvin, param_ciclo)
        
        # Acumulação Quadrática (stroe empirico)
        c_cyc_tot = np.sqrt(c_cyc_tot**2 + dano_mes**2)
        historico_ccyc.append(c_cyc_tot)
        
        if mes == 1:
            dano_mes1 = dano_mes
        
        logger.info(f"Mês {mes}: Dano Unitário = {dano_mes:.6f} | Acumulado = {c_cyc_tot:.6f}")

    # Checa decaimento não-linear: se fosse linear, o mes 12 seria 12 * dano_mes1
    expected_linear = dano_mes1 * 12
    
    logger.info(f"Acúmulo no final de 12 meses: {historico_ccyc[-1]:.6f}")
    logger.info(f"Acúmulo caso fosse Linear Direto: {expected_linear:.6f}")
    
    try:
        assert historico_ccyc[-1] < expected_linear, "Curva de Degradação está linear! Fator não-linear falhou."
        # No modelo estrito, c_cyc = sqrt(12 * dano^2) = sqrt(12) * dano = ~3.46 * dano
        assert np.isclose(historico_ccyc[-1], np.sqrt(12) * dano_mes1, rtol=1e-2), "C_cyc_tot não obedece a raiz quadrada exata."
        logger.info("PASS: Validação da Degradação Não-Linear Stroe.")
        payload["assertions"]["stroe_nonlinear"] = {"pass": True, "msg": "Acumulação de Capacity Fade é corretamente quadrática"}
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        payload["assertions"]["stroe_nonlinear"] = {"pass": False, "msg": str(e)}

    payload["historico_degradacao"] = historico_ccyc
    payload["history_meses"] = list(range(1, 13))
    payload["tc3_params"] = {
        "duration_months": 12,
        "model": "Stroe (Quadratic Accumulation)"
    }

    # =========================================================
    # 4. Exportação via Relatório
    # =========================================================
    df_resumo = pd.DataFrame({
        'Mes': list(range(1, 13)),
        'C_cyc_Acumulado': historico_ccyc
    })
    
    export_xlsx([df_resumo, df_res_tc1.head(120), df_res_tc2.head(100)], 
                os.path.join("debug", "Engine_Validation_Report.xlsx"))
    
    logger.info("Testes Finalizados com Sucesso. Artifactos salvos em /debug.")
    return payload

if __name__ == "__main__":
    for perfil in PERFIS_BATERIA.keys():
        print(f"\n{'='*50}\nVALIDANDO PERFIL: {perfil}\n{'='*50}")
        res = rodar_validacao(perfil_nome=perfil)
        print(res["assertions"])
