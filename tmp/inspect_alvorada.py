import pandas as pd
path = r"C:\Users\Ledax\OneDrive - LEDAX\Área de Trabalho\BESx\_ref\MEMÓRIAS DE MASSA\Alvorada_Consumo_1-ano.xlsx"
df = pd.read_excel(path, nrows=5)
print("Colunas encontradas:")
print(df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head())
