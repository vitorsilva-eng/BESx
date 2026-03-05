
import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch

# Add project root to path
import sys
import os
# Adiciona o diretório 'src' ao sys.path para reconhecer o pacote 'besx'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src"))

from besx.infrastructure.loaders.data_handler import fatiar_dados_mensais
from besx.domain.models.battery_simulator import ciclos_idle, picos_e_vales
from besx.config import CONFIGURACAO

class TestDataHandler(unittest.TestCase):

    def setUp(self):
        # Setup configuration for tests
        # Pydantic models are usually updated via attribute access
        self.original_dt = CONFIGURACAO.dados_entrada.dt_minutos
        self.original_dias = CONFIGURACAO.dados_entrada.dias_por_ano_avg
        self.original_prominence = CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence
        
        CONFIGURACAO.dados_entrada.dt_minutos = 1
        CONFIGURACAO.dados_entrada.dias_por_ano_avg = 360
        CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence = 1.0

    def tearDown(self):
        # Restore configuration
        CONFIGURACAO.dados_entrada.dt_minutos = self.original_dt
        CONFIGURACAO.dados_entrada.dias_por_ano_avg = self.original_dias
        CONFIGURACAO.modelo_degradacao.ciclo.peak_prominence = self.original_prominence

    def test_ciclos_idle_basic(self):
        """Test basic idle detection with constant blocks."""
        # Profile: [10, 10, 10, 20, 20, 30]
        # Idle periods: 10 (3 samples), 20 (2 samples)
        profile = [10, 10, 10, 20, 20, 30]
        
        expected_idle = [
            {'t': 3, 'SOC': 10, 'index': 2}, # t=3 samples (indices 0, 1, 2)
            {'t': 2, 'SOC': 20, 'index': 4}  # t=2 samples (indices 3, 4)
        ]
        
        # Note: The logic in ciclos_idle calculates t_meses based on config
        # We focus on 't', 'SOC' and 'index' for correctness verification
        
        # O teste falhará se não passarmos dt_minutos e minutos_por_mes
        # pois a função agora aceita esses argumentos obrigatoriamente (ou quase)
        # Vamos conferir a assinatura no battery_simulator.py:
        # def ciclos_idle(profile: list, dt_minutos_soc: float, minutos_por_mes: float) -> list:
        
        result = ciclos_idle(profile, dt_minutos_soc=1.0, minutos_por_mes=43200)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['t'], 3)
        self.assertEqual(result[0]['SOC'], 10)
        self.assertEqual(result[1]['t'], 2)
        self.assertEqual(result[1]['SOC'], 20)

    def test_ciclos_idle_no_idle(self):
        """Test profile with no idle periods (changing every step)."""
        profile = [10, 11, 12, 13, 14]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 0)

    def test_ciclos_idle_full_idle(self):
        """Test profile that is entirely idle."""
        profile = [10, 10, 10, 10]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['t'], 4)

    def test_ciclos_idle_float_precision(self):
        """Test idle detection with floating point numbers."""
        # Exact floats
        profile = [10.5, 10.5, 12.0]
        result = ciclos_idle(profile, 1.0, 43200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['t'], 2)
        self.assertEqual(result[0]['SOC'], 10.5)

    def test_picos_e_vales(self):
        """Test peak and valley detection."""
        # Simple triangular wave: 0 -> 10 -> 0
        s = pd.Series([0, 5, 10, 5, 0])
        # With prominence 1.0 (default in setup), 10 is a peak, 0 are valleys/endpoints
        
        # The function returns the SIMPLIFIED profile (values at peaks/valleys)
        result = picos_e_vales(s)
        
        # It should preserve start [0], peak [10], and end [0]
        # Intermediate values [5, 5] should be removed if they are not peaks
        expected_values = [0, 10, 0]
        
        # Note: find_peaks behavior depends heavily on strict inequality and prominence.
        # 0 -> 10 -> 0: 10 is strictly greater than neighbors. Prominence check applies.
        
        # Let's verify what it returns.
        # indices: 0 (start), 2 (peak 10), 4 (end)
        # result: [0, 10, 0]
        
        np.testing.assert_array_equal(result, np.array(expected_values))

    def test_fatiar_dados_mensais(self):
        """Test slicing dataframe into monthly chunks."""
        # Mock config for 30 days/month, 1 min step -> 43200 lines/month
        # Let's force a smaller month for testing efficiency
        CONFIGURACAO.dados_entrada.dias_por_mes_sim = 1
        CONFIGURACAO.dados_entrada.dt_minutos = 60 # 1 hour steps
        # 1 day = 24 hours = 24 lines
        
        # Create DF with 50 lines (2 months + 2 lines remainder)
        df_total = pd.DataFrame({
            'Tempo': range(50), # 0..49
            'Potencia': range(50)
        })
        
        chunks = fatiar_dados_mensais(df_total)
        
        # Should result in 2 chunks of 24 lines each
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 24)
        self.assertEqual(len(chunks[1]), 24)
        
        # Check time reset behavior
        self.assertEqual(chunks[1].iloc[0]['Tempo'], 0) # Should be reset to 0

if __name__ == '__main__':
    unittest.main()
