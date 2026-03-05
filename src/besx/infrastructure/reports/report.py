
import os
import datetime
import pandas as pd
from besx.infrastructure.logging.logger import logger

def gerar_relatorio_txt(file_manager, config, df_res, sim_duration_str, prefixo=""):
    """
    Gera um relatório de texto detalhado com metadados, configuração 
    e resumo dos resultados da simulação.
    
    Args:
        file_manager (FileManager): Gerenciador de arquivos para salvar o relatório.
        config (dict): Dicionário de configuração usado na simulação.
        df_res (pd.DataFrame): DataFrame com os resultados mensais consolidados.
        sim_duration_str (str): String com a duração total da simulação.
        prefixo (str): Prefixo (backend, bateria, etc) para o nome do arquivo final.
    """
    
    cfg_bat = config.bateria
    cfg_sim = config.simulacao
    cfg_deg_ciclo = config.modelo_degradacao.ciclo
    cfg_deg_cal = config.modelo_degradacao.calendario
    
    # Cálculos Finais
    soh_final = df_res.iloc[-1]['capacidade_restante']
    perda_total = df_res.iloc[-1]['dano_total_acum']
    ciclos_totais = df_res['Ciclos_Contagem'].sum()
    efc_total = df_res['EFC_Ciclos_Equivalentes'].sum()
    
    # Estimativa simples de vida útil (linear)
    # Se perdeu X% em N meses, perderá 20% (EOL) em quanto tempo?
    meses_simulados = len(df_res)
    perda_por_mes = perda_total / meses_simulados if meses_simulados > 0 else 0
    eol_target = cfg_bat.capacidade_limite_perda_perc
    
    if perda_por_mes > 0:
        meses_ate_eol = eol_target / perda_por_mes
        anos_ate_eol = meses_ate_eol / 12
        vida_util_str = f"{anos_ate_eol:.1f} anos ({meses_ate_eol:.0f} meses)"
    else:
        vida_util_str = "Indeterminada (perda desprezível)"

    txt = []
    txt.append("="*50)
    txt.append(f"RELATÓRIO DE SIMULAÇÃO BESx")
    txt.append("="*50)
    txt.append(f"Data da Execução: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    txt.append(f"Duração da Simulação: {sim_duration_str}")
    txt.append("")
    
    txt.append("-" * 30)
    txt.append("1. CONFIGURAÇÃO (SNAPSHOT)")
    txt.append("-" * 30)
    txt.append(f"Arquivo de Entrada: {config.dados_entrada.ARQUIVO_MAT}")
    txt.append(f"Passo de Tempo (dt): {config.dados_entrada.dt_minutos} min")
    txt.append("")
    txt.append("[Bateria]")
    txt.append(f"  Capacidade Nominal: {cfg_bat.capacidade_nominal_wh} Wh")
    txt.append(f"  Tensão Nom/Min/Max: {3.2}V / {cfg_bat.v_min_celula}V / {cfg_bat.v_max_celula}V") # Tensão Nom aprox
    txt.append(f"  Temperatura: {cfg_bat.Tbat_kelvin - 273.15:.1f} °C")
    txt.append(f"  SOC Operacional: {cfg_bat.soc_min*100:.1f}% - {cfg_bat.soc_max*100:.1f}%")
    txt.append("")
    txt.append("[Parâmetros de Degradação]")
    txt.append(f"  Ciclo (Rainflow): a={cfg_deg_ciclo.a}, b={cfg_deg_ciclo.b}")
    txt.append(f"  Calendário: k_T={cfg_deg_cal.k_T}, k_soc={cfg_deg_cal.k_soc}")
    txt.append("")

    txt.append("-" * 30)
    txt.append("2. ESTATÍSTICAS OPERACIONAIS (MÉDIAS)")
    txt.append("-" * 30)
    txt.append(f"SOC Médio Global: {df_res['SOC_Medio'].mean() * 100.0:.1f}%")
    txt.append(f"C-Rate Médio: {df_res['C_Rate_Medio'].mean():.2f} C")
    txt.append(f"DOD Médio (dos Ciclos): {df_res['DOD_Medio_Perc'].mean() * 100.0:.1f}%")
    txt.append(f"SOC Médio em Repouso: {df_res['SOC_Medio_Idle'].replace(0, float('nan')).mean() * 100.0:.1f}%")
    txt.append(f"Tempo em SOC Alto (>90%): {df_res['Tempo_SOC_Alto_Perc'].mean():.1f}%")
    txt.append(f"Tempo em SOC Baixo (<10%): {df_res['Tempo_SOC_Baixo_Perc'].mean():.1f}%")
    txt.append("")

    txt.append("-" * 30)
    txt.append("3. RESULTADOS DE DEGRADAÇÃO")
    txt.append("-" * 30)
    txt.append(f"SOH Inicial: {cfg_sim.SOH_INICIAL_PERC}%")
    txt.append(f"SOH Final ({meses_simulados} meses): {soh_final:.2f}%")
    txt.append(f"Perda Total Acumulada: {perda_total:.3f}%")
    txt.append(f"  -> Por Ciclagem: {df_res.iloc[-1]['dano_ciclo_acum']:.3f}%")
    txt.append(f"  -> Por Calendário: {df_res.iloc[-1]['dano_cal_acum']:.3f}%")
    txt.append("")
    txt.append(f"Ciclos Contados (Rainflow): {int(ciclos_totais)}")
    txt.append(f"Ciclos Equivalentes (EFC): {efc_total:.1f}")
    txt.append("")
    txt.append(f"ESTIMATIVA DE VIDA ÚTIL (até {eol_target}% de perda):")
    txt.append(f"  >> {vida_util_str} <<")
    txt.append("(Nota: Projeção linear baseada na taxa de degradação atual)")
    txt.append("="*50)
    
    conteudo = "\n".join(txt)
    nome_arquivo = f"report_{prefixo}.txt" if prefixo else "report.txt"
    path = file_manager.save_report(conteudo, filename=nome_arquivo)
    logger.info(f"Relatório detalhado salvo em: {path}")
    return path
