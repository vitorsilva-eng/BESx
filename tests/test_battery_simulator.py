"""
test_battery_simulator.py

Testes unitários para o módulo battery_simulator.py.
Verifica o comportamento da integração de Coulomb em cenários-chave.
"""

import sys
import os
import unittest
import numpy as np
import pandas as pd

# Add project root to path
# Adiciona o diretório 'src' ao sys.path para reconhecer o pacote 'besx'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "src"))

from besx.domain.models.battery_simulator import simular_soc_mes
from besx.config import BateriaConfig


# ---------------------------------------------------------------------- #
#  Configuração de bateria mínima para os testes                          #
# ---------------------------------------------------------------------- #
CFG_BAT_TESTE = {
    'Ah':       100.0,   # 100 Ah
    'Ns':       1,       # 1 módulo em série
    'Np':       1,       # 1 string em paralelo
    'soc_prof': [0.0, 0.5, 1.0],
    'ocv_prof': [3.0, 3.3, 3.6],  # V do banco (Ns=1)
    'soc_min':  0.10,   # 10%
    'soc_max':  0.90,   # 90%
    'capacidade_nominal_wh': 1000.0,
    'P_bess':   50_000.0,  # 50 kW
}

SOH_PLENO = 1.0   # 100%


def _df_mes_constante(p_w: float, n_passos: int = 60, dt_min: float = 1.0) -> pd.DataFrame:
    """
    Cria um DataFrame de potência constante em Watts.

    Args:
        p_w:      Potência em Watts (positivo=carga, negativo=descarga)
        n_passos: Número de amostras
        dt_min:   Intervalo de tempo em minutos

    Returns:
        DataFrame com colunas ['Tempo', 'Potencia_kW']
    """
    tempos = np.arange(n_passos) * dt_min  # minutos
    return pd.DataFrame({'Tempo': tempos, 'Potencia_kW': [p_w] * n_passos})


