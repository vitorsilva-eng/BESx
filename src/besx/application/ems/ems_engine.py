"""
Módulo do Sistema de Gerenciamento de Energia (EMS) da bateria.

Este módulo implementa algoritmos de despacho (Peak Shaving e Load Shifting) 
para pré-processar as curvas de carga da unidade consumidora, gerando o
perfil de potência da bateria que será utilizado no motor de simulação (BESx).
"""

import pandas as pd
import numpy as np
from typing import Optional, Union
from besx.infrastructure.logging.logger import logger

class BessEMS:
    """
    Sistema de Gerenciamento de Energia para Baterias (EMS).
    
    Esta classe implementa as estratégias de operação da bateria, como
    Load Shifting (Arbitragem) e Peak Shaving (Corte de Pico), antes
    da simulação dinâmica de degradação.
    
    Attributes:
        p_bess_max_w (float): Potência máxima de carga/descarga do inversor em Watts.
        capacidade_nominal_wh (float): Capacidade nominal de energia em Watt-hora.
    """
    
    def __init__(self, p_bess_max_w: float, capacidade_nominal_wh: float) -> None:
        """
        Inicializa o EMS com os parâmetros físicos do BESS.
        
        Args:
            p_bess_max_w (float): Potência máxima de carga/descarga (Watts).
            capacidade_nominal_wh (float): Capacidade de energia do banco (Watt-hora).
        """
        self.p_bess_max_w = p_bess_max_w
        self.capacidade_nominal_wh = capacidade_nominal_wh
        logger.info(f"BessEMS inicializado: P_max={p_bess_max_w}W, E_nom={capacidade_nominal_wh}Wh")

    def _calcular_dt_horas(self, df: pd.DataFrame, time_col: str) -> float:
        """
        Calcula o passo de tempo médio em horas a partir do DataFrame.
        """
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            tempos = pd.to_datetime(df[time_col])
        else:
            tempos = df[time_col]
        
        # Considera a diferença mediana para evitar distorções de eventuais falhas
        diffs = tempos.diff().dropna()
        if diffs.empty:
            return 1.0  # valor padrão se não puder determinar
        
        dt_horas = diffs.median().total_seconds() / 3600.0
        return dt_horas

    def gerar_perfil_load_shifting(
        self, 
        df_carga: pd.DataFrame, 
        hora_inicio_carga: int, 
        hora_fim_carga: int, 
        hora_inicio_descarga: int, 
        hora_fim_descarga: int,
        limite_demanda_kw: float,
        coluna_tempo: str = 'Time',
        coluna_carga_kw: str = 'Load_kW'
    ) -> pd.DataFrame:
        """
        Aplica a estratégia de Load Shifting (Arbitragem de Tempo de Uso).
        
        A bateria é carregada durante a janela de carga até atingir a capacidade,
        limitada de tal forma que a potência da carga + potência da bateria <= limite_demanda_kw.
        Durante a janela de descarga, a bateria é descarregada limitando-se à potência 
        da carga ou à potência máxima do inversor.
        
        Args:
            df_carga (pd.DataFrame): DataFrame com a curva de carga da unidade.
            hora_inicio_carga (int): Hora em que se inicia a carga (0-23).
            hora_fim_carga (int): Hora em que se encerra a carga (0-23).
            hora_inicio_descarga (int): Hora em que se inicia a descarga (0-23).
            hora_fim_descarga (int): Hora em que se encerra a descarga (0-23).
            limite_demanda_kw (float): Limite de potência total (consumo + carga da bateria) em kW.
            coluna_tempo (str): Nome da coluna de tempo no DataFrame.
            coluna_carga_kw (str): Nome da coluna com os dados de carga em kW.
            
        Returns:
            pd.DataFrame: Novo DataFrame contendo a coluna de tempo original e 'Potencia_Bateria_W'.
        """
        logger.info("Iniciando processamento de Load Shifting.")
        
        df = df_carga.copy()
        
        if not pd.api.types.is_datetime64_any_dtype(df[coluna_tempo]):
            df['datetime_temp'] = pd.to_datetime(df[coluna_tempo])
        else:
            df['datetime_temp'] = df[coluna_tempo]
            
        horas = df['datetime_temp'].dt.hour
        dt_h = self._calcular_dt_horas(df, 'datetime_temp')
        
        potencia_bat_w = np.zeros(len(df))
        carga_w = df[coluna_carga_kw].values * 1000.0  # Converte kW para W
        limite_demanda_w = limite_demanda_kw * 1000.0  # Converte kW para W
        
        energia_virtual_wh = 0.0  # Estado virtual de energia (0 a nominal)
        
        for i in range(len(df)):
            hora_atual = horas.iloc[i]
            p_load = carga_w[i]
            
            # Lógica de Janela (trata passagens pela meia-noite)
            is_carga = False
            if hora_inicio_carga < hora_fim_carga:
                is_carga = hora_inicio_carga <= hora_atual < hora_fim_carga
            else:
                is_carga = hora_atual >= hora_inicio_carga or hora_atual < hora_fim_carga
                
            is_descarga = False
            if hora_inicio_descarga < hora_fim_descarga:
                is_descarga = hora_inicio_descarga <= hora_atual < hora_fim_descarga
            else:
                is_descarga = hora_atual >= hora_inicio_descarga or hora_atual < hora_fim_descarga
                
            # Ação de Carga
            if is_carga:
                espaco_livre_wh = self.capacidade_nominal_wh - energia_virtual_wh
                folga_demanda_w = limite_demanda_w - p_load
                
                if espaco_livre_wh > 0 and folga_demanda_w > 0:
                    pot_max_energia = espaco_livre_wh / dt_h
                    p_req_w = min(self.p_bess_max_w, pot_max_energia, folga_demanda_w)
                    potencia_bat_w[i] = p_req_w
                    energia_virtual_wh += p_req_w * dt_h
                else:
                    potencia_bat_w[i] = 0.0
                    
            # Ação de Descarga
            elif is_descarga:
                if energia_virtual_wh > 0:
                    p_load = carga_w[i]
                    p_des_disp_w = min(self.p_bess_max_w, p_load)
                    pot_desc_energia_w = min(p_des_disp_w, energia_virtual_wh / dt_h)
                    
                    potencia_bat_w[i] = -pot_desc_energia_w  # Descarga é negativa
                    energia_virtual_wh -= pot_desc_energia_w * dt_h
                else:
                    potencia_bat_w[i] = 0.0
            else:
                potencia_bat_w[i] = 0.0
                
            energia_virtual_wh = max(0.0, min(self.capacidade_nominal_wh, energia_virtual_wh))

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
        coluna_tempo: str = 'Time',
        coluna_carga_kw: str = 'Load_kW'
    ) -> pd.DataFrame:
        """
        Aplica a estratégia de Peak Shaving (Corte de Pico).
        
        A bateria supre a demanda que ultrapassa o limite especificado,
        descarregando. Caso a demanda esteja abaixo, recarrega a bateria
        se houver espaço.
        
        Args:
            df_carga (pd.DataFrame): DataFrame com a curva de carga da unidade.
            limite_demanda_kw (float): Limite de demanda contratada em kW.
            coluna_tempo (str): Nome da coluna de tempo no DataFrame.
            coluna_carga_kw (str): Nome da coluna com os dados de carga em kW.
            
        Returns:
            pd.DataFrame: Novo DataFrame contendo a coluna de tempo original e 'Potencia_Bateria_W'.
        """
        logger.info(f"Iniciando processamento de Peak Shaving com limite {limite_demanda_kw} kW.")
        
        df = df_carga.copy()
        
        if not pd.api.types.is_datetime64_any_dtype(df[coluna_tempo]):
            df['datetime_temp'] = pd.to_datetime(df[coluna_tempo])
        else:
            df['datetime_temp'] = df[coluna_tempo]
            
        dt_h = self._calcular_dt_horas(df, 'datetime_temp')
        
        potencia_bat_w = np.zeros(len(df))
        carga_w = df[coluna_carga_kw].values * 1000.0
        limite_demanda_w = limite_demanda_kw * 1000.0
        
        energia_virtual_wh = self.capacidade_nominal_wh 
        
        for i in range(len(df)):
            p_load = carga_w[i]
            
            if p_load > limite_demanda_w:
                if energia_virtual_wh > 0:
                    p_req_descarga_w = p_load - limite_demanda_w
                    p_des_w = min(p_req_descarga_w, self.p_bess_max_w)
                    p_des_w = min(p_des_w, energia_virtual_wh / dt_h)
                    
                    potencia_bat_w[i] = -p_des_w
                    energia_virtual_wh -= p_des_w * dt_h
                else:
                    potencia_bat_w[i] = 0.0
            
            elif p_load < limite_demanda_w:
                espaco_livre_wh = self.capacidade_nominal_wh - energia_virtual_wh
                if espaco_livre_wh > 0:
                    folga_carga_w = limite_demanda_w - p_load
                    p_car_w = min(folga_carga_w, self.p_bess_max_w)
                    p_car_w = min(p_car_w, espaco_livre_wh / dt_h)
                    
                    potencia_bat_w[i] = p_car_w
                    energia_virtual_wh += p_car_w * dt_h
                else:
                    potencia_bat_w[i] = 0.0
            else:
                potencia_bat_w[i] = 0.0
                
            energia_virtual_wh = max(0.0, min(self.capacidade_nominal_wh, energia_virtual_wh))

        df_out = pd.DataFrame({
            coluna_tempo: df[coluna_tempo],
            'Potencia_Bateria_W': potencia_bat_w
        })
        
        logger.info("Cálculo de Peak Shaving finalizado.")
        return df_out
