"""
data_handler.py (O Especialista em Dados)

Responsabilidade: Tudo relacionado à manipulação dos dados de entrada.
Sabe como ler o arquivo .mat, convertê-lo para um DataFrame e fatiá-lo
em pedaços mensais.
"""
from besx.infrastructure.loaders.conversor import converter_csv_para_mat
import pandas as pd
from scipy.io import loadmat
from scipy.signal import find_peaks
import numpy as np
import scipy.io
import os
import math
from besx.infrastructure.logging.logger import logger

# Importa a configuração centralizada
from besx.config import CONFIGURACAO

def data_handle(nome_arquivo=None, meses_alvo=None, file_manager=None):
    """
    Função principal do módulo: orquestra o carregamento e fatiamento dos dados.
    """
    import os

    logger.info("--- Início do Data Handle ---")

    # 1. Selecionar Arquivo (Interação com usuário se não fornecido)
    if nome_arquivo is None:
        nome_arquivo_inicial = selecionar_arquivo_database()
    else:
        nome_arquivo_inicial = nome_arquivo

    if not nome_arquivo_inicial:
        return [] 

    # 2. Identificar e Converter (CSV -> MAT se necessário)
    # Esta função retorna apenas o NOME do arquivo .mat (ex: "arquivo.mat")
    nome_arquivo_mat = identificar_tipo_arquivo(nome_arquivo_inicial)
    
    if not nome_arquivo_mat:
        logger.error("Falha na identificação do arquivo.")
        return []

    from besx.config import PATH_DATABASE
    caminho_completo = os.path.join(PATH_DATABASE, nome_arquivo_mat)
    logger.info(f"Tentando carregar dados de: {caminho_completo}")

    # 3. Carregar arquivo usando o caminho completo
    
    df_completo = carregar_dados_mat(caminho_completo) 

    # --- TRAVA DE SEGURANÇA
    if df_completo is None:
        logger.error(f"Falha ao carregar o arquivo. Verifique se ele existe e é um .mat válido.")
        return []

    logger.info("Dados carregados com sucesso. Iniciando análise...")

    # 4. Analisar Dados
    dt_minutos = analisar_integridade_dados(df_completo)
    
    if dt_minutos is None:
         logger.error("Não foi possível determinar o passo de tempo.")
         return []

    CONFIGURACAO.dados_entrada.dt_minutos = dt_minutos

    # 5. Ajustar Duração (Opcional)
    df_final = ajustar_duracao_dados(df_completo, dt_minutos, meses_alvo=meses_alvo, interativo=(nome_arquivo is None))
    
    # Atualiza anos de simulação no config para os plots
    minutos_totais = len(df_final) * dt_minutos
    anos_simulados = minutos_totais / (360 * 24 * 60)
    CONFIGURACAO.simulacao.ANOS_SIMULACAO = round(anos_simulados, 2)

    # 6. Fatiar em Meses
    lista_meses = fatiar_dados_mensais(df_final) 
    
    return lista_meses



#1 Execução
def selecionar_arquivo_database():
    logger.info("Carregando dados de entrada...")
    from besx.config import PATH_DATABASE
    pasta_database = PATH_DATABASE

    # 1. Verifica se a pasta existe
    if not os.path.exists(pasta_database):
        # Tenta criar a pasta se não existir, para evitar erro na próxima vez
        try:
            os.makedirs(pasta_database)
            logger.warning(f"Aviso: A pasta '{pasta_database}' não existia e foi criada. Coloque seus arquivos nela.")
        except OSError:
            logger.error(f"Erro: A pasta '{pasta_database}' não foi encontrada.")
        return None
    
    # 2. Lista os arquivos (ignorando subpastas e arquivos ocultos como .DS_Store)
    arquivos = [
        f for f in os.listdir(pasta_database) 
        if os.path.isfile(os.path.join(pasta_database, f)) and not f.startswith('.')
    ]

    if not arquivos:
        logger.warning(f"Aviso: A pasta '{pasta_database}' está vazia.")
        return None

    # 3. Exibe as opções
    logger.info(f"--- Arquivos disponíveis em '{pasta_database}/' ---")
    for i, arquivo in enumerate(arquivos):
        logger.info(f"[{i + 1}] {arquivo}")

    # 4. Loop de interação com o usuário
    while True:
        try:
            entrada = input("\nDigite o número do arquivo que deseja analisar: ")
            escolha = int(entrada)
            
            if 1 <= escolha <= len(arquivos):
                arquivo_escolhido = arquivos[escolha - 1]
                logger.info(f"-> Arquivo selecionado: {arquivo_escolhido}")
                
                # Retorna apenas o nome do arquivo (ou o caminho completo se preferir)
                return arquivo_escolhido 
            else:
                logger.warning(f"Opção inválida. Escolha entre 1 e {len(arquivos)}.")
        except ValueError:
            logger.error("Entrada inválida. Por favor, digite um número inteiro.")
#2 Execução


