
"""
Created on Fri Oct  3 08:47:58 2025

@author: Vitor Silva
@Universidade Federal do Recôncavo da Bahia
@Company: LEDAX
"""
import matplotlib.pyplot as plt
import math
import pandas as pd
import numpy as np
import rainflow
import datetime
from scipy.signal import find_peaks
from IPython.display import display
import xmlrpc.client
from scipy.io import loadmat

#################################

# 1. Carregar os dados do Atot.mat
# 2. Traduzir 'df_mes_potencia' (min->seg, DataFrame->Matriz)
# 3. Enviar dados ao PLECS (dados do primeiro mês: set SOH, set Potência)
# 4. Rodar PLECS (simulate)
# 5. Receber SOC do PLECS (get SOC)
# 6. Traduzir SOC (Resultado PLECS -> Série alinhada com o tempo)
# 7. Calcular danos (dano_ciclo, dano_calendar)
# 8. Acumular danos (acum_ciclo_global, acum_cal_global)
# 9. Envia novamente os dados do segundo mês e o novo SOH





def acumular_dano(Ccal_total_mes, acum_cal_global, exp_tempo):
    """
    Acumula o dano de acordo com a exponencial.
    """
    return (Ccal_total_mes**exp_tempo + acum_cal_global**exp_tempo)**(1/exp_tempo)

def dano_ciclo (lista_rainflow_mes, Temp_kelvin,config_modelo_ciclo):
    """
    Calcula o dano total por ciclos (%) para o mês, agrupando primeiro
    e depois calculando o dano para cada grupo.
    Args:
        lista_rainflow_mes (list): Lista de ciclos do rainflow.
        Temp_kelvin (float): Temperatura da bateria.
        config_modelo_ciclo (dict): Dicionário contendo as constantes do modelo
                                    de ciclo (a, b, c, d, g, h) e parâmetros
                                    de arredondamento (range_round_dp, mean_round_dp).
    """
    
    if not lista_rainflow_mes:
        # print("   -> Nenhum ciclo rainflow encontrado.") # Movido para o loop principal
        return 0.0

    df_rainflow = pd.DataFrame(lista_rainflow_mes,
                               columns = ["Range", "Mean", "Count", "Start", "End"])
    # --- INÍCIO DO DEBUG ---
    if df_rainflow['Range'].dtype == 'object':
        print("\n--- DEBUG: DETECTADO DTYPE 'OBJECT' NA COLUNA 'RANGE' ---")
        print("Tipos de dados (dtypes) atuais do df_rainflow:")
        print(df_rainflow.dtypes)
        print("\nAmostra de valores não numéricos na coluna 'Range':")
        # Esta linha mostrará os valores que não são números
        print(df_rainflow[pd.to_numeric(df_rainflow['Range'], errors='coerce').isna()]['Range'].unique())
    # --- FIM DO DEBUG ---
    range_dp = config_modelo_ciclo.get('range_round_dp', 1)
    mean_dp = config_modelo_ciclo.get('mean_round_dp', 1)

    df_rainflow['Range'] = pd.to_numeric(df_rainflow['Range'], errors='coerce')
    df_rainflow['range_rounded'] = df_rainflow['Range'].round(range_dp)

    df_rainflow['Mean'] = pd.to_numeric(df_rainflow['Mean'], errors='coerce')
    df_rainflow['mean_rounded'] = df_rainflow['Mean'].round(mean_dp)

    histograma = df_rainflow.groupby(['range_rounded', 'mean_rounded']).agg(
        contagem_grupo=('Count', 'sum')
    ).reset_index()

    soma_dos_quadrados_mes = 0.0

    # 2. Itera sobre o HISTOGRAMA
    for index, info_grupo in histograma.iterrows():
        dod_representativo = info_grupo['range_rounded']
        soc_medio_representativo = info_grupo['mean_rounded']
        nc_grupo = info_grupo['contagem_grupo']

        # 3. Calcula o dano unitário (Passa o config)
        dano_unitario = calcular_dano_ciclo_unitario(dod_representativo,
                                                    soc_medio_representativo,
                                                    Temp_kelvin,
                                                    config_modelo_ciclo) # Repassa o config

        # 4. Calcula o dano do grupo aplicando nc^0.5
        dano_do_grupo = dano_unitario * (nc_grupo**0.5)

        # 5. Acumula quadraticamente
        soma_dos_quadrados_mes += dano_do_grupo**2

    # 6. Retorna o total do mês
    Ccyc_total_mes = np.sqrt(soma_dos_quadrados_mes)
    return Ccyc_total_mes
  
