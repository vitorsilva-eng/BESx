
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

from besx.domain.models.degradation_model import dano_ciclo, dano_calendar, acumular_dano, calcular_estatisticas_operacionais
from besx.config import CONFIGURACAO, DegradacaoCicloConfig, DegradacaoCalendarioConfig

class TestDegradationModel(unittest.TestCase):

    def setUp(self):
        # We don't need to clear CONFIGURACAO, just mock the values if needed
        # but better to pass params explicitly to functions where possible
        pass

    @patch('besx.domain.models.degradation_model.rainflow.extract_cycles')
    def test_dano_ciclo(self, mock_rainflow):
        """Test cycle damage calculation."""
        # Mock rainflow output: [(Range, Mean, Count, Start, End)]
        mock_rainflow.return_value = [(0.5, 0.5, 1, 0, 10)]
        
        # We need valid config objects
        params_ciclo = DegradacaoCicloConfig(
            a=1.0, b=0.0, c=1.0, d=0.0, g=1.0, h=1.0,
            range_round_dp=1, mean_round_dp=1
        )
        
        profile = [0, 1, 0]
        dano_total, _ = dano_ciclo(profile, Temp_kelvin=300, model_params=params_ciclo)
        
        self.assertAlmostEqual(dano_total, 0.5)

    def test_dano_calendar(self):
        """Test calendar damage calculation."""
        # Idle periods: 1 period of 1 month, SOC 0.5
        idle_periods = [{'t': 1, 't_meses': 1.0, 'SOC': 0.5}]
        
        params_cal = DegradacaoCalendarioConfig(
            k_T=1.0, exp_T=0.0, k_soc=1.0, exp_soc=0.0, exp_cal=1.0
        )
        
        dano, _ = dano_calendar(idle_periods, Tbat_kelvin=300, model_params=params_cal, dt_minutos=1.0, dias_por_ano_avg=360)
        
        self.assertEqual(dano, 1.0)

    def test_acumular_dano(self):
        """Test damage accumulation."""
        # sum of x^p + y^p ^ (1/p)
        # 3, 4, p=2 -> sqrt(9+16) = 5
        res = acumular_dano(3, 4, 2)
        self.assertEqual(res, 5)

if __name__ == '__main__':
    unittest.main()
