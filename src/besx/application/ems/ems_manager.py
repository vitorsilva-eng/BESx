from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import List
from besx.application.ems.ems_engine import BessEMS
from besx.infrastructure.logging.logger import logger
from besx.config import CONFIGURACAO

class BaseStrategy(ABC):
    """Abstract Base Class for EMS Strategies."""
    
    @abstractmethod
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        """
        Executes the specific EMS strategy.
        
        Args:
            df_carga: Validated DataFrame containing the load data.
            bess_ems: The BessEMS engine instance.
            **kwargs: Additional parameters for the strategy.
            
        Returns:
            DataFrame containing the strategy output (typically adding/modifying `Potencia_Bateria_W`).
        """
        pass

class LoadShiftingStrategy(BaseStrategy):
    """Wrapper for the existing Load Shifting algorithm."""
    
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        col_tempo = kwargs.get('time_col', 'Time')
        col_carga = kwargs.get('load_col', 'Carga_W')
        
        df_out = bess_ems.gerar_perfil_load_shifting(
            df_carga=df_carga,
            hora_inicio_carga=kwargs.get('hora_inicio_carga', 0),
            hora_fim_carga=kwargs.get('hora_fim_carga', 0),
            hora_inicio_descarga=kwargs.get('hora_inicio_descarga', 0),
            hora_fim_descarga=kwargs.get('hora_fim_descarga', 0),
            limite_demanda_kw=kwargs.get('limite_demanda_kw', 0.0),
            ignorar_fins_de_semana=kwargs.get('ignorar_fins_de_semana', True),
            feriados=kwargs.get('feriados', None),
            coluna_tempo=col_tempo,
            coluna_carga=col_carga
        )
        return df_out

class PeakShavingStrategy(BaseStrategy):
    """Wrapper for the existing Peak Shaving algorithm."""
    
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        col_tempo = kwargs.get('time_col', 'Time')
        col_carga = kwargs.get('load_col', 'Carga_W')
        limite = kwargs.get('limite_demanda_kw', 0.0)
        faixa_kw = kwargs.get('faixa_seguranca_kw', 0.0)
        faixa_pct = kwargs.get('faixa_seguranca_pct', 0.0)
        
        df_out = bess_ems.gerar_perfil_peak_shaving(
            df_carga=df_carga,
            limite_demanda_kw=limite,
            faixa_seguranca_kw=faixa_kw,
            faixa_seguranca_pct=faixa_pct,
            coluna_tempo=col_tempo,
            coluna_carga=col_carga
        )
        return df_out

class PowerFactorCorrectionStrategy(BaseStrategy):
    """Wrapper for the Power Factor Correction algorithm."""
    
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        col_tempo = kwargs.get('time_col', 'Time')
        pf_target = kwargs.get('pf_target', 1.0)
        s_max_va = kwargs.get('s_max_va', 1e9) # Default to huge capacity if not provided, though it should be
        
        df_out = bess_ems.gerar_perfil_power_factor_correction(
            df_carga=df_carga,
            pf_target=pf_target,
            s_max_va=s_max_va,
            coluna_tempo=col_tempo
        )
        return df_out


class CombinedStrategyLSPS(BaseStrategy):
    """Wrapper for the Combined Load Shifting & Peak Shaving algorithm."""
    
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        col_tempo = kwargs.get('time_col', 'Time')
        col_carga = kwargs.get('load_col', 'Carga_W')
        
        df_out = bess_ems.gerar_perfil_combinado_ls_ps(
            df_carga=df_carga,
            limite_demanda_kw=kwargs.get('limite_demanda_kw', 0.0),
            hora_inicio_carga=kwargs.get('hora_inicio_carga', 0),
            hora_fim_carga=kwargs.get('hora_fim_carga', 0),
            hora_inicio_descarga=kwargs.get('hora_inicio_descarga', 0),
            hora_fim_descarga=kwargs.get('hora_fim_descarga', 0),
            faixa_seguranca_kw=kwargs.get('faixa_seguranca_kw', 0.0),
            faixa_seguranca_pct=kwargs.get('faixa_seguranca_pct', 0.0),
            ignorar_fins_de_semana=kwargs.get('ignorar_fins_de_semana', True),
            feriados=kwargs.get('feriados', None),
            coluna_tempo=col_tempo,
            coluna_carga=col_carga
        )
        return df_out