def calcular_dano_ciclo_unitario(dod_percent, soc_medio_percent, Tbat_kelvin, config_ciclo):
    """
    Calcula o dano unitário (para um único ciclo) com base nos parâmetros
    físicos fornecidos no dicionário de configuração.

    Args:
        dod_percent (float): Profundidade de descarga (Range).
        soc_medio_percent (float): Estado de carga médio.
        Tbat_kelvin (float): Temperatura da bateria.
        config_ciclo (dict): Dicionário com as constantes (a, b, c, d, g, h).
    """
    # Desempacota os parâmetros físicos do dicionário de configuração
    try:
        a = config_ciclo['a']
        b = config_ciclo['b']
        c = config_ciclo['c']
        d = config_ciclo['d']
        g = config_ciclo['g']
        h = config_ciclo['h']
    except KeyError as e:
        raise KeyError(f"Erro: A configuração do modelo de ciclo não contém a chave {e}. Verifique o dicionário CONFIGURACAO.")

    # O restante da lógica de cálculo permanece o mesmo
    CFade_soc = a * np.exp(b * soc_medio_percent)
    CFade_temp = c * np.exp(d * Tbat_kelvin)
    CFade_depth = g * (dod_percent**h) if dod_percent > 0 else 0
    
    return CFade_depth * CFade_soc * CFade_temp

def dano_calendar(lista_periodos_idle, Tbat_kelvin, config_modelo_calendario):
    """
    Calcula o dano total por calendário (%) para o mês.

    Args:
        lista_periodos_idle (list): Lista de dicionários de períodos 'idle'.
        Tbat_kelvin (float): Temperatura da bateria.
        config_modelo_calendario (dict): Dicionário com as constantes do modelo
                                         de calendário (k_T, exp_T, etc.).
    """
    Ccal_total_mes = 0.0
    if lista_periodos_idle:
        # 1. Passa o config para a função filha
        lista_danos_calendar_individuais_mes = calcular_lista_danos_calendario(
            lista_periodos_idle, 
            Tbat_kelvin,
            config_modelo_calendario # Repassa o config
        )

        # 2. Lê os expoentes do config
        try:
            exp_tempo = config_modelo_calendario['exp_cal']
            inv_exp_tempo = 1/exp_tempo
        except KeyError as e:
            raise KeyError(f"Erro: A configuração do modelo de calendário não contém a chave {e}.")

        # 3. Acumula não-linearmente usando os expoentes do config
        soma_termos_cal_mes = sum(d**exp_tempo for d in lista_danos_calendar_individuais_mes if d > 0)
        Ccal_total_mes = soma_termos_cal_mes**inv_exp_tempo
        
        return Ccal_total_mes
    else:
        # 4. Remove o 'print'
        return 0.0

def calcular_lista_danos_calendario(lista_periodos_idle, Tbat_kelvin, config_calendario):
    """
    Calcula o dano individual para CADA período idle na lista de entrada.

    Args:
        lista_periodos_idle (list): Lista de dicionários ('SOC', 't_meses').
        Tbat_kelvin (float): Temperatura da bateria em Kelvin.
        config_calendario (dict): Dicionário com as constantes do modelo
                                  (k_T, exp_T, k_soc, exp_soc, exp_tempo).
    """
    if not lista_periodos_idle:
        return []

    # Desempacota os parâmetros físicos do dicionário de configuração
    try:
        k_T = config_calendario['k_T']
        exp_T = config_calendario['exp_T']
        k_soc = config_calendario['k_soc']
        exp_soc = config_calendario['exp_soc']
        exp_tempo = 1/config_calendario['exp_cal'] # Usado para Ccal_time
    except KeyError as e:
        raise KeyError(f"Erro: A configuração do modelo de calendário não contém a chave {e}. Verifique o dicionário CONFIGURACAO.")

    lista_danos_individuais = []

    # Itera sobre cada período parado
    for periodo in lista_periodos_idle:
        soc_percent = periodo['SOC']
        t_meses = periodo['t_meses']

        # Calcula os fatores de dano para este período
        CCal_temperature = k_T * np.exp(exp_T * Tbat_kelvin)
        Ccal_soc = k_soc * np.exp(exp_soc * soc_percent)
        Ccal_time = t_meses**exp_tempo # Usa o exp_tempo do config

        # Calcula o dano APENAS deste período parado
        dano_periodo = CCal_temperature * Ccal_soc * Ccal_time

        # Adiciona o dano à lista
        lista_danos_individuais.append(dano_periodo)

    return lista_danos_individuais

