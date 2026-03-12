from abc import ABC, abstractmethod
import pandas as pd
from typing import List
from besx.application.ems.ems_engine import BessEMS
from besx.infrastructure.logging.logger import logger

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
        # Assumes df_carga already has the correct column names for the engine ('Carga_W' or passed via kwargs)
        col_carga = kwargs.get('load_col', 'Carga_W')
        df_out = bess_ems.gerar_perfil_load_shifting(df_carga, col_carga)
        return df_out

class PeakShavingStrategy(BaseStrategy):
    """Wrapper for the existing Peak Shaving algorithm."""
    
    def execute(self, df_carga: pd.DataFrame, bess_ems: BessEMS, **kwargs) -> pd.DataFrame:
        col_carga = kwargs.get('load_col', 'Carga_W')
        df_out = bess_ems.gerar_perfil_peak_shaving(df_carga, col_carga)
        return df_out


class EMSManager:
    """
    Manager class to handle data ingestion, validation, and strategy execution
    for the Battery Energy Storage System (BESS).
    """
    
    def __init__(self, strategies: List[BaseStrategy], p_bess_max_w: float, capacidade_nominal_wh: float):
        self.strategies = strategies
        self.p_bess_max_w = p_bess_max_w
        self.capacidade_nominal_wh = capacidade_nominal_wh
        self.bess_ems = BessEMS(p_bess_max_w=self.p_bess_max_w, capacidade_nominal_wh=self.capacidade_nominal_wh)
        
    def validate_and_prepare_input(self, df: pd.DataFrame, time_col: str, load_col: str) -> pd.DataFrame:
        """
        Validates the input DataFrame following strict rules (REQ-04 to REQ-08).
        
        Args:
            df: Raw input DataFrame.
            time_col: Name of the datetime column.
            load_col: Name of the load column.
            
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

        # REQ-08: kWh Inference heuristics
        # If mean values are around what would be the integral (Ah-throughput * dt / hours)
        # Assuming maximum powers in standard datasets vs integrated values
        # e.g.: If values are typical to Energy rather than Power (Values * dt ~ Power?) Let's be explicit and careful:
        # A simple check: if the user passes 'kW' but the magnitude is suspiciously low compared to 'kWh=kW*h',
        # However, a robust proxy is checking if `load_col` string has `kWh` in its name.
        if 'kwh' in str(load_col).lower():
            # If explicit that it's energy, auto convert
            logger.warning(f"Detected explicit kWh column '{load_col}'. Converting to kW using dt={dt_val:.4f}h.")
            df[load_col] = df[load_col] / dt_val
        elif df[load_col].mean() < (self.p_bess_max_w / 1000) * 0.1 and dt_val < 0.5:
             # Just a structural heuristic. We'll leave the robust conversion explicit.
             pass
             
        # Add basic mapping to 'Carga_W' if it doesn't exist
        if 'Carga_W' not in df.columns:
            if 'kw' in str(load_col).lower():
                df['Carga_W'] = df[load_col] * 1000
            else:
                 df['Carga_W'] = df[load_col]
            
        return df

    def run(self, df_carga: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Placeholder for Strategy Execution and Validation"""
        pass
