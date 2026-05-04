import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Imports de Domínio
from besx.domain.models.degradation_model import (
    dano_ciclo, 
    dano_calendar, 
    calcular_estatisticas_operacionais, 
    EstatisticasOperacionais
)
from besx.domain.models.battery_simulator import picos_e_vales, ciclos_idle
from besx.infrastructure.logging.logger import logger

@dataclass
class DamageResult:
    """DTO para transportar os resultados do processamento de degradação de um mês."""
    Ccyc: float
    Ccal: float
    acum_ciclo_global: float
    acum_cal_global: float
    soh_atual: float                  # Fração 0-1
    stats_ops: EstatisticasOperacionais
    df_ciclo_detalhado: pd.DataFrame
    df_calendario_detalhado: pd.DataFrame
    idle_cycles_mes: List[Dict[str, Any]]
    perfil_simp: np.ndarray           # SOC simplificado (picos e vales) para debug

class DegradationEngine:
    """Motor de degradação otimizado para passo único."""

    def __init__(self, soh_inicial_perc: float, config: Any) -> None:
        """Inicializa o motor com o SOH inicial e as configurações."""
        self.config = config
        self.soh_inicial_perc = soh_inicial_perc
        self.soh_atual = soh_inicial_perc / 100.0
        self.acum_ciclo_global = 0.0
        self.acum_cal_global = 0.0
        self.exp_cal = self.config.modelo_degradacao.calendario.exp_cal
        self.cfg_bat = self.config.bateria

    def calculate_degradation(
        self,
        perfil_soc_mes: pd.DataFrame,
        df_mes_entrada: pd.DataFrame,
        mes_id: int,
        caminho_debug: str,
        gerar_debug: bool = False
    ) -> DamageResult:
        """
        Calcula a degradação otimizando o processamento da série temporal.
        """
        soc_series = perfil_soc_mes['SOC']
        
        # 1. Passo Único de Simplificação (Prepara dados para Ciclo e Estatísticas)
        prominence = self.config.modelo_degradacao.ciclo.peak_prominence
        perfil_simp = picos_e_vales(soc_series, prominence=prominence)
        
        # 2. Passo Único de Idle (Prepara dados para Calendário e Estatísticas)
        if len(perfil_soc_mes) > 1:
            dt_soc_minutos = (perfil_soc_mes['Tempo'].iloc[1] - perfil_soc_mes['Tempo'].iloc[0]) / 60.0
        else:
            dt_soc_minutos = 1.0
        minutos_por_mes = (self.config.dados_entrada.dias_por_ano_avg * 24 * 60) / 12
        
        # Usamos round(4) para evitar micro-ruídos térmicos se houver, mas picos_e_vales já deve filtrar.
        # battery_simulator.ciclos_idle agora espera np.ndarray e é vetorizada.
        idle_cycles_mes = ciclos_idle(
            soc_series.values,
            dt_minutos_soc=dt_soc_minutos,
            minutos_por_mes=minutos_por_mes
        )

        # 3. Cálculo de Dano (Ciclo)
        params_ciclo = self.config.modelo_degradacao.ciclo
        Ccyc, df_ciclo_detalhado = dano_ciclo(None, self.cfg_bat.Tbat_kelvin, params_ciclo, perfil_simp=perfil_simp)
        self.acum_ciclo_global = np.sqrt(self.acum_ciclo_global**2 + Ccyc**2)

        # 4. Cálculo de Dano (Calendário)
        params_cal = self.config.modelo_degradacao.calendario
        Ccal, df_calendario_detalhado = dano_calendar(
            idle_cycles_mes,
            self.cfg_bat.Tbat_kelvin_idle,
            model_params=params_cal,
            dt_minutos=self.config.dados_entrada.dt_minutos,
            dias_por_ano_avg=self.config.dados_entrada.dias_por_ano_avg
        )
        self.acum_cal_global = (self.acum_cal_global**self.exp_cal + Ccal**self.exp_cal)**(1/self.exp_cal)
        
        # 5. Atualiza SOH
        perda_total_perc = self.acum_ciclo_global + self.acum_cal_global
        self.soh_atual = (self.soh_inicial_perc - perda_total_perc) / 100.0
        
        # 6. Estatísticas Operacionais (Passando perfil simplificado e idle para evitar re-cálculo)
        n_unid = getattr(self.config.simulacao, 'n_unidades', 1)
        cap_kwh = (self.cfg_bat.capacidade_nominal_wh * n_unid) / 1000.0
        stats_ops = calcular_estatisticas_operacionais(
            perfil_soc_mes, 
            df_mes_entrada, 
            cap_kwh=cap_kwh, 
            lista_periodos_idle=idle_cycles_mes,
            perfil_simp=perfil_simp
        )
        
        return DamageResult(
            Ccyc=Ccyc,
            Ccal=Ccal,
            acum_ciclo_global=self.acum_ciclo_global,
            acum_cal_global=self.acum_cal_global,
            soh_atual=self.soh_atual,
            stats_ops=stats_ops,
            df_ciclo_detalhado=df_ciclo_detalhado,
            df_calendario_detalhado=df_calendario_detalhado,
            idle_cycles_mes=idle_cycles_mes,
            perfil_simp=perfil_simp
        )

    def get_state(self) -> Dict[str, Any]:
        return {
            "acum_ciclo_global": self.acum_ciclo_global,
            "acum_cal_global": self.acum_cal_global,
            "soh_atual": self.soh_atual
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        self.acum_ciclo_global = state.get("acum_ciclo_global", 0.0)
        self.acum_cal_global = state.get("acum_cal_global", 0.0)
        self.soh_atual = state.get("soh_atual", self.soh_inicial_perc / 100.0)
