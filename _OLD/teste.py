import scipy.io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Função auxiliar para analisar cada arquivo
def inspecionar_mat(nome_arquivo):
    print(f"\n{'='*20} ANÁLISE DE: {nome_arquivo} {'='*20}")
    try:
        mat = scipy.io.loadmat(nome_arquivo)
        # Filtra chaves que não são metadados (ex: __header__)
        variaveis = [k for k in mat.keys() if not k.startswith('__')]
        
        if not variaveis:
            print("ERRO: Nenhuma variável de dados encontrada no arquivo.")
            return

        nome_var = variaveis[0]
        dados = mat[nome_var]
        print(f"Variável principal: '{nome_var}' | Formato (Shape): {dados.shape}")

        # Identifica Vetores de Tempo e Potência
        # O padrão esperado é 2 linhas (Tempo, Potencia) ou 2 colunas
        if dados.shape[0] == 2: # Formato 2xN
            tempo = dados[0, :]
            potencia = dados[1, :]
            formato = "2xN (Linhas)"
        elif dados.shape[1] == 2: # Formato Nx2
            tempo = dados[:, 0]
            potencia = dados[:, 1]
            formato = "Nx2 (Colunas)"
        else:
            print(f"ALERTA: Formato estranho {dados.shape}. Esperado 2 colunas ou 2 linhas.")
            return

        # Análise de Tempo (dt)
        dt_amostras = np.diff(tempo)
        dt_medio = np.mean(dt_amostras)
        dt_constante = np.allclose(dt_amostras, dt_medio, atol=1e-2)
        
        print(f"--- Tempo ---")
        print(f"Início: {tempo.min()} | Fim: {tempo.max()}")
        print(f"Passo de tempo (dt) médio: {dt_medio:.2f}")
        print(f"O passo de tempo é constante? {'SIM' if dt_constante else 'NÃO (Cuidado!)'}")

        # Análise de Potência (Unidades)
        max_pot = np.max(np.abs(potencia))
        mean_pot = np.mean(np.abs(potencia))
        
        print(f"--- Potência ---")
        print(f"Máximo Absoluto: {max_pot:.2f}")
        print(f"Média Absoluta:  {mean_pot:.2f}")
        
        # Heurística de Unidade
        # Se a potência for > 10.000, provavalmente é Watts. Se for < 10.000, provavelmente kW (para BESS industrial)
        provavel_unidade = "Watts (W)" if max_pot > 5000 else "Kilowatts (kW)"
        print(f"Unidade Provável: {provavel_unidade}")

    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")

# Executa para os dois arquivos
inspecionar_mat('Atot.mat')
inspecionar_mat('cmveditora.mat')