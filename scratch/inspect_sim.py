import pandas as pd
import json
import glob
import os

sim_dir = r"c:\Users\Ledax\OneDrive - LEDAX\Área de Trabalho\BESx\results\sim_20260601_215358"
pkl_files = glob.glob(os.path.join(sim_dir, "data", "resultados_completos*.pkl"))
snap_files = glob.glob(os.path.join(sim_dir, "data", "config_snapshot*.json"))

if pkl_files:
    df = pd.read_pickle(pkl_files[0])
    print("DataFrame shape:", df.shape)
    print("Columns:", list(df.columns))
    
    last = df.iloc[-1]
    print("\nÚltimo registro:")
    print("Mês:", last['mes'])
    print("Capacidade Restante (SOH):", last['capacidade_restante'])
    print("Dano Ciclo Acum:", last['dano_ciclo_acum'])
    print("Dano Cal Acum:", last['dano_cal_acum'])
    print("Dano Ciclo Mês Médio:", df['dano_ciclos_mes'].mean())
    print("Dano Cal Mês Médio:", df['dano_cal_mes'].mean())
    
    if snap_files:
        with open(snap_files[0], 'r', encoding='utf-8') as f:
            snap = json.load(f)
        exp_cal = float(snap.get('modelo_degradacao', {}).get('calendario', {}).get('exp_cal', 0.5))
        dias_ano = float(snap.get('dados_entrada', {}).get('dias_por_ano_avg', 365.25))
        print("exp_cal:", exp_cal)
        print("dias_por_ano_avg:", dias_ano)
        
        # Testar calcular_rul
        from besx.domain.models.degradation_model import calcular_rul
        rul_anos = calcular_rul(
            soh_atual_perc=last['capacidade_restante'],
            dano_ciclo_medio=df['dano_ciclos_mes'].mean(),
            dano_cal_medio=df['dano_cal_mes'].mean(),
            acum_ciclo_atual=last['dano_ciclo_acum'],
            acum_cal_atual=last['dano_cal_acum'],
            exp_cal=exp_cal,
            dias_por_ano_avg=dias_ano
        )
        print("calcular_rul retornado:", rul_anos)
