import pandas as pd
import scipy.io
import numpy as np
import os
from besx.infrastructure.logging.logger import logger

def expandir_curva_carga(
    caminho_arquivo, 
    coluna_data='Data', 
    coluna_potencia='Potencia', 
    anos_para_expandir=10, 
    separador_csv=','
):
    """
    Lê uma curva de carga, detecta a resolução e expande para N anos.
    Assume crescimento vegetativo de 0%.
    Adiciona contagem de meses padronizados de 30 dias.
    """
    
    logger.info(f"--- Lendo arquivo: {caminho_arquivo} ---")
    try:
        # Tenta ler o CSV. Converta a coluna de data para datetime.
        df = pd.read_csv(caminho_arquivo, sep=separador_csv)
        df[coluna_data] = pd.to_datetime(df[coluna_data])
        df = df.sort_values(by=coluna_data).reset_index(drop=True)
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo. Verifique o separador ou nomes das colunas.\nErro: {e}")
        return None

    # --- 1. Detectar Resolução ---
    if len(df) < 2:
        logger.error("Erro: O arquivo precisa ter pelo menos 2 linhas para calcular a resolução.")
        return None
        
    delta_t = df[coluna_data][1] - df[coluna_data][0]
    resolucao_minutos = delta_t.total_seconds() / 60
    
    logger.info(f"Resolução detectada: {resolucao_minutos:.1f} minutos")
    
    # --- 2. Preparar Expansão ---
    # Dados originais (apenas a coluna de potência)
    potencia_base = df[coluna_potencia].values
    total_linhas_base = len(potencia_base)
    
    # Cálculo de quantas vezes precisamos repetir os dados
    # Se a base já for 1 ano, repetimos 'anos_para_expandir' vezes.
    # Se a base for menor, precisaríamos calcular, mas assumiremos que a entrada
    # é o "ciclo padrão" (ex: 1 ano típico) a ser repetido.
    repeticoes = int(anos_para_expandir)
    
    logger.info(f"Base de dados original tem {total_linhas_base} registros.")
    logger.info(f"Expandindo para {anos_para_expandir} anos (Repetindo a base {repeticoes} vezes)...")
    
    # --- 3. Expansão dos Dados (Crescimento 0%) ---
    # tile repete o array 'repeticoes' vezes
    nova_potencia = np.tile(potencia_base, repeticoes)
    
    # --- 4. Reconstrução da Linha do Tempo ---
    # Data inicial
    data_inicio = df[coluna_data][0]
    total_novos_registros = len(nova_potencia)
    
    # Cria um array de deltas de tempo
    # Ex: [0 min, 15 min, 30 min, ...]
    # Multiplicamos o índice pelo delta_t
    indices_tempo = np.arange(total_novos_registros)
    deltas = pd.to_timedelta(indices_tempo * resolucao_minutos, unit='m')
    
    novas_datas = data_inicio + deltas
    
    # --- 5. Criação do DataFrame Expandido ---
    df_expandido = pd.DataFrame({
        'Data_Hora': novas_datas,
        'Potencia': nova_potencia
    })
    
    # --- 6. Adicionar Lógica de "Mês de 30 Dias" ---
    # Quantas linhas correspondem a 1 hora?
    linhas_por_hora = 60 / resolucao_minutos
    
    # Quantas linhas correspondem a 30 dias (720 horas)?
    linhas_por_mes_padrao = linhas_por_hora * 24 * 30
    
    # Cria coluna de mês (1, 1, 1... 2, 2, 2...)
    # Usamos divisão inteira (//) pelo tamanho do bloco do mês
    df_expandido['Mes_Simulacao'] = (df_expandido.index // linhas_por_mes_padrao).astype(int) + 1
    
    # Adiciona também o Ano de Simulação para facilitar
    linhas_por_ano_padrao = linhas_por_mes_padrao * 12 # 360 dias comerciais
    df_expandido['Ano_Simulacao'] = (df_expandido.index // linhas_por_ano_padrao).astype(int) + 1

    logger.info("--- Expansão Concluída ---")
    logger.info(df_expandido.head())
    logger.info("...")
    logger.info(df_expandido.tail())
    
    return df_expandido


def converter_csv_para_mat(csv_path, mat_path, var_name):
    """
    Converte um arquivo CSV específico para o formato .mat do MATLAB.

    O CSV deve ter duas colunas, separadas por ponto e vírgula,
    e usar vírgula como separador decimal.

    Args:
        csv_path (str): Caminho para o arquivo CSV de entrada.
        mat_path (str): Caminho para o arquivo .mat de saída.
        var_name (str): Nome da variável a ser usada no arquivo .mat.
    """
    logger.info(f"Iniciando a conversão de '{csv_path}' para '{mat_path}'...")

    if not os.path.exists(csv_path):
        logger.error(f"Erro: O arquivo de entrada '{csv_path}' não foi encontrado.")
        return

    try:
        # Lê o arquivo CSV usando pandas, especificando delimitador, decimal e a codificação 'utf-8-sig' para ignorar o BOM
        df = pd.read_csv(csv_path, delimiter=';', decimal=',', header=None, encoding='utf-8-sig')

        # Converte o DataFrame para um array NumPy e transpõe para o formato 2xN
        data_array = df.to_numpy().T

        # Salva o array em um arquivo .mat
        scipy.io.savemat(mat_path, {var_name: data_array})

        logger.info(f"Conversão concluída com sucesso! Arquivo '{mat_path}' foi gerado.")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a conversão: {e}")

if __name__ == "__main__":
    converter_csv_para_mat(CSV_FILENAME, MAT_FILENAME, MAT_VARIABLE_NAME)