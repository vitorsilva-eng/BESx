
import os
import json
import time
import numpy as np
import pandas as pd
import datetime
from pydantic import BaseModel
from typing import List, Any, Dict

# Imports internos
from besx.infrastructure.files.file_manager import FileManager
from besx.infrastructure.loaders.data_handler import data_handle
from besx.infrastructure.plecs.plecs_connector import run_monthly_simulation, close_plecs_server, extrair_soc_final
from besx.domain.models.degradation_model import dano_ciclo, dano_calendar, calcular_estatisticas_operacionais
from besx.domain.models.battery_simulator import picos_e_vales, ciclos_idle
from besx.infrastructure.visualization.plots import plotar_capacidade_mensal, plotar_composicao_degradacao
from besx.infrastructure.reports.report import gerar_relatorio_txt
from besx.infrastructure.logging.logger import logger
from besx.infrastructure.reports.validation_report import gerar_relatorio_validacao, exportar_debug_degradacao, export_xlsx

class ResultadoMes(BaseModel):
    mes: int
    total_meses: int
    dano_ciclos_mes: float
    dano_cal_mes: float
    dano_ciclo_acum: float
    dano_cal_acum: float
    dano_total_acum: float
    capacidade_restante: float
    acum_energia_carga_kWh: float
    acum_energia_descarga_kWh: float
    df_soc_amostrado: List[Dict[str, Any]]
    Ciclos_Contagem: int
    EFC_Ciclos_Equivalentes: float
    DOD_Medio_Perc: float
    C_Rate_Max: float
    C_Rate_Medio: float
    SOC_Medio: float
    SOC_Medio_Idle: float
    Tempo_SOC_Alto_Perc: float
    Tempo_SOC_Baixo_Perc: float
    Energia_Carga_kWh: float
    Energia_Descarga_kWh: float
    Rainflow_Cycles: List[Any]

