
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from besx.config import CONFIGURACAO
from besx.infrastructure.logging.logger import logger


def imprimir_histograma(df_rainflow_mes: pd.DataFrame, ano: int, mes: int) -> None:
    """
    Imprime um histograma de contagem de ciclos agrupados por DOD (Range)
    para um mês/ano específico.

    Args:
        df_rainflow_mes (pd.DataFrame): DataFrame com os ciclos rainflow ('Range', 'Count').
        ano (int): O ano sendo processado (para o título).
        mes (int): O mês sendo processado (para o título).
    """
    logger.info(f"--- Histograma de Ciclos do Mes {mes}/{ano} ---")

    if df_rainflow_mes.empty:
        logger.warning("   -> Nenhum ciclo rainflow encontrado para histograma.")
        return

    df_local = df_rainflow_mes.copy()

    # Lê o parâmetro de arredondamento do config
    hist_dp = CONFIGURACAO.modelo_degradacao.ciclo.range_round_dp
    
    df_local['range_rounded'] = df_local['Range'].round(hist_dp)
    
    histograma_df = df_local.groupby('range_rounded')['Count'].sum().reset_index()
    
    for _, linha in histograma_df.iterrows():
        dod = linha['range_rounded']
        contagem = linha['Count']
        logger.info(f"-> Encontrado(s) {contagem} ciclo(s) com DOD de: {dod:.2f}%")

def plotar_capacidade_mensal(df_resultados: pd.DataFrame, nome_arquivo_saida: str) -> None:
    """
    Gera um gráfico da capacidade restante da bateria ao final de cada mês.

    Args:
        df_resultados (pd.DataFrame): DataFrame com os resultados mensais.
                                  Deve conter a coluna 'capacidade_restante'.
        nome_arquivo_saida (str): O nome do arquivo PNG que será salvo.
    """
    logger.info(f"--- Gerando Imagem: {nome_arquivo_saida} ---")

    if df_resultados.empty or 'capacidade_restante' not in df_resultados.columns:
        logger.warning("   -> Nenhum resultado ou coluna 'capacidade_restante' encontrada para plotar.")
        return

    # Lê parâmetros da configuração global
    cfg_sim = CONFIGURACAO.simulacao
    cfg_bat = CONFIGURACAO.bateria
    
    capacidade_inicial = cfg_sim.SOH_INICIAL_PERC
    limite_eol_perc = cfg_bat.capacidade_limite_perda_perc

    # 1. Evita 'Side Effect' - Trabalha em uma cópia
    df_plot = df_resultados.copy()

    # 2. Cria o eixo X sequencial na cópia local
    df_plot['mes'] = range(1, len(df_plot) + 1)

    # 3. Lógica de cálculo redundante foi REMOVIDA.

    # 4. Lê parâmetros de plotagem do config
    figsize = (15, 7) 
    cor = 'darkgreen' 
    dpi = 150 

    # 5. Calcula o limite EOL com base nos parâmetros da simulação
    linha_eol = capacidade_inicial - limite_eol_perc # ex: 100 - 20 = 80
    
    # 6. Lê limites Y do config
    ylim_top = 105
    # Define o limite inferior como 10 abaixo do EOL, ou o mínimo do plot
    ylim_bottom_min = linha_eol - 10
    ylim_bottom = min(ylim_bottom_min, df_plot['capacidade_restante'].min() - 5)
    
    # 7. Lê espaçamento dos Ticks (eixo X) do config
    xticks_step_months = 12 # Pode ser movido para o config se desejar

    # 8. Plota o gráfico de linha
    plt.figure(figsize=figsize)
    plt.plot(df_plot['mes'], df_plot['capacidade_restante'],
             marker='o', linestyle='-', color=cor, label='Capacidade Restante')

    # Usa o parâmetro 'linha_eol' calculado
    plt.axhline(y=linha_eol, color='red', linestyle='--', label=f'Limite Fim de Vida ({linha_eol:.0f}%)')

    # Adiciona títulos e rótulos
    plt.title('Evolução da Capacidade Restante da Bateria (SOH)')
    plt.xlabel('Mês da Simulação (Sequencial)')
    plt.ylabel('Capacidade Restante (%)')
    
    # Usa os limites Y do config
    plt.ylim(bottom=ylim_bottom, top=ylim_top)
    
    # Usa o passo (step) do config
    step = max(1, len(df_plot) // xticks_step_months)
    plt.xticks(np.arange(0, len(df_plot) + 1, step=step))
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    # Usa o DPI do config
    plt.savefig(nome_arquivo_saida, dpi=dpi)
    logger.info("Imagem gerada com sucesso.")


def plotar_composicao_degradacao(df_resultados: pd.DataFrame, nome_arquivo_saida: str) -> None:
    """
    Gera um gráfico de área empilhada mostrando a contribuição
    de Ciclo vs. Calendário na degradação total acumulada.
    """
    # Configuração do gráfico
    plt.figure(figsize=(10, 6))
    dpi = 150 
    meses = df_resultados['mes']
    deg_ciclo = df_resultados['dano_ciclo_acum']
    deg_cal = df_resultados['dano_cal_acum']
    
    # Cria o gráfico de área empilhada
    plt.stackplot(meses, deg_ciclo, deg_cal, 
                  labels=['Degradação por Ciclo', 'Degradação por Calendário'],
                  colors=['#1f77b4', '#ff7f0e'], # Azul e Laranja
                  alpha=0.7)
    
    # Linha do total para destaque
    plt.plot(meses, df_resultados['dano_total_acum'], color='black', linestyle='--', linewidth=1, label='Perda Total Acumulada')

    # Estilização
    plt.title('Composição da Degradação da Bateria (SOH Loss)')
    plt.xlabel('Mês da Simulação')
    plt.ylabel('Perda Acumulada de SOH (%)')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(left=1, right=meses.max())
    plt.ylim(bottom=0)
    
    # Exibe
    plt.tight_layout()
    plt.savefig(nome_arquivo_saida, dpi=dpi)