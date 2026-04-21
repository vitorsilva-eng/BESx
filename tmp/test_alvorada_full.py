import pandas as pd
import numpy as np
from besx.application.analysis.load_analyzer import LoadAnalyzer
from besx.application.ems.ems_manager import EMSManager

path = r"C:\Users\Ledax\OneDrive - LEDAX\Área de Trabalho\BESx\_ref\MEMÓRIAS DE MASSA\Alvorada_Consumo_1-ano.xlsx"

print(f"--- ANALISANDO ARQUIVO: {path} ---")

# 1. Simular o processamento inicial do EMSManager
# (O EMSManager faz a validação e conversão de kWh -> Carga_W)
df_raw = pd.read_excel(path)

# Precisamos ajustar o formato da data específico desta planilha antes de mandar para o Manager
# Ex: 25/07/2024 - 23:00 -> 25/07/2024 23:00
df_raw['Data_Reg'] = df_raw['Data do registro'].str.replace(' - ', ' ')

ems_manager = EMSManager(strategies=[], p_bess_max_w=100000, capacidade_nominal_wh=200000)
# O Manager vai detectar o 'kWh' no nome e converter para Watt
df_valid = ems_manager.validate_and_prepare_input(df_raw, 'Data_Reg', 'kWh')

print(f"Registros validados: {len(df_valid)}")

# 2. Rodar o LoadAnalyzer (Janela de Ponta padrão 18h-21h)
analyzer = LoadAnalyzer(df_valid, 'Data_Reg', 'Carga_W')
metrics = analyzer.analyze(peak_start_hour=18, peak_end_hour=21)

print("\n--- 📈 RESULTADOS DO DIAGNÓSTICO ---")
print(f"Duração Total: {metrics.duration_days:.1f} dias")
print(f"Intervalo (dt): {metrics.dt_min:.2f} min")

print("\n[POTÊNCIA]")
print(f"Pmax: {metrics.p_max_w/1000:,.2f} kW")
print(f"P95:  {metrics.p95_w/1000:,.2f} kW")
print(f"P90:  {metrics.p90_w/1000:,.2f} kW")
print(f"Pmed: {metrics.p_avg_w/1000:,.2f} kW")
print(f"Fator de Carga: {metrics.load_factor:.2%}")

print("\n[ENERGIA]")
print(f"Total: {metrics.total_energy_kwh:,.0f} kWh")
print(f"Média Diária: {metrics.avg_daily_energy_kwh:.1f} kWh/dia")
print(f"Projeção Mensal: {metrics.est_monthly_energy_kwh:,.0f} kWh")

print("\n[INTELIGÊNCIA DE PONTA]")
print(f"Pmax na Ponta: {metrics.p_max_ponta_w/1000:,.2f} kW")
print(f"Energia na Ponta: {metrics.energy_ponta_kwh:,.1f} kWh")
print(f"Participação na Ponta: {metrics.pct_energy_ponta:.1%}")

if metrics.duration_days < 1.0:
    print("\nXXX ERRO: DADOS INSUFICIENTES PARA O BESx! XXX")
else:
    print("\n--- STATUS: PLANILHA APROVADA PARA SIMULAÇÃO ---")