def imprimir_histograma(df_rainflow_mes, ano, mes, config_histograma):
    """
    Imprime um histograma de contagem de ciclos agrupados por DOD (Range)
    para um mês/ano específico.

    Args:
        df_rainflow_mes (pd.DataFrame): DataFrame com os ciclos rainflow ('Range', 'Count').
        ano (int): O ano sendo processado (para o título).
        mes (int): O mês sendo processado (para o título).
        config_histograma (dict): Dicionário contendo 'hist_round_dp' 
                                  para o arredondamento do DOD.
    """
    # 1. Título impresso com 'ano' e 'mes' recebidos como argumento
    print(f"\n--- Histograma de Ciclos do Mes {mes}/{ano} ---")

    if df_rainflow_mes.empty:
        print("   -> Nenhum ciclo rainflow encontrado para histograma.")
        return

    # 2. Evita 'Side Effect' trabalhando em uma cópia do DataFrame
    df_local = df_rainflow_mes.copy()

    # 3. Lê o parâmetro de arredondamento do config (usa 0 como padrão)
    hist_dp = config_histograma.get('hist_round_dp', 0)
    
    df_local['range_rounded'] = df_local['Range'].round(hist_dp)
    
    histograma_df = df_local.groupby('range_rounded')['Count'].sum().reset_index()
    
    for _, linha in histograma_df.iterrows():
        dod = linha['range_rounded']
        contagem = linha['Count']
        print(f"-> Encontrado(s) {contagem} ciclo(s) com DOD de: {dod:.2f}%")

def ciclos_idle(profile, dt_minutos, dias_por_ano_avg):
    """
    Encontra períodos 'idle' (SOC constante) em um perfil de SOC.

    Args:
        profile (list): Lista do perfil de SOC.
        dt_minutos (float): O intervalo de tempo (delta t) entre 
                            amostras no perfil, em minutos.
        dias_por_ano_avg (float): Número médio de dias por ano 
                                  (ex: 365.25) para cálculo do mês.
    """
    cont = 0
    idle_cycles = []
    
    # Calcula o número médio de minutos em um mês com base nos parâmetros
    minutos_por_mes = (dias_por_ano_avg * 24 * 60) / 12

    for i in range(len(profile)-1):
        if profile[i] == profile[i+1]:
            cont += 1
        else:
            if cont > 0:
                # O período 'cont+1' inclui a amostra atual e as anteriores
                num_amostras_idle = cont + 1
                tempo_total_minutos = num_amostras_idle * dt_minutos
                
                data = {
                    't': num_amostras_idle, # Duração em amostras
                    't_meses': tempo_total_minutos / minutos_por_mes, # Duração em meses
                    'SOC': profile[i], # O SOC constante do período
                    'index': i # O índice onde o período terminou
                }
                idle_cycles.append(data)
            cont = 0
            
    # --- Correção de Bug ---
    # Verifica se o perfil terminou em um período idle
    if cont > 0:
        num_amostras_idle = cont + 1
        tempo_total_minutos = num_amostras_idle * dt_minutos
        data = {
            't': num_amostras_idle,
            't_meses': tempo_total_minutos / minutos_por_mes,
            'SOC': profile[len(profile)-1], # Pega o último SOC
            'index': len(profile)-1 # O índice final
        }
        idle_cycles.append(data)
            
    return idle_cycles

def carregar_dados(filename, novos_nomes_colunas):
    """
    Carrega os dados do arquivo CSV, renomeia as colunas e trata erros.

    Args:
        filename (str): O caminho para o arquivo CSV.
        novos_nomes_colunas (list): A lista de nomes de colunas esperada.
    
    Returns:
        pd.DataFrame: O DataFrame carregado e renomeado.
        
    Raises:
        FileNotFoundError: Se o arquivo CSV não for encontrado.
        ValueError: Se o número de colunas no CSV não corresponder
                    ao número de nomes de colunas esperado.
    """
    try:
        df = pd.read_csv(filename)
        # 1. Usa a variável 'filename' no print
        print(f"Arquivo '{filename}' carregado com sucesso.")
    except FileNotFoundError:
        # 3. Lança a exceção em vez de 'exit()'
        raise FileNotFoundError(f"ERRO: O arquivo de dados '{filename}' não foi encontrado.")
    
    # 2. 'novos_nomes_colunas' agora é recebido como argumento

    if len(df.columns) == len(novos_nomes_colunas):
        df.columns = novos_nomes_colunas
    else:
        # 3. Lança a exceção em vez de 'exit()'
        raise ValueError(
            f"\nERRO: O arquivo CSV '{filename}' tem {len(df.columns)} colunas, "
            f"mas foram fornecidos {len(novos_nomes_colunas)} nomes. Verifique o arquivo."
        )

    return df