class EMSManager:
    """
    Manager class to handle data ingestion, validation, and strategy execution
    for the Battery Energy Storage System (BESS).
    """
    
    def __init__(self, strategies: List[BaseStrategy], p_bess_max_w: float, capacidade_nominal_wh: float, s_inversor_va: float = None):
        self.strategies = strategies
        self.p_bess_max_w = p_bess_max_w
        self.capacidade_nominal_wh = capacidade_nominal_wh
        self.bess_ems = BessEMS()
        self.s_inversor_va = s_inversor_va if s_inversor_va is not None else self.p_bess_max_w
        
    def validate_and_prepare_input(self, df: pd.DataFrame, time_col: str, load_col: str, fp_col: str = None, q_col: str = None, va_col: str = None, unit: str = None) -> pd.DataFrame:
        """
        Validates the input DataFrame following strict rules (REQ-04 to REQ-08).
        
        Args:
            df: Raw input DataFrame.
            time_col: Name of the datetime column.
            load_col: Name of the load column.
            fp_col: Optional column name for Power Factor.
            q_col: Optional column name for Reactive Power (kVARh).
            va_col: Optional column name for Apparent Power (kVAh).
            
        Returns:
            Validated and standard-formatted DataFrame.
        """
        # REQ-04: Datetime
        try:
            df[time_col] = pd.to_datetime(df[time_col])
        except Exception as e:
            logger.error(f"Failed to parse datetime in column '{time_col}': {e}")
            raise ValueError(f"Datetime parsing failed for column '{time_col}'. Ensure it's coercible to datetime64.") from e

        # REQ-05: Numeric values only
        if not pd.api.types.is_numeric_dtype(df[load_col]):
            logger.error(f"Non-numeric values found in column '{load_col}'")
            raise ValueError(f"Column '{load_col}' must contain strictly numeric values.")

        # REQ-06: Reject NaNs explicitly without interpolating
        nan_indices = df[df[load_col].isna()].index.tolist()
        if nan_indices:
            logger.error(f"NaN values found at indices: {nan_indices}")
            raise ValueError(f"NaN values detected in '{load_col}' at indices: {nan_indices[:10]}... Please clean the data.")

        # Sort values by time to ensure calculations are continuous
        df = df.sort_values(by=time_col).reset_index(drop=True)

        # REQ-07: dt Uniformity validation
        dts = df[time_col].diff().dt.total_seconds() / 3600.0  # en hours
        dt_median = dts.median()
        
        # Checking variance exceeding ±5%
        if not dts.dropna().between(dt_median * 0.95, dt_median * 1.05).all():
            logger.warning(f"Variation in time-step (dt) exceeds ±5% of the median ({dt_median:.4f}h). Results may suffer precision loss.")
            
        # Ensure median dt works for calculation
        dt_val = dt_median if pd.notna(dt_median) else 1.0

        # REQ-08: Explicit unit conversion based on physical unit selected by the user
        raw_values = df[load_col].values
        
        # Falls back to heuristic detection if unit is not specified or not recognized
        if not unit or unit not in ["W", "kW", "Wh", "kWh"]:
            col_name_lower = str(load_col).lower()
            is_energy_name = any(x in col_name_lower for x in ['kwh', 'wh', 'energia', 'energy'])
            is_suspiciously_small = np.max(raw_values) < 5000.0
            
            if is_energy_name or is_suspiciously_small:
                unit = "kWh" if np.max(raw_values) < 1000000.0 else "Wh"
            else:
                unit = "kW" if np.max(raw_values) < 2000.0 else "W"
            logger.warning(f"REQ-08: No explicit unit specified. Heuristically detected '{unit}' for column '{load_col}'.")
            df.attrs['heuristic_detected_unit'] = unit
            
        df.attrs['original_unit'] = unit
        
        # Apply conversion/scaling mathematically based on selected unit
        if unit == "W":
            df['Carga_W'] = raw_values
        elif unit == "kW":
            df['Carga_W'] = raw_values * 1000.0
            df.attrs['scaling_applied'] = True
            logger.warning(f"REQ-08: Scaled active power column '{load_col}' from kW to Watts.")
        elif unit == "Wh":
            df['Carga_W'] = raw_values / dt_val
            df.attrs['conversion_applied'] = True
            logger.warning(f"REQ-08: Converted energy column '{load_col}' from Wh to Power (W) using dt={dt_val:.4f}h.")
        elif unit == "kWh":
            df['Carga_W'] = (raw_values * 1000.0) / dt_val
            df.attrs['conversion_applied'] = True
            logger.warning(f"REQ-08: Converted energy column '{load_col}' from kWh to Power (W) using dt={dt_val:.4f}h.")
        
        
        # --- OPTIONAL REACTIVE DATA PROCESSING ---
        if q_col and q_col in df.columns:
            # Assume kVARh (Energy) -> Convert to VAr (Power)
            df['Carga_VAr'] = (df[q_col] * 1000.0) / dt_val
            logger.info(f"Processed reactive column '{q_col}' as VAr using dt={dt_val:.4f}h.")
        
        if va_col and va_col in df.columns:
            # Assume kVAh (Energy) -> Convert to VA (Power)
            df['Carga_VA'] = (df[va_col] * 1000.0) / dt_val
            logger.info(f"Processed apparent column '{va_col}' as VA using dt={dt_val:.4f}h.")

        if fp_col and fp_col in df.columns:
            df['Carga_FP'] = pd.to_numeric(df[fp_col], errors='coerce').fillna(1.0)
            logger.info(f"Using column '{fp_col}' as Carga_FP.")
            
        # Power Triangle Inference
        has_fp = 'Carga_FP' in df.columns
        has_var = 'Carga_VAr' in df.columns
        has_va = 'Carga_VA' in df.columns
        w = df['Carga_W'].values
        
        if has_fp:
            fp = df['Carga_FP'].values
            fp_safe = np.where(fp == 0, 1e-9, fp)
            if not has_va:
                df['Carga_VA'] = w / fp_safe
            if not has_var:
                df['Carga_VAr'] = w * np.tan(np.arccos(np.clip(fp, -1.0, 1.0)))
        elif has_var:
            var = df['Carga_VAr'].values
            va = np.sqrt(w**2 + var**2)
            if not has_va:
                df['Carga_VA'] = va
            if not has_fp:
                df['Carga_FP'] = np.where(va == 0, 1.0, w / va)
        elif has_va:
            va = df['Carga_VA'].values
            if not has_var:
                df['Carga_VAr'] = np.sqrt(np.clip(va**2 - w**2, 0, None))
            if not has_fp:
                df['Carga_FP'] = np.where(va == 0, 1.0, w / va)
        else:
            # If no column was explicitly selected but we found a standard name earlier, use it
            # Otherwise default to zero
            if 'Carga_VAr' not in df.columns:
                df['Carga_VAr'] = 0.0
            if 'Carga_VA' not in df.columns:
                df['Carga_VA'] = df['Carga_W']
            if 'Carga_FP' not in df.columns:
                df['Carga_FP'] = 1.0
            
        return df

    def run(self, df_carga: pd.DataFrame, time_col: str, load_col: str, soc_inicial: float = 50.0, **kwargs) -> pd.DataFrame:
        """
        Validates data, executes strategies sequentially, and calculates heuristic metrics.
        
        Args:
            df_carga: Raw input DataFrame.
            time_col: Name of datetime column.
            load_col: Name of load column.
            fp_col: Optional column name for Power Factor.
            q_col: Optional column name for Reactive Power (kVARh).
            soc_inicial: Initial SOC in percentage (0 to 100). Default is 50.0.
            
        Returns:
            DataFrame with `Potencia_Bateria_W`, heuristic `SOC_Heuristico`, and other metrics.
        """
        # Step 1: Validation and Standardization
        df_processed = self.validate_and_prepare_input(
            df_carga.copy(), 
            time_col, 
            load_col, 
            fp_col=kwargs.get('fp_col'), 
            q_col=kwargs.get('q_col'),
            unit=kwargs.get('unit')
        )
        
        # Initialize Potencia_Bateria_W to 0 conceptually (no dispatch) if not present
        if 'Potencia_Bateria_W' not in df_processed.columns:
            df_processed['Potencia_Bateria_W'] = 0.0

        # Step 2: Sequential Execution of Strategies
        for strategy in self.strategies:
            # Merge self.s_inversor_va into kwargs for strategy execution
            current_kwargs = kwargs.copy()
            if 's_max_va' not in current_kwargs:
                current_kwargs['s_max_va'] = self.s_inversor_va
                
            # Execute the strategy and get ONLY the battery power result
            df_out = strategy.execute(df_processed, self.bess_ems, time_col=time_col, load_col='Carga_W', **current_kwargs)
            
            # Merge the result back into the main processed dataframe
            if 'Potencia_Bateria_W' in df_out.columns:
                df_processed['Potencia_Bateria_W'] = df_out['Potencia_Bateria_W'].values
                
            # Merge reactive power dispatch if present
            if 'Potencia_Reativa_Bateria_VAr' in df_out.columns:
                df_processed['Potencia_Reativa_Bateria_VAr'] = df_out['Potencia_Reativa_Bateria_VAr'].values

        # Step 3: Heuristic SOC integration (REQ-11)
        if 'Potencia_Bateria_W' not in df_processed.columns:
            logger.warning("No strategy defined Potencia_Bateria_W. Output will just reflect zero dispatch.")
            df_processed['Potencia_Bateria_W'] = 0.0

        # Create time deltas explicitly for integration
        dts_hours = df_processed[time_col].diff().dt.total_seconds() / 3600.0
        dts_hours = dts_hours.fillna(0.0)
        
        energy_wh = [0.0]  # Start balanced at 0.0
        
        for i in range(1, len(df_processed)):
            dt_h = dts_hours.iloc[i]
            potencia_ativa_w = df_processed['Potencia_Bateria_W'].iloc[i]
            potencia_reativa_var = df_processed.get('Potencia_Reativa_Bateria_VAr', pd.Series(0.0, index=df_processed.index)).iloc[i]
            
            # Cálculo de Potência Aparente e Perdas Estimadas (Heurístico)
            s_va = np.sqrt(potencia_ativa_w**2 + potencia_reativa_var**2)
            rendimento = getattr(CONFIGURACAO.bateria, 'rendimento_pcs', 0.88)
            perdas_w = s_va * (1.0 - rendimento)
            
            # Potência Total DC (Convenção: P > 0 Carga, P < 0 Descarga)
            # As perdas sempre aumentam a descarga ou diminuem a carga.
            potencia_total_dc_w = potencia_ativa_w - perdas_w
            
            # Integral: Energy[t] = Energy[t-1] + (Power[t] * dt)
            delta_kwh = (potencia_total_dc_w * dt_h) / 1000.0
            new_energy_kwh = energy_wh[-1] + delta_kwh
            energy_wh.append(new_energy_kwh)
            
        # Calculate Accumulated Energy Balance
        # Assigning as a list avoids index misalignment issues
        df_processed['Energia_Acumulada_kWh'] = energy_wh

        # Step 4: Final Calculations and Status
        # Carga Ajustada (Ponto de vista da rede: Carga + Bateria)
        df_processed['Carga_Ajustada_W'] = df_processed['Carga_W'] + df_processed['Potencia_Bateria_W']
        
        # Bateria em kW para exportação amigável
        df_processed['Bateria_kW'] = df_processed['Potencia_Bateria_W'] / 1000.0
        
        # Determine Status operacional (Convenção Ponto de Vista da Carga: Positivo = Carga)
        def get_status(p_w):
            if p_w > 0.1: return "CHARGE"
            if p_w < -0.1: return "DISCHARGE"
            return "IDLE"
            
        df_processed['Status'] = df_processed['Potencia_Bateria_W'].apply(get_status)
        
        return df_processed
