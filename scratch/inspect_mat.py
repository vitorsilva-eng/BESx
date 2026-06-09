import pandas as pd
import os
from besx.config import PATH_DATABASE
from besx.infrastructure.loaders.data_handler import carregar_dados_mat, analisar_integridade_dados

caminho = os.path.join(PATH_DATABASE, "cmveditora.mat")
print("Caminho completo:", caminho)
if os.path.exists(caminho):
    df = carregar_dados_mat(caminho)
    if df is not None:
        print("DataFrame shape:", df.shape)
        dt = analisar_integridade_dados(df)
        print("dt_minutos:", dt)
        minutos_totais = len(df) * dt
        meses_totais = minutos_totais / (30 * 24 * 60)
        print("Duração original (meses):", meses_totais)
        print("Duração original (anos):", meses_totais / 12)
else:
    print("Arquivo não existe no database!")