def add_timestamp_and_month(df, start_date):
    start_data = pd.to_datetime(start_date)
    deltas_de_tempo = pd.to_timedelta(df['Tempo_min'], unit='m')
    df['Timestamp'] = start_data + deltas_de_tempo
    df['Mes'] = df['Timestamp'].dt.month
    df['Ano'] = df['Timestamp'].dt.year
    print("\nDataFrame atualizado com colunas 'Timestamp' e 'Mes' real.")
    return df

def picos_e_vales(profile_series, config_modelo_ciclo):
    """
    Extrai picos e vales de uma Série de SOC, incluindo início e fim,
    usando a proeminência definida na configuração.

    Args:
        profile_series (pd.Series): Série de SOC com índice original.
        config_modelo_ciclo (dict): Dicionário contendo a configuração
                                    'peak_prominence'.
    """
    profile_array = profile_series.to_numpy()

    # 1. Lê a proeminência do dicionário de configuração
    prominence_val = config_modelo_ciclo.get('peak_prominence', 1)

    # 2. Usa o valor de proeminência do config
    picos, _ = find_peaks(profile_array, prominence=prominence_val)
    vales, _ = find_peaks(-profile_array, prominence=prominence_val)

    # Usa os ÍNDICES da Série original
    indices_combinados = np.concatenate((
        [profile_series.index[0]],
        profile_series.index[picos],
        profile_series.index[vales],
        [profile_series.index[-1]]
    ))
    indices_ordenados = np.sort(np.unique(indices_combinados))

    soc_profile_simp = profile_series.loc[indices_ordenados].to_numpy()
    return soc_profile_simp

def multiplicar_dados(df, anos, dt, dias_por_ano_avg):
    """
    Replica o DataFrame de dados base para cobrir o número desejado de anos.

    Args:
        df (pd.DataFrame): O DataFrame base (geralmente 1 ano de dados).
        anos (int): O número total de anos de simulação desejado.
        dt (float): O intervalo de tempo (delta t) das amostras, em minutos.
        dias_por_ano_avg (float): Número médio de dias por ano (ex: 365.25).
    """
    
    num_pontos_base = len(df)
    duracao_base_minutos = num_pontos_base * dt
    
    # 1. Verifica se a base de dados não está vazia para evitar divisão por zero
    if duracao_base_minutos == 0:
        print("ERRO: DataFrame de dados base está vazio. Não é possível multiplicar.")
        return pd.DataFrame() # Retorna DataFrame vazio

    # 2. Usa o parâmetro 'dias_por_ano_avg'
    minutos_totais_desejados = anos * dias_por_ano_avg * 24 * 60
    
    num_repeticoes = math.ceil(minutos_totais_desejados / duracao_base_minutos)
    
    # Garante que num_repeticoes seja int para pd.concat
    df_replicado = pd.concat([df] * int(num_repeticoes), ignore_index=True)

    tempo_continuo = np.arange(0, len(df_replicado) * dt, dt)
    df_replicado['Tempo_min'] = tempo_continuo[:len(df_replicado)]

    max_tempo_minutos = int(minutos_totais_desejados)
    df_extended = df_replicado[df_replicado['Tempo_min'] < max_tempo_minutos].copy()

    return df_extended

