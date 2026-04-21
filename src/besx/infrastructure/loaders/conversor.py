import pandas as pd
import os
from besx.infrastructure.logging.logger import logger

def converter_csv_para_pkl(csv_path: str, pkl_path: str) -> None:
    """
    Converte um arquivo CSV específico para o formato Pickle (.pkl) otimizado.
    O CSV deve ter duas colunas (Tempo; Potencia ou similar), separadas por ';' 
    e com vírgula como decimal (padrão Excel BR).
    """
    logger.info(f"Convertendo '{csv_path}' para Pickle nativo '{pkl_path}'...")
    if not os.path.exists(csv_path):
        logger.error(f"Erro: Arquivo '{csv_path}' não encontrado.")
        return
    try:
        # Lê o CSV com padrões comuns brasileiros
        df = pd.read_csv(csv_path, delimiter=';', decimal=',', header=None, encoding='utf-8-sig')
        # Padroniza nomes para o motor BESx
        df.columns = ['Tempo', 'Potencia_kW']
        # Salva em Pickle (muito mais rápido que .mat para leitura no pandas)
        df.to_pickle(pkl_path)
        logger.info(f"Conversão Pickle concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro na conversão Pickle: {e}")