class TestSimularSOCMes(unittest.TestCase):

    # ------------------------------------------------------------------ #
    #  1. Estrutura da saída                                               #
    # ------------------------------------------------------------------ #
    def test_saida_tem_colunas_corretas(self):
        """A saída deve ter exatamente as colunas 'Tempo' e 'SOC'."""
        df_mes = _df_mes_constante(0.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)

        self.assertIn('Tempo', resultado.columns)
        self.assertIn('SOC', resultado.columns)

    def test_saida_tem_mesmo_numero_de_linhas(self):
        """O número de linhas da saída deve ser igual ao da entrada."""
        n = 120
        df_mes = _df_mes_constante(0.0, n_passos=n)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        self.assertEqual(len(resultado), n)

    def test_tempo_em_segundos(self):
        """Coluna Tempo deve estar em segundos (primeiro valor = 0 s)."""
        df_mes = _df_mes_constante(0.0, n_passos=60, dt_min=1.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        # Primeiro passo é t=0 min → 0 s
        self.assertAlmostEqual(resultado['Tempo'].iloc[0], 0.0, places=3)
        # Segundo passo é t=1 min → 60 s
        self.assertAlmostEqual(resultado['Tempo'].iloc[1], 60.0, places=3)

    def test_soc_em_percentual(self):
        """SOC deve estar em % (0–100), não em fração (0–1)."""
        df_mes = _df_mes_constante(0.0, n_passos=10)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        # Com SOC inicial = 0.5 → deve aparecer como 50.0, não 0.5
        self.assertAlmostEqual(resultado['SOC'].iloc[0], 50.0, places=2)

    # ------------------------------------------------------------------ #
    #  2. Condições iniciais                                               #
    # ------------------------------------------------------------------ #
    def test_soc_inicial_correto(self):
        """O primeiro valor de SOC deve corresponder ao soc_inicial fornecido."""
        soc_inicial = 0.65  # 65%
        df_mes = _df_mes_constante(0.0)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, soc_inicial, cfg)
        self.assertAlmostEqual(resultado['SOC'].iloc[0], soc_inicial * 100.0, places=2)

    def test_potencia_zero_soc_constante(self):
        """Com potência zero, o SOC deve permanecer constante ao longo do tempo."""
        soc_inicial = 0.5
        df_mes = _df_mes_constante(0.0, n_passos=100)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, soc_inicial, cfg)
        soc_series = resultado['SOC']
        self.assertTrue((soc_series == soc_series.iloc[0]).all(),
                        msg="SOC deve ser constante quando P=0")

    # ------------------------------------------------------------------ #
    #  3. Direção correta do SOC                                           #
    # ------------------------------------------------------------------ #
    def test_carga_aumenta_soc(self):
        """Potência positiva (carga) deve aumentar o SOC."""
        df_mes = _df_mes_constante(10000.0, n_passos=60)  # 10000 W (10 kW) de carga
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        soc_final = resultado['SOC'].iloc[-1]
        soc_inicial_saida = resultado['SOC'].iloc[0]
        self.assertGreater(soc_final, soc_inicial_saida,
                           msg="Carga deve aumentar o SOC")

    def test_descarga_diminui_soc(self):
        """Potência negativa (descarga) deve diminuir o SOC."""
        df_mes = _df_mes_constante(-10000.0, n_passos=60)  # -10000 W (-10 kW) de descarga
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg)
        soc_final = resultado['SOC'].iloc[-1]
        soc_inicial_saida = resultado['SOC'].iloc[0]
        self.assertLess(soc_final, soc_inicial_saida,
                        msg="Descarga deve diminuir o SOC")

    # ------------------------------------------------------------------ #
    #  4. Limites operacionais                                             #
    # ------------------------------------------------------------------ #
    def test_soc_nao_ultrapassa_socmax(self):
        """SOC nunca deve ultrapassar soc_max (90%)."""
        # Carga intensa (50000 W = 50 kW) por muito tempo, partindo de 80%
        df_mes = _df_mes_constante(50000.0, n_passos=500)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.8, cfg)
        soc_max_config = CFG_BAT_TESTE['soc_max'] * 100.0
        self.assertTrue(
            (resultado['SOC'] <= soc_max_config + 1e-6).all(),
            msg=f"SOC ultrapassou soc_max={soc_max_config}%"
        )

    def test_soc_nao_cai_abaixo_socmin(self):
        """SOC nunca deve cair abaixo de soc_min (10%)."""
        # Descarga intensa (-50000 W = -50 kW) por muito tempo, partindo de 20%
        df_mes = _df_mes_constante(-50000.0, n_passos=500)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        resultado = simular_soc_mes(df_mes, SOH_PLENO, 0.2, cfg)
        soc_min_config = CFG_BAT_TESTE['soc_min'] * 100.0
        self.assertTrue(
            (resultado['SOC'] >= soc_min_config - 1e-6).all(),
            msg=f"SOC caiu abaixo de soc_min={soc_min_config}%"
        )

    def test_potencia_limitada_por_p_bess(self):
        """Potência muito alta deve ser clipada ao valor de P_bess."""
        # Potência de 200000 W > P_bess de 50000 W → deve se comportar igual a 50000 W
        df_200kw = _df_mes_constante(200000.0, n_passos=60)
        df_50kw  = _df_mes_constante(50000.0,  n_passos=60)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        r200 = simular_soc_mes(df_200kw, SOH_PLENO, 0.5, cfg)
        r50  = simular_soc_mes(df_50kw,  SOH_PLENO, 0.5, cfg)
        np.testing.assert_array_almost_equal(
            r200['SOC'].to_numpy(), r50['SOC'].to_numpy(), decimal=4,
            err_msg="Potência deve ser limitada pelo P_bess"
        )

    # ------------------------------------------------------------------ #
    #  5. Efeito do SOH                                                    #
    # ------------------------------------------------------------------ #
    def test_soh_reduzido_aumenta_variacao_soc(self):
        """
        Com SOH reduzido a capacidade efetiva diminui,
        portanto a mesma carga provoca maior variação de SOC.
        """
        # Potência de 100 W para não saturar.
        df_mes = _df_mes_constante(100.0, n_passos=11)
        cfg = BateriaConfig(**CFG_BAT_TESTE)
        # SOH Pleno (1.0) vs SOH Reduzido (0.5)
        r_pleno     = simular_soc_mes(df_mes, 1.0, 0.5, cfg)
        r_degradado = simular_soc_mes(df_mes, 0.5, 0.5, cfg)

        delta_pleno     = r_pleno['SOC'].iloc[-1]     - r_pleno['SOC'].iloc[0]
        delta_degradado = r_degradado['SOC'].iloc[-1] - r_degradado['SOC'].iloc[0]

        # Com SOH 0.5, a variação deve ser o dobro da de SOH 1.0 (aproximadamente)
        self.assertGreater(
            delta_degradado, delta_pleno,
            msg="Bateria degradada deve ter maior variação de SOC para mesma potência"
        )

    # ------------------------------------------------------------------ #
    #  6. Conservação de energia (verificação analítica)                 #
    # ------------------------------------------------------------------ #
    def test_conservacao_energetica_carga_simples(self):
        """
        Verifica que a variação de SOC é próxima ao valor calculado analiticamente.
        """
        cfg_dict = CFG_BAT_TESTE.copy()
        cfg_dict['ocv_prof'] = [3.3, 3.3, 3.3]
        cfg_dict['soc_max']  = 0.99
        cfg_dict['rendimento_pcs'] = 1.0

        p_w     = 100.0
        n       = 11      # 10 intervalos de 1 min
        df_mes  = _df_mes_constante(p_w, n_passos=n, dt_min=1.0)
        Q_Ah    = cfg_dict['Ah'] * cfg_dict['Np'] * SOH_PLENO  # 100 Ah
        v_const = 3.3     
        i_A     = p_w / v_const  
        dt_h    = 1.0 / 60.0  
        delta_analitico = (i_A * dt_h * 10) / Q_Ah * 100.0  

        cfg_obj = BateriaConfig(**cfg_dict)
        resultado      = simular_soc_mes(df_mes, SOH_PLENO, 0.5, cfg_obj)
        delta_simulado = resultado['SOC'].iloc[-1] - resultado['SOC'].iloc[0]

        self.assertAlmostEqual(delta_simulado, delta_analitico, delta=0.5)

if __name__ == '__main__':
    unittest.main(verbosity=2)