def identificar_tipo_arquivo(nome_arquivo_selecionado):
    """
    Analisa a extensão, converte se necessário e RETORNA o nome do arquivo .mat final.
    """
    nome_base, extensao = os.path.splitext(nome_arquivo_selecionado)
    extensao = extensao.lower()

    # Monta caminhos completos
    from besx.config import PATH_DATABASE
    caminho_origem = os.path.join(PATH_DATABASE, nome_arquivo_selecionado)
    
    # O destino sempre será .mat
    nome_arquivo_mat = f"{nome_base}.mat"
    caminho_destino = os.path.join(PATH_DATABASE, nome_arquivo_mat)

    if extensao == '.mat':
        logger.info(f"-> Arquivo MAT detectado: {nome_arquivo_selecionado}")
        # Atualiza config
        CONFIGURACAO.dados_entrada.ARQUIVO_MAT = nome_arquivo_selecionado
        return nome_arquivo_selecionado

    elif extensao == '.csv':
        logger.info(f"-> Arquivo CSV detectado. Convertendo '{nome_arquivo_selecionado}'...")
        
        # Chama o conversor
        converter_csv_para_mat(caminho_origem, caminho_destino, "ATot")
        
        logger.info(f"-> Conversão concluída. Novo arquivo gerado: {nome_arquivo_mat}")
        
        # Atualiza config para usar o MAT, não o CSV
        CONFIGURACAO.dados_entrada.ARQUIVO_MAT = nome_arquivo_mat
        
        # IMPORTANTE: Retorna o nome do arquivo MAT, não o CSV
        return nome_arquivo_mat

    else:
        logger.error(f"Erro: Extensão '{extensao}' não suportada.")
        return None


#3 Execução
def carregar_dados_mat(filename):
    """
    (Função interna) Carrega um arquivo .mat e o converte para um DataFrame.
    """
    
    try:
        dados_mat = loadmat(filename)
        # Filtra chaves que não começam com __ (metadados do MAT)
        variaveis = [k for k in dados_mat.keys() if not k.startswith('__')]
        
        if not variaveis:
            logger.error(f"O arquivo '{filename}' não contém variáveis válidas.")
            return None
            
        nome_variavel = variaveis[0]
        matriz_dados = dados_mat[nome_variavel]
        df_total = pd.DataFrame(matriz_dados.T, columns=['Tempo', 'Potencia_kW'])     
        logger.info(f"Arquivo '{filename}' carregado. Total de {len(df_total)} linhas.")
        return df_total
    except Exception as e:
        logger.error(f"Erro ao carregar ou converter '{filename}': {e}")
        return None

def analisar_integridade_dados(df):
    """
    Analisa os dados assumindo que a primeira coluna é Tempo (em minutos)
    e a segunda é Potência.
    """
    logger.info("="*40)
    logger.info("RELATÓRIO DE ANÁLISE DOS DADOS")
    logger.info("="*40)
    
    col_tempo = df.columns[0]
    col_valor = df.columns[1]

    # --- 1. Tempo de Amostra (dt) ---
    # Verifica se a coluna é numérica
    if pd.api.types.is_numeric_dtype(df[col_tempo]):
        # Calcula a diferença entre passos (ex: 5 - 0 = 5)
        deltas = df[col_tempo].diff().dropna()
        
        # Pega o valor mais comum (moda)
        dt_minutos = deltas.mode()[0]
        
        logger.info(f"1. Tempo de Amostra Detectado: {dt_minutos} minutos")
        
        # Verifica constância
        is_constant = np.allclose(deltas, dt_minutos, atol=1e-5)
        if not is_constant:
            logger.warning(f"   [ALERTA] Passo de tempo varia! (Jitter ou buracos nos dados)")
            logger.warning(f"   Variação: Min={deltas.min()}, Max={deltas.max()}")
        else:
            logger.info(f"   [OK] O passo de tempo é constante.")
            
        # --- 2. Quantidade de Meses ---
        tempo_inicial = df[col_tempo].min()
        tempo_final = df[col_tempo].max()
        duracao_minutos = tempo_final - tempo_inicial
        
        # Conversão: 1 mês = 30 dias * 24h * 60min = 43.200 minutos
        minutos_em_um_mes = 30 * 24 * 60
        meses_totais = duracao_minutos / minutos_em_um_mes
        
        logger.info(f"2. Cobertura Temporal:")
        logger.info(f"   Início: {tempo_inicial} min")
        logger.info(f"   Fim:    {tempo_final} min")
        logger.info(f"   Duração Total: {duracao_minutos:.0f} minutos")
        logger.info(f"   Meses Completos (base 30 dias): {meses_totais:.2f} meses")
        
    else:
        logger.error("Erro: A coluna de tempo não é numérica. Verifique o formato do arquivo.")
        return None

    # --- 3. Verificação de Nulos ---
    nulos = df[col_valor].isna().sum()
    if nulos > 0:
        logger.warning(f"3. [PERIGO] Valores Nulos (NaN) detectados: {nulos}")
    else:
        logger.info(f"3. [OK] Nenhum valor nulo detectado.")

    # --- 4. Estatísticas de Valor ---
    max_val = df[col_valor].max()
    min_val = df[col_valor].min()
    mean_val = df[col_valor].mean()
    
    logger.info(f"4. Estatísticas de Valor ({col_valor}):")
    logger.info(f"   Máximo: {max_val:.2f}")
    logger.info(f"   Mínimo: {min_val:.2f}")
    logger.info(f"   Média:  {mean_val:.2f}")

    logger.info("="*40)
    
    return dt_minutos

