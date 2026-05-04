"""
Módulo do Sistema de Gerenciamento de Energia (EMS) da bateria.

Este módulo implementa algoritmos de despacho (Peak Shaving e Load Shifting) 
de forma puramente algorítmica e vetorizada, gerando o perfil de setpoint
(Potência Alvo) agnóstico às restrições físicas da bateria.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union
from besx.infrastructure.logging.logger import logger

class BessEMS:
    """
    Sistema de Gerenciamento de Energia para Baterias (EMS).
    
    Esta classe implementa as estratégias puras de perfil de despacho, baseando-se
    apenas nas restrições comerciais da rede elétrica (Time-of-Use e/ou Demand Limit).
    Não lida com as restrições físicas reais da bateria, operando de forma 100% vetorizada e O(1).
    """
    
    def __init__(self) -> None:
        """
        Inicializa o gerador de perfis do EMS de forma agnóstica à bateria.
        """
        logger.info("BessEMS inicializado (Agnóstico à Bateria).")

    def gerar_perfil_load_shifting(
        self, 
        df_carga: pd.DataFrame, 
        hora_inicio_carga: int, 
        hora_fim_carga: int, 
        hora_inicio_descarga: int, 
        hora_fim_descarga: int,
        limite_demanda_kw: float,
        ignorar_fins_de_semana: bool = True,
        feriados: Optional[list] = None,
        coluna_tempo: str = 'Time',
        coluna_carga: str = 'Load_W'
    ) -> pd.DataFrame:
        """
        Aplica a estratégia de Load Shifting (Arbitragem de Tempo de Uso) de forma vetorizada.
        """
        logger.info("Iniciando processamento de Load Shifting (Vetorizado).")
        
        df = df_carga.copy()
        
        if not pd.api.types.is_datetime64_any_dtype(df[coluna_tempo]):
            df['datetime_temp'] = pd.to_datetime(df[coluna_tempo])
        else:
            df['datetime_temp'] = df[coluna_tempo]
            
        horas = df['datetime_temp'].dt.hour
        dias_semana = df['datetime_temp'].dt.dayofweek
        datas = df['datetime_temp'].dt.date
        
        potencia_bat_w = np.zeros(len(df))
        
        # Filtro de dias úteis e feriados
        dias_invalidos = np.zeros(len(df), dtype=bool)
        if ignorar_fins_de_semana:
            dias_invalidos = dias_invalidos | (dias_semana >= 5)  # 5=Sábado, 6=Domingo
        if feriados:
            feriados_dates = pd.to_datetime(feriados).dt.date if isinstance(feriados, pd.Series) else pd.to_datetime(feriados).date
            dias_invalidos = dias_invalidos | datas.isin(feriados_dates)
        carga_w = df[coluna_carga].values
        limite_demanda_w = limite_demanda_kw * 1000.0  
        
        # Máscaras de Janela
        if hora_inicio_carga < hora_fim_carga:
            is_carga = (horas >= hora_inicio_carga) & (horas < hora_fim_carga)
        else:
            is_carga = (horas >= hora_inicio_carga) | (horas < hora_fim_carga)
            
        if hora_inicio_descarga < hora_fim_descarga:
            is_descarga = (horas >= hora_inicio_descarga) & (horas < hora_fim_descarga)
        else:
            is_descarga = (horas >= hora_inicio_descarga) | (horas < hora_fim_descarga)
            
        # Ação de Carga (Sinal Positivo = Bateria agindo como Carga/Consumidor)
        folga_demanda = limite_demanda_w - carga_w
        mask_carga = is_carga & (folga_demanda > 0) & (~dias_invalidos)
        potencia_bat_w[mask_carga] = folga_demanda[mask_carga]
        
        # Ação de Descarga (Sinal Negativo = Bateria agindo como Gerador)
        mask_descarga = is_descarga & (~dias_invalidos)
        potencia_bat_w[mask_descarga] = -carga_w[mask_descarga]

        df_out = pd.DataFrame({
            coluna_tempo: df[coluna_tempo],
            'Potencia_Bateria_W': potencia_bat_w
        })
        
        logger.info("Cálculo de Load Shifting finalizado.")
        return df_out

    def gerar_perfil_peak_shaving(
        self, 
        df_carga: pd.DataFrame, 
        limite_demanda_kw: float,
        faixa_seguranca_kw: float = 0.0,
        faixa_seguranca_pct: float = 0.0,
        coluna_tempo: str = 'Time',
        coluna_carga: str = 'Load_W'
    ) -> pd.DataFrame:
        """
        Aplica a estratégia de Peak Shaving (Corte de Pico) de forma vetorizada,
        considerando faixas de segurança absolutas ou percentuais.
        """
        # Desconta a margem do limite alvo de demanda
        limite_efetivo_kw = limite_demanda_kw - faixa_seguranca_kw
        if faixa_seguranca_pct > 0:
            limite_efetivo_kw -= (limite_demanda_kw * (faixa_seguranca_pct / 100.0))
            
        logger.info(f"Iniciando Peak Shaving. Limite Contratado: {limite_demanda_kw}kW | Alvo Efetivo: {limite_efetivo_kw}kW (Vetorizado).")
        
        df = df_carga.copy()
        
        carga_w = df[coluna_carga].values
        limite_demanda_w = limite_efetivo_kw * 1000.0
        
        # Espelho matemático: Tenta manter a energia da rede exatamente no limite_demanda_w
        # Se carga > limite: descarrega o excesso (potencia_dis_w negativo)
        # Se carga < limite: carrega o quanto sobrar (potencia_dis_w positivo)
        potencia_dis_w = limite_demanda_w - carga_w
        
        df_out = pd.DataFrame({
            coluna_tempo: df[coluna_tempo],
            'Potencia_Bateria_W': potencia_dis_w
        })
        
        logger.info("Cálculo de Peak Shaving finalizado.")
        return df_out

    def gerar_perfil_power_factor_correction(
        self,
        df_carga: pd.DataFrame,
        pf_target: float,
        s_max_va: float,
        coluna_tempo: str = 'Time'
    ) -> pd.DataFrame:
        """
        Aplica a correção do fator de potência de forma vetorizada, despachando potência reativa (VAr).
        Respeita a capacidade geométrica do inversor S_max.
        """
        logger.info(f"Iniciando correção de fator de potência. PF={pf_target}, S_max={s_max_va}VA (Vetorizado).")
        
        # Potência Ativa Total da Rede (Carga da instalação)
        # Como o PFC roda de forma isolada nesta etapa, a rede enxerga apenas a carga ativa
        p_rede = df_carga['Carga_W'].values
        
        q_carga = df_carga.get('Carga_VAr', pd.Series(0.0, index=df_carga.index)).values
        
        # 1. Calcular Q_alvo
        pf_safe = np.clip(pf_target, -1.0, 1.0)
        tan_phi = np.tan(np.arccos(np.abs(pf_safe)))
        q_alvo = np.sign(q_carga) * np.abs(p_rede) * tan_phi
        
        # 2. Q necessário
        q_req = q_alvo - q_carga
        
        # 3. Sobra do inversor (S_max)
        # Como não há despacho de potência ativa, toda a capacidade do inversor (VA) está disponível para reativos
        q_disp = s_max_va
        
        # 4. Clip limits
        q_bess = np.clip(q_req, -q_disp, q_disp)
        
        df_out = pd.DataFrame({
            coluna_tempo: df_carga[coluna_tempo] if coluna_tempo in df_carga.columns else df_carga.index,
            'Potencia_Reativa_Bateria_VAr': q_bess
        })
        
        logger.info("Cálculo de correção de fator de potência finalizado.")
        return df_out
