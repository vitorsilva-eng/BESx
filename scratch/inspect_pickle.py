import pandas as pd
import glob
import os
import ast

res_path = "results"
dirs = sorted([d for d in os.listdir(res_path) if os.path.isdir(os.path.join(res_path, d))], reverse=True)
if dirs:
    latest_dir = dirs[0]
    pkl_files = glob.glob(os.path.join(res_path, latest_dir, "data", "resultados_completos*.pkl"))
    if pkl_files:
        print(f"Lendo: {pkl_files[0]}")
        df = pd.read_pickle(pkl_files[0])
        print("Colunas principais:")
        print(df.columns.tolist())
        
        # Pega o df_soc_amostrado do mes 0
        if 'df_soc_amostrado' in df.columns:
            raw = df.iloc[0]['df_soc_amostrado']
            if isinstance(raw, str):
                raw = ast.literal_eval(raw)
            if raw:
                df_soc = pd.DataFrame(raw)
                print("\nColunas do df_soc_amostrado:")
                print(df_soc.columns.tolist())
                print("\nPrimeiras linhas do df_soc_amostrado:")
                print(df_soc.head())
                print("\nUltimas linhas do df_soc_amostrado:")
                print(df_soc.tail())
            else:
                print("df_soc_amostrado vazio")
        else:
            print("df_soc_amostrado nao encontrado")
    else:
        print("Nenhum arquivo pkl encontrado")
else:
    print("Nenhuma pasta de resultados encontrada")