def ajustar_duracao_dados(df, dt_minutos, meses_alvo=None, interativo=True):
    """
    Expande ou corta os dados.
    Baseia-se em meses padronizados de 30 dias.
    """
    col_tempo = df.columns[0]
    col_valor = df.columns[1] # Potência
    
    # Cálculos de base
    total_linhas_atual = len(df)
    minutos_por_mes = 30 * 24 * 60 # 43.200 minutos
    linhas_por_mes = minutos_por_mes / dt_minutos
    
    meses_atuais = total_linhas_atual / linhas_por_mes
    
    logger.info("--- Ajuste de Duração da Simulação ---")
    logger.info(f"Dados carregados: {meses_atuais:.1f} meses ({total_linhas_atual} amostras).")
    
    if interativo:
        entrada = input(f"Digite a quantidade de meses desejada (ou Enter para manter {meses_atuais:.1f}): ").strip()
        if not entrada:
            logger.info("-> Mantendo duração original.")
            return df
        try:
            meses_finais = float(entrada)
        except ValueError:
            logger.warning("-> Entrada inválida. Mantendo duração original.")
            return df
    else:
        # Modo não-interativo (ex: dashboard)
        if meses_alvo is not None:
            meses_finais = meses_alvo
        else:
            logger.info("-> Mantendo duração original.")
            return df

    # Calcula quantas linhas precisamos no total
    linhas_alvo = int(meses_finais * linhas_por_mes)
    
    if linhas_alvo == total_linhas_atual:
        logger.info("-> Duração inalterada.")
        return df

    # CENÁRIO 1: CORTAR (LIMITAR)
    if linhas_alvo < total_linhas_atual:
        logger.info(f"-> Reduzindo dados para {meses_finais} meses...")
        df_novo = df.iloc[:linhas_alvo].copy()
        return df_novo

    # CENÁRIO 2: EXPANDIR (REPETIR)
    if linhas_alvo > total_linhas_atual:
        logger.info(f"-> Expandindo dados para {meses_finais} meses (Repetição cíclica)...")
        
        # 1. Repetir os valores de potência
        # Calculamos quantas cópias inteiras precisamos + sobra
        repeticoes = math.ceil(linhas_alvo / total_linhas_atual)
        
        # Repete o array de potência
        valores_potencia = df[col_valor].values
        novo_array_potencia = np.tile(valores_potencia, repeticoes)
        
        # Corta o excesso para ficar exato
        novo_array_potencia = novo_array_potencia[:linhas_alvo]
        
        # 2. Reconstruir o vetor de Tempo (Fundamental!)
        # O tempo deve continuar crescendo: 0, 5, 10, ..., N
        tempo_inicial = df[col_tempo].iloc[0]
        novo_array_tempo = np.arange(0, linhas_alvo) * dt_minutos + tempo_inicial
        
        # 3. Montar novo DataFrame
        df_novo = pd.DataFrame({
            col_tempo: novo_array_tempo,
            col_valor: novo_array_potencia
        })
        
        return df_novo



def fatiar_dados_mensais(df):
    """
    Divide o DataFrame em uma lista de DataFrames mensais.
    Considera um mês padrão de 30 dias.
    """
    logger.info("Fatiando dados em meses...")
    
    # Busca a configuração de tempo (dt) no objeto central
    dt_minutos = CONFIGURACAO.dados_entrada.dt_minutos
    dias_mes = CONFIGURACAO.dados_entrada.dias_por_mes_sim
    
    # 1 mês = dias_mes * 24 horas * 60 minutos
    minutos_por_mes = dias_mes * 24 * 60
    amostras_por_mes = int(minutos_por_mes / dt_minutos)
    
    lista_meses = []
    total_linhas = len(df)
    
    for i in range(0, total_linhas, amostras_por_mes):
        df_mes = df.iloc[i : i + amostras_por_mes].copy()
        
        # Reseta o tempo para começar em 0 em cada mês
        df_mes['Tempo'] = df_mes['Tempo'] - df_mes['Tempo'].iloc[0]
        
        # Validação: só adiciona se tiver um volume mínimo de dados (ex: > 20% do mês)
        if len(df_mes) > (amostras_por_mes * 0.2):
            lista_meses.append(df_mes)
            
    logger.info(f"Fatiamento concluído: {len(lista_meses)} meses gerados.")
    return lista_meses