def plotar_capacidade_mensal(df_resultados, capacidade_inicial, limite_eol_perc, 
                             nome_arquivo_saida, config_plot):
    """
    Gera um gráfico da capacidade restante da bateria ao final de cada mês.

    Args:
        df_resultados (pd.DataFrame): DataFrame com os resultados mensais.
                                  Deve conter a coluna 'capacidade_restante'.
        capacidade_inicial (float): A capacidade inicial da bateria em %.
        limite_eol_perc (float): O percentual de perda de capacidade que
                                 define o EOL (ex: 20.0).
        nome_arquivo_saida (str): O nome do arquivo PNG que será salvo.
        config_plot (dict): Dicionário com parâmetros de plotagem
                            (figsize, dpi, cor, ylim_top, etc.).
    """
    print(f"\n--- Gerando Imagem: {nome_arquivo_saida} ---")

    if df_resultados.empty or 'capacidade_restante' not in df_resultados.columns:
        print("   -> Nenhum resultado ou coluna 'capacidade_restante' encontrada para plotar.")
        return

    # 1. Evita 'Side Effect' - Trabalha em uma cópia
    df_plot = df_resultados.copy()

    # 2. Cria o eixo X sequencial na cópia local
    df_plot['mes_sequencial'] = range(1, len(df_plot) + 1)

    # 3. Lógica de cálculo redundante foi REMOVIDA.

    # 4. Lê parâmetros de plotagem do config
    figsize = config_plot.get('mensal_figsize', (15, 7))
    cor = config_plot.get('mensal_cor', 'darkgreen')
    dpi = config_plot.get('dpi', 150)
    
    # 5. Calcula o limite EOL com base nos parâmetros da simulação
    linha_eol = capacidade_inicial - limite_eol_perc # ex: 100 - 20 = 80
    
    # 6. Lê limites Y do config
    ylim_top = config_plot.get('ylim_top', 101)
    # Define o limite inferior como 10 abaixo do EOL, ou o mínimo do plot
    ylim_bottom_min = config_plot.get('ylim_bottom_min_eol', linha_eol - 10) # ex: 70
    ylim_bottom = min(ylim_bottom_min, df_plot['capacidade_restante'].min() - 5)
    
    # 7. Lê espaçamento dos Ticks (eixo X) do config
    xticks_step_months = config_plot.get('xticks_step_months', 12)

    # 8. Plota o gráfico de linha
    plt.figure(figsize=figsize)
    plt.plot(df_plot['mes_sequencial'], df_plot['capacidade_restante'],
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
    plt.show()
    print("Imagem gerada com sucesso.")

def plotar_capacidade_anual(df_resultados, capacidade_inicial, limite_eol_perc,
                            nome_arquivo_saida, config_plot):
    """
    Gera um gráfico de LINHA da capacidade restante da bateria ao final
    de cada ANO simulado.

    Args:
        df_resultados (pd.DataFrame): DataFrame com os resultados mensais.
                                  Deve conter colunas 'ano', 'mes',
                                  e 'capacidade_restante'.
        capacidade_inicial (float): A capacidade inicial da bateria em %.
        limite_eol_perc (float): O percentual de perda de capacidade que
                                 define o EOL (ex: 20.0).
        nome_arquivo_saida (str): O nome do arquivo PNG que será salvo.
        config_plot (dict): Dicionário com parâmetros de plotagem
                            (figsize, dpi, cor, marker, etc.).
    """
    print(f"\n--- Gerando Imagem : {nome_arquivo_saida} ---")

    if df_resultados.empty or 'capacidade_restante' not in df_resultados.columns:
        print("   -> Nenhum resultado ou coluna 'capacidade_restante' encontrada para plotar.")
        return

    # 1. Evita 'Side Effect' - Trabalha em uma cópia
    df_plot = df_resultados.copy()

    # 2. Lógica redundante removida.
    
    # 3. Aplica o clip (se necessário) na cópia local
    df_plot['capacidade_restante'] = df_plot['capacidade_restante'].clip(lower=0)
    
    # 4. Filtra para obter o último registro de cada ano (na cópia)
    df_anual = df_plot.groupby('ano').last().reset_index()

    # --- AJUSTE: Adiciona o ponto inicial (Ano 0 ou Ano Inicial - 1) ---
    primeiro_ano = df_anual['ano'].min()
    df_inicial = pd.DataFrame({
        'ano': [primeiro_ano - 1],
        'capacidade_restante': [capacidade_inicial] # Usa o parâmetro
    })
    df_plotar = pd.concat([df_inicial, df_anual[['ano', 'capacidade_restante']]], ignore_index=True)
    df_plotar = df_plotar.sort_values(by='ano')

    # 5. Lê parâmetros de plotagem do config
    figsize = config_plot.get('anual_figsize', (12, 7))
    cor = config_plot.get('anual_cor', 'darkred')
    marker = config_plot.get('anual_marker', 's')
    markersize = config_plot.get('anual_markersize', 8)
    dpi = config_plot.get('dpi', 150)
    
    # Parâmetros de anotação de texto
    text_offset = config_plot.get('anual_text_offset', 0.5)
    text_fontsize = config_plot.get('anual_text_fontsize', 9)
    text_color = config_plot.get('anual_text_color', 'black')
    text_format = config_plot.get('anual_text_format', "{:.2f}%")

    # 6. Calcula o limite EOL com base nos parâmetros da simulação
    linha_eol = capacidade_inicial - limite_eol_perc # ex: 100 - 20 = 80
    
    # 7. Lê limites Y do config
    ylim_top = config_plot.get('ylim_top', 105) # Reutiliza o ylim_top
    ylim_bottom_min = config_plot.get('ylim_bottom_min_eol', linha_eol - 10) # ex: 70
    ylim_bottom = min(ylim_bottom_min, df_plotar['capacidade_restante'].min() - 5)

    # 8. Plota o gráfico de LINHA
    plt.figure(figsize=figsize)
    plt.plot(df_plotar['ano'], df_plotar['capacidade_restante'],
             marker=marker,
             markersize=markersize,
             linestyle='-',
             color=cor,
             label='Capacidade Fim de Ano')

    # Adiciona os valores (texto) em cada ponto
    for index, row in df_plotar.iterrows():
        plt.text(row['ano'], row['capacidade_restante'] + text_offset,
                 text_format.format(row['capacidade_restante']),
                 ha='center',
                 color=text_color,
                 fontsize=text_fontsize)

    # Adiciona a linha de EOL (calculada)
    plt.axhline(y=linha_eol, color='red', linestyle='--', label=f'Limite Fim de Vida ({linha_eol:.0f}%)')

    # Adiciona títulos e rótulos
    plt.title('Evolução Anual da Capacidade Restante da Bateria (SOH)')
    plt.xlabel('Ano da Simulação')
    plt.ylabel('Capacidade Restante (%)')
    
    # Usa os limites Y do config
    plt.ylim(bottom=ylim_bottom, top=ylim_top)
    
    plt.xticks(df_plotar['ano'].astype(int))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    
    # Usa o DPI do config
    plt.savefig(nome_arquivo_saida, dpi=dpi)
    plt.show()
    print("Imagem gerada com sucesso.")

def simular_degradacao_bateria(config):
    """
    Executa a simulação de degradação da bateria com base 
    no dicionário de configuração fornecido.
    """
    
    # --- Desempacota parâmetros do dicionário ---
    cfg_sim = config["simulacao"]
    cfg_arq = config["arquivos"]
    cfg_bat = config["bateria"]
    cfg_mod_cal = config["modelo_fisico"]["calendario"]
    cfg_mod_ciclo = config["modelo_fisico"]["ciclo"]
    cfg_entrada = config["config_dados_entrada"]

    # Parâmetros de simulação
    tempo_simulacao_anos = cfg_sim["tempo_simulacao_anos"]
    dt_minutos = cfg_sim["dt_minutos"]
    data_inicio_simulacao = cfg_sim["data_inicio_simulacao"]
    num_meses_base = cfg_entrada["meses_por_ano_sim"]
    
    # Parametros da Bateria
    Tbat_kelvin = cfg_bat["Tbat_kelvin"]
    capacidade_inicial = cfg_bat["capacidade_inicial_perc"]
    capacidade_limite_perda = cfg_bat["capacidade_limite_perda_perc"]
    
    # Parâmetros dos modelos de degradação
    exp_cyc = cfg_mod_ciclo["exp_cycle"]
    exp_cal = cfg_mod_cal["exp_cal"]
    
    # Parâmetros de plotagem
    cfg_plot = config["config_plot"] 

    simulacao_terminada = False
    resultados_mensais = []
    acum_ciclo_global = 0.0
    acum_cal_global = 0.0

    # ===================================================================
    # PARTE 1 - RECEBER OS DADOS DE ENTRADA 
    # ===================================================================
    lista_perfis_base_mensais = carregar_e_fatiar_dados_entrada(
        cfg_arq["arquivo_entrada_mat"],
        cfg_entrada
    )
    if not lista_perfis_base_mensais:
        print("Falha ao carregar dados de entrada. Abortando.")
        return
    


    df_stamped = add_timestamp_and_month(df_simulacao, data_inicio_simulacao)
    anos = sorted(df_stamped['Ano'].unique())

    # ===================================================================
    # PARTE 2 REVISADA: CÁLCULO MENSAL COM ACUMULAÇÃO EFETIVA
    # ===================================================================

    for ano in anos:
        df_ano_atual = df_stamped[df_stamped['Ano'] == ano]
        meses_no_ano = sorted(df_ano_atual['Mes'].unique()) 

        for mes in meses_no_ano:
            df_mes = df_ano_atual[df_ano_atual['Mes'] == mes].copy()
            if df_mes.empty:
                continue
            
            soc_profile_picos_vales = picos_e_vales(df_mes['SOC'], cfg_mod_ciclo)
            rainflow_mes = rainflow.extract_cycles(soc_profile_picos_vales)
            
            # Passa o dt_minutos e dias_por_ano_avg para ciclos_idle
            idle_cycles_mes = ciclos_idle(
                df_mes['SOC'].round(1).tolist(),
                dt_minutos,
                cfg_sim["dias_por_ano_avg"]
            )

            # Passa os dicionários de modelo físico para as funções de dano
            Ccyc_total_mes = dano_ciclo(
                rainflow_mes, 
                Tbat_kelvin, 
                cfg_mod_ciclo # Passa o dicionário de ciclo
            )  
            acum_ciclo_global = acumular_dano(
                Ccyc_total_mes, 
                acum_ciclo_global, 
                2)
            
            Ccal_total_mes = dano_calendar(
                idle_cycles_mes, 
                Tbat_kelvin,
                cfg_mod_cal # Passa o dicionário de calendário
            )
            
            acum_cal_global = acumular_dano(
                Ccal_total_mes, 
                acum_cal_global, 
                exp_cal, 
            )
            dano_total_acumulado_fim_mes = acum_cal_global + acum_ciclo_global
            capacidade_restante = capacidade_inicial - dano_total_acumulado_fim_mes

            resultados_mensais.append({
                'ano': ano,
                'mes': mes,
                'dano_ciclos_mes': Ccyc_total_mes,                  # Dano causado por ciclos no mês
                'dano_cal_mes': Ccal_total_mes,                     # Dano causado por calendário no mês
                'dano_ciclo_acum': acum_ciclo_global,               # Dano ACUMULADO de ciclos até fim do mês
                'dano_cal_acum': acum_cal_global,                   # Dano ACUMULADO de calendário até fim do mês
                'dano_total_acum': dano_total_acumulado_fim_mes,    # Dano TOTAL acumulado até fim do mês
                'capacidade_restante': capacidade_restante
            })
            ultimo_resultado = resultados_mensais[-1]
            #######print(f"-> Capacidade Restante ao final do Mês {mes}/{ano}: {capacidade_restante:.4f}%")       
            if dano_total_acumulado_fim_mes >= capacidade_limite_perda:
                print(f"\n!!! ATENÇÃO: Limite de {capacidade_limite_perda}% de perda de capacidade atingido no Mês {mes}/{ano}. !!!")
                
                print("--- SIMULAÇÃO INTERROMPIDA ---")
                simulacao_terminada = True
                break # Sai do loop interno (meses)

        # --- NOVO: Verifica se precisa sair do loop externo (anos) ---
        if simulacao_terminada:
            break # Sai do loop externo (anos)
      
    # --- PARTE 3: RESULTADOS FINAIS CONSOLIDADOS ---
    df_resultados_finais = pd.DataFrame(resultados_mensais)
    print("\n--- Resultado Final Consolidado (Estimativa Mensal Acumulada) ---")
    
    # Use print() para portabilidade, em vez de display()
    print(df_resultados_finais)

    plotar_capacidade_mensal(
        df_resultados_finais, 
        capacidade_inicial,
        capacidade_limite_perda,
        cfg_arq["plot_mensal"],
        cfg_plot
    )
    plotar_capacidade_anual(
        df_resultados_finais, 
        capacidade_inicial,
        capacidade_limite_perda,
        cfg_arq["plot_anual"],
        cfg_plot
    )

    print("\n --- PERDA DE CAPACIDADE TOTAL ACUMULADA (Final) ---")
    if not df_resultados_finais.empty:
        dano_final_acumulado = ultimo_resultado['dano_total_acum']
        print(f"-> A perda de capacidade total acumulada estimada foi de {dano_final_acumulado:.2f}%")
    else:
        print("Nenhum resultado calculado.")

    return df_resultados_finais

def carregar_e_fatiar_dados_entrada(filename, config_entrada):
    """
    Carrega o arquivo de entrada .mat, converte para um DataFrame
    e o fatia em blocos mensais com base na configuração.
    
    Args:
        filename (str): Caminho para o arquivo .mat (ex: 'Atot.mat').
        config_entrada (dict): O dicionário "config_dados_entrada"
                               contendo dt_minutos, dias_por_mes_sim, etc.
    
    Retorna:
        list: Uma lista de DataFrames, um para cada mês.
    """
    
    # --- 1. CARREGAR E TRANSFORMAR (Como fizemos antes) ---
    try:
        dados_mat = loadmat(filename)
        df_total = pd.DataFrame(dados_mat['ATot'].T, columns=['Tempo', 'Potencia_kW'])
        print(f"Arquivo '{filename}' carregado. Total de {len(df_total)} linhas.")
    except Exception as e:
        print(f"Erro ao carregar ou converter '{filename}': {e}")
        return []

    # --- 2. CALCULAR O TAMANHO DA FATIA (Dinamicamente) ---
    # Lê os parâmetros do config
    dt_minutos = config_entrada['dt_minutos']
    dias_por_mes = config_entrada['dias_por_mes_sim']
    num_meses = config_entrada['meses_por_ano_sim']

    # Calcula as linhas por mês (sem "números mágicos")
    minutos_por_mes = dias_por_mes * 24 * 60
    linhas_por_mes = int(minutos_por_mes / dt_minutos) # ex: 30*24*60 / 5 = 8640

    total_linhas_esperado = linhas_por_mes * num_meses # ex: 8640 * 12 = 103680

    if len(df_total) != total_linhas_esperado:
        print(f"Atenção: O total de linhas ({len(df_total)}) não corresponde"
              f" ao esperado ({total_linhas_esperado}). Verifique config_dados_entrada.")

    # --- 3. FATIAR O DATAFRAME ---
    lista_dataframes_mensais = []
    
    for i in range(num_meses):
        indice_inicio = i * linhas_por_mes
        indice_fim = (i + 1) * linhas_por_mes
        
        df_mes = df_total.iloc[indice_inicio:indice_fim].copy()
        
        # Reinicia o tempo para o PLECS (começando em 0)
        if not df_mes.empty:
            tempo_inicial_do_mes = df_mes['Tempo'].iloc[0]
            df_mes['Tempo'] = df_mes['Tempo'] - tempo_inicial_do_mes
        
        lista_dataframes_mensais.append(df_mes)
        
    print(f"Dados fatiados em {len(lista_dataframes_mensais)} blocos mensais de {linhas_por_mes} linhas cada.")
    return lista_dataframes_mensais


if __name__ == "__main__":
    CONFIGURACAO = {
        "simulacao": {
            "tempo_simulacao_anos": 15,
            "dt_minutos": 5,
            "data_inicio_simulacao": '2025-01-01 00:00:00',
            

        },
        "arquivos": {
            "entrada_csv": "dadosnovos.csv",
            "arquivo_entrada_mat": "Atot.mat",
            "plecs_model_file": "caminho/para/seu_modelo.plecs",
            "plot_mensal": "capacidade_restante_mensal.png",
            "plot_anual": "capacidade_restante_anual.png",
            "colunas_csv": [
                'Tempo_min','Hora_do_Dia','Tensao_V',
                'Potencia_kW','Estado_Maquina',
                'Corrente_A','SOC'
            ]
        },
        "bateria": {
            "capacidade_inicial_perc": 100.0,
            "capacidade_limite_perda_perc": 20.0,
            "Tbat_kelvin": 30 + 273.15            
        },
        "modelo_fisico": {
            "ciclo": {
                "a": 2.6418, "b": -0.01943, "c": 0.004,
                "d": 0.01705, "g": 0.0123, "h": 0.7162,
                "exp_cycle": 2,"peak_prominence": 1.0, 
                "range_round_dp": 1,    
                "mean_round_dp": 1      
            },
            "calendario": {
                "k_T": 1.9775e-11, "exp_T": 0.07511,
                "k_soc": 1.639, "exp_soc": 0.007388,
                "exp_cal": 10/8
            }
        },
        "config_plot": {
            "dpi": 150,
            "ylim_top": 105,
            "ylim_bottom_min_eol": 70, 

            "mensal_figsize": (15, 7),
            "mensal_cor": "darkgreen",
            "xticks_step_months": 12,

            "anual_figsize": (12, 7),
            "anual_cor": "darkred",
            "anual_marker": "s",
            "anual_markersize": 8,
            
            "anual_text_offset": 0.5,
            "anual_text_fontsize": 9,
            "anual_text_color": "black",
            "anual_text_format": "{:.2f}%"
        },
        "config_dados_entrada": {
            "dt_minutos": 5,             # Espaçamento (delta t) do arquivo .mat
            "dias_por_ano_avg": 360,     # Para cálculo de multiplicação
            "dias_por_mes_sim": 30,      # Definição de um "mês" de simulação
            "meses_por_ano_sim": 12      # Definição de um "ano" de simulação
        }
        # ---------------------------------------------
    }
    # ---------------------------------------------

    # Passa o dicionário completo para a função principal
    # Conecta ao servidor PLECS que está rodando na sua máquina na porta 1080
    #plecs_server = xmlrpc.client.ServerProxy("http://localhost:1080/RPC2")
    #resultados = simular_degradacao_bateria(CONFIGURACAO)

    #plecs_server.plecs.load()                           #carrega o modelo
    #plecs_server.plecs.set(nome_do_bloco, valor)        #envia os dados de entrada
    #plecs_server.plecs.simulate(nome_do_modelo)         #roda a simulação
    #plecs_server.plecs.get(nome_do_bloco_de_saida)      #pega os dados de saída




    