class SimulationManager:
    def __init__(self, config, backend: str = "python", data_file: str = None,
                 on_mes_complete: callable = None, sim_until_eol: bool = False,
                 resume_folder: str = None):
        self.config = config
        self.backend = backend  # "python" | "plecs"
        self.data_file = data_file # Opcional: nome do arquivo em /database
        self.on_mes_complete = on_mes_complete
        self.sim_until_eol = sim_until_eol  # Se True, ignora meses_alvo e roda até EOL
        # Inicializa gerenciador de arquivos (cria pastas)
        self.file_manager = FileManager(resume_folder=resume_folder)
        
        # Estado Inicial
        self.soh_atual = self.config.simulacao.SOH_INICIAL_PERC / 100.0
        self.soc_zero = 0
        self.resultados_mensais = []
        self.calculos_detalhados = []  # Armazena DataFrames detalhados de cada mês
        
        # Variáveis de Acumulação
        self.acum_ciclo_global = 0.0
        self.acum_cal_global = 0.0
        self.acum_energia_carga = 0.0
        self.acum_energia_descarga = 0.0
        self.start_time = None
        
        # Controle de Checkpoint
        self.mes_inicial = 1
        
        # Atalhos de config
        self.exp_cal = self.config.modelo_degradacao.calendario.exp_cal
        self.cfg_bat = self.config.bateria
        
        # Carrega checkpoint se existir
        self._carregar_checkpoint()

    def _carregar_checkpoint(self):
        caminho_checkpoint = self.file_manager.get_data_path("checkpoint.json")
        if os.path.exists(caminho_checkpoint):
            try:
                with open(caminho_checkpoint, 'r', encoding='utf-8') as f:
                    estado = json.load(f)
                self.soh_atual = estado.get("soh_atual", self.soh_atual)
                self.soc_zero = estado.get("soc_zero", self.soc_zero)
                self.acum_ciclo_global = estado.get("acum_ciclo_global", self.acum_ciclo_global)
                self.acum_cal_global = estado.get("acum_cal_global", self.acum_cal_global)
                self.acum_energia_carga = estado.get("acum_energia_carga", self.acum_energia_carga)
                self.acum_energia_descarga = estado.get("acum_energia_descarga", self.acum_energia_descarga)
                self.resultados_mensais = estado.get("resultados_mensais", [])
                
                meses_salvos = len(self.resultados_mensais)
                if meses_salvos > 0:
                    self.mes_inicial = self.resultados_mensais[-1].get("mes", meses_salvos) + 1
                logger.info(f"Checkpoint carregado com sucesso. Retomando a partir do mês {self.mes_inicial} (SOH: {self.soh_atual*100:.2f}%)")
            except Exception as e:
                logger.error(f"Erro ao carregar o checkpoint.json: {e}")

    def _salvar_checkpoint(self):
        caminho_checkpoint = self.file_manager.get_data_path("checkpoint.json")
        estado = {
            "soh_atual": self.soh_atual,
            "soc_zero": self.soc_zero,
            "acum_ciclo_global": self.acum_ciclo_global,
            "acum_cal_global": self.acum_cal_global,
            "acum_energia_carga": self.acum_energia_carga,
            "acum_energia_descarga": self.acum_energia_descarga,
            "resultados_mensais": self.resultados_mensais,
        }
        try:
            with open(caminho_checkpoint, 'w', encoding='utf-8') as f:
                json.dump(estado, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Erro ao salvar checkpoint.json: {e}")

    def run(self):
        self.start_time = datetime.datetime.now()
        logger.info("Iniciando a Execução via SimulationManager")
        logger.info(f"Resultados serão salvos em: {self.file_manager.sim_folder}")
        
        # --- ETAPA 1: CARREGANDO OS DADOS ---
        # Em modo EOL, carrega o máximo de dados possível (20 anos)
        # Em modo normal, usa os anos configurados pelo usuário
        if self.sim_until_eol:
            meses_alvo = 240  # 20 anos como teto de segurança para EOL
            logger.info("[EOL] Modo 'Simular até Fim de Vida' ativo. Rodando até atingir o limite.")
        elif self.config.simulacao.MESES_SIMULACAO is not None:
            meses_alvo = self.config.simulacao.MESES_SIMULACAO
            logger.info(f"Modo Duração Personalizada: {meses_alvo} meses.")
        else:
            meses_alvo = self.config.simulacao.ANOS_SIMULACAO * 12
        
        # Passamos o data_file se fornecido, senão ele pede via console no data_handle()
        df_perfil_bess = data_handle(nome_arquivo=self.data_file, meses_alvo=meses_alvo)
        
        if not df_perfil_bess:
            logger.error("Falha ao carregar dados de entrada. Abortando.")
            return

        logger.info("Dados iniciais tratados")
        
        # --- ETAPA 2: ITERAÇÃO MENSAL ---
        total_meses = len(df_perfil_bess)
        
        try:
            for mes_idx, df_mes in enumerate(df_perfil_bess):
                mes_id = mes_idx + 1
                if mes_id < self.mes_inicial:
                    continue  # Pula os meses já processados no checkpoint
                    
                self._processar_mes(df_mes, mes_id, total_meses)
                self._salvar_checkpoint()
                
                # Checagem de fim de vida (sempre ativa)
                if self.soh_atual * 100 <= 100 - self.cfg_bat.capacidade_limite_perda_perc:
                    logger.warning("Capacidade limite atingida. Finalizando simulação.")
                    break
        finally:
            if self.backend == "plecs":
                close_plecs_server()

        # --- ETAPA 3: RESULTADOS FINAIS ---
        self._finalizar_simulacao()

    def _processar_mes(self, df_mes, mes_id, total_meses):
        # 1. Simulação da bateria (backend escolhido no menu)
        perfil_soc_mes = run_monthly_simulation(
            df_mes, self.soh_atual, self.soc_zero, mes_id,
            config=self.config,
            backend=self.backend
        )
        
        # Atualiza SOC inicial para o próximo mês
        self.soc_zero = extrair_soc_final(perfil_soc_mes)
        
        # ... (logging/debug omitido por brevidade se não mudar)
        # Exporta Debug SOC
        caminho_debug = self.file_manager.get_debug_path("") # Pasta debug
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_soc_mes, "perfil_soc_mes", mes_id, pasta_debug=caminho_debug)
        
        # 2. Dano Cíclico
        prominence = self.config.modelo_degradacao.ciclo.peak_prominence
        perfil_simp = picos_e_vales(perfil_soc_mes['SOC'], prominence=prominence)
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_simp, "picos_e_vales", mes_id, pasta_debug=caminho_debug)   
        
        # Prepara parâmetros para o modelo de ciclo
        params_ciclo = self.config.modelo_degradacao.ciclo
        Ccyc, df_ciclo_detalhado = dano_ciclo(perfil_simp.tolist(), self.cfg_bat.Tbat_kelvin, params_ciclo)
        self.acum_ciclo_global = np.sqrt(self.acum_ciclo_global**2 + Ccyc**2)
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(perfil_soc_mes['SOC'].round(1).tolist(),"soc_usado_idle", mes_id, pasta_debug=caminho_debug)

        # 3. Dano Calendário
        if len(perfil_soc_mes) > 1:
            dt_soc_minutos = (perfil_soc_mes['Tempo'].iloc[1] - perfil_soc_mes['Tempo'].iloc[0]) / 60.0
        else:
            dt_soc_minutos = 1.0
        
        minutos_por_mes = (self.config.dados_entrada.dias_por_ano_avg * 24 * 60) / 12
        idle_cycles_mes = ciclos_idle(
            perfil_soc_mes['SOC'].round(1).tolist(), 
            dt_minutos_soc=dt_soc_minutos,
            minutos_por_mes=minutos_por_mes
        )
        
        if self.config.relatorio.gerar_validacao_detalhada:
            exportar_debug_degradacao(idle_cycles_mes, "idle_cycles_mes", mes_id, pasta_debug=caminho_debug)
        
        params_cal = self.config.modelo_degradacao.calendario
        Ccal, df_calendario_detalhado = dano_calendar(
            idle_cycles_mes, 
            self.cfg_bat.Tbat_kelvin_idle,
            model_params=params_cal,
            dt_minutos=self.config.dados_entrada.dt_minutos,
            dias_por_ano_avg=self.config.dados_entrada.dias_por_ano_avg
        )
        self.acum_cal_global = (self.acum_cal_global**self.exp_cal + Ccal**self.exp_cal)**(1/self.exp_cal)

        # 4. Atualiza SOH
        perda_total_perc = self.acum_ciclo_global + self.acum_cal_global
        self.soh_atual = (self.config.simulacao.SOH_INICIAL_PERC - perda_total_perc) / 100.0

        # 5. Estatísticas
        cap_kwh = self.cfg_bat.capacidade_nominal_wh / 1000.0
        stats_ops = calcular_estatisticas_operacionais(perfil_soc_mes, df_mes, cap_kwh=cap_kwh, lista_periodos_idle=idle_cycles_mes)
        
        logger.info(f"   -> Resumo Mês {mes_id}/{total_meses}: {stats_ops.Ciclos_Contagem} ciclos | "
              f"SOH: {self.soh_atual*100:.2f}%")

        # 6. Agrega Resultados
        self.acum_energia_carga += stats_ops.Energia_Carga_kWh
        self.acum_energia_descarga += stats_ops.Energia_Descarga_kWh

        # Realiza Downsampling do perfil Operacional para o Frontend e Histórico 
        # (Preserva máximo de 1000 pontos p/ mes para não travar RAM do Streamlit)
        passo_amostral = max(1, len(perfil_soc_mes) // 1000)
        df_plot_reduzido = perfil_soc_mes.iloc[::passo_amostral].copy()
        try:
            dict_soc_amostrado = df_plot_reduzido.to_dict(orient='records')
        except Exception as e:
            logger.warning(f"Falha ao gerar amostragem do Mês {mes_id}. Erro: {e}")
            dict_soc_amostrado = []
            
        resultado_mes = ResultadoMes(
            mes=mes_id,
            total_meses=total_meses,
            dano_ciclos_mes=Ccyc,
            dano_cal_mes=Ccal,
            dano_ciclo_acum=self.acum_ciclo_global,
            dano_cal_acum=self.acum_cal_global,
            dano_total_acum=self.acum_ciclo_global + self.acum_cal_global,
            capacidade_restante=self.soh_atual * 100,
            acum_energia_carga_kWh=self.acum_energia_carga,
            acum_energia_descarga_kWh=self.acum_energia_descarga,
            df_soc_amostrado=dict_soc_amostrado,
            **stats_ops.model_dump()
        )
        self.resultados_mensais.append(resultado_mes.model_dump())
        
        # Armazena cálculos detalhados para o relatório de validação
        self.calculos_detalhados.append({
            'mes': mes_id,
            'df_ciclo': df_ciclo_detalhado,
            'df_calendario': df_calendario_detalhado
        })

        # 7. Callback para Dashboard (Live Update)
        if self.on_mes_complete:
            self.on_mes_complete(perfil_soc_mes, dados_mes, df_mes)

    def _finalizar_simulacao(self):
        df_resultados_finais = pd.DataFrame(self.resultados_mensais)
        
        logger.info(f"\n--- Resultado Final Consolidado ---\n{df_resultados_finais.tail()}")
        
        # Obter nome amigável da bateria
        bateria_nome = next(
            (n for n, p in __import__('besx.config', fromlist=['PERFIS_BATERIA']).PERFIS_BATERIA.items()
             if p.capacidade_nominal_wh == self.config.bateria.capacidade_nominal_wh), 'Desconhecido'
        )
        # Prefixo: Ex: python_Bateria_100kWh_20231027_103000
        prefixo = f"{self.backend}_{bateria_nome}_{self.file_manager.timestamp}"
        
        # Salvar Excel Final na pasta data
        caminho_excel = self.file_manager.get_data_path(f"resultados_completos_{prefixo}.xlsx")
        df_resultados_finais.to_excel(caminho_excel, index=False)
        logger.info(f"Resultados salvos em: {caminho_excel}")

        # Salvar snapshot da configuração para comparação futura
        try:
            snap = self.config.model_dump(exclude={'bateria'})
            snap['bateria_nome'] = bateria_nome
            snap['bateria_cap_wh'] = self.config.bateria.capacidade_nominal_wh
            snap['bateria_soc_min'] = self.config.bateria.soc_min
            snap['bateria_soc_max'] = self.config.bateria.soc_max
            snap['backend'] = self.backend
            snap['sim_until_eol'] = self.sim_until_eol
            snap['total_meses_simulados'] = len(self.resultados_mensais)
            snap['data_file'] = self.data_file
            snap['timestamp'] = self.file_manager.timestamp
            # Serializar para JSON com suporte a float
            snap_path = self.file_manager.get_data_path(f"config_snapshot_{prefixo}.json")
            with open(snap_path, 'w', encoding='utf-8') as f:
                json.dump(snap, f, indent=2, default=str)
            logger.info(f"Snapshot da configuração salvo em: {snap_path}")
        except Exception as e:
            logger.warning(f"Não foi possível salvar config_snapshot.json: {e}")

        # Plots
        caminho_plot_cap = self.file_manager.get_plot_path(f"capacidade_restante_mensal_{prefixo}.png")
        plotar_capacidade_mensal(df_resultados_finais, nome_arquivo_saida=caminho_plot_cap)
        
        caminho_plot_comp = self.file_manager.get_plot_path(f"composicao_degradacao_{prefixo}.png")
        plotar_composicao_degradacao(df_resultados_finais, nome_arquivo_saida=caminho_plot_comp)
        
        close_plecs_server()
        
        # Gerar Relatório de Validação (se habilitado)
        if self.config.relatorio.gerar_validacao_detalhada:
            gerar_relatorio_validacao(
                self.file_manager, 
                self.config, 
                self.resultados_mensais, 
                self.calculos_detalhados,
                prefixo=prefixo
            )
        
        # Gerar Relatório de Texto
        # Calcula a duração
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        gerar_relatorio_txt(self.file_manager, self.config, df_resultados_finais, str(duration), prefixo=prefixo)

    # Método antigo removido em favor do módulo externo