import os
import json
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

# ============================================================
#  ▶  ALTERE AQUI PARA TROCAR O MODELO DE BATERIA  ◀
# ============================================================
PERFIL_ATIVO = "LiFePO4_78Ah"
# ============================================================

# --- Classes de Configuração (Pydantic) ---

class PlecsConfig(BaseModel):
    MODELO_PLECS: str = "bess_batch_mode"
    BLOCO_SOH_ALIAS: str = "SOH_Input"
    ARQUIVO_ENTRADA_POT: str = "potencia_mes_in.mat"
    ARQUIVO_SAIDA_SOC: str = "soc_out_mes.csv"
    Nfases: int = 3

class DadosEntradaConfig(BaseModel):
    ARQUIVO_MAT: str = "cmveditora.mat"
    dt_minutos: Union[str, float, int] = ""  # Pode ser string vazia inicial ou número
    dias_por_mes_sim: int = 30
    meses_por_ano_sim: int = 12
    dias_por_ano_avg: int = 360

class SimulacaoConfig(BaseModel):
    SOH_INICIAL_PERC: float = 100.0
    ANOS_SIMULACAO: int = 1
    MESES_SIMULACAO: Optional[int] = None
    data_inicio_simulacao: str = '2025-01-01 00:00:00'

class BateriaConfig(BaseModel):
    model_config = {"populate_by_name": True}
    capacidade_nominal_wh: float
    capacidade_limite_perda_perc: float = 20.0
    Tbat_kelvin: float = 298.15
    Tbat_kelvin_idle: float = 298.15
    soc_min: float = Field(default=0.2, alias="soc_min")
    soc_max: float = Field(default=0.8, alias="soc_max")
    Rs: Optional[float] = None
    Ah: Optional[float] = None
    Ns: Optional[int] = None
    Np: Optional[int] = None
    v_min_celula: Optional[float] = Field(default=None, alias="Vbmin")
    v_max_celula: Optional[float] = Field(default=None, alias="Vbmax")
    P_bess: Optional[float] = None
    soc_prof: Optional[List[float]] = None
    ocv_prof: Optional[List[float]] = None
    rendimento_pcs: float = 0.88

class DegradacaoCicloConfig(BaseModel):
    a: float = 2.6418
    b: float = -0.01943
    c: float = 0.004
    d: float = 0.01705
    g: float = 0.0123
    h: float = 0.7162
    exp_cycle: float = 2.0
    peak_prominence: float = 0.01
    range_round_dp: int = 1
    mean_round_dp: int = 1

class DegradacaoCalendarioConfig(BaseModel):
    k_T: float = 1.9775e-11
    exp_T: float = 0.07511
    k_soc: float = 1.639
    exp_soc: float = 0.007388
    exp_cal: float = 1.25  # 10/8

class ModeloDegradacaoConfig(BaseModel):
    ciclo: DegradacaoCicloConfig = Field(default_factory=DegradacaoCicloConfig)
    calendario: DegradacaoCalendarioConfig = Field(default_factory=DegradacaoCalendarioConfig)

class PathsConfig(BaseModel):
    data: str = "data"
    sim: str = "sim"
    debug: str = "debug"
    plots: str = "plots"
    relatorio: str = "relatorio"

class RelatorioConfig(BaseModel):
    gerar_validacao_detalhada: bool = True
    incluir_calculos_intermediarios: bool = True

class LLMConfig(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

class Settings(BaseModel):
    plecs: PlecsConfig = Field(default_factory=PlecsConfig)
    dados_entrada: DadosEntradaConfig = Field(default_factory=DadosEntradaConfig)
    simulacao: SimulacaoConfig = Field(default_factory=SimulacaoConfig)
    bateria: Optional[BateriaConfig] = None
    modelo_degradacao: ModeloDegradacaoConfig = Field(default_factory=ModeloDegradacaoConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    relatorio: RelatorioConfig = Field(default_factory=RelatorioConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)

# --- Carregamento de Perfis de Bateria ---
# --- Caminhos Base ---
from pathlib import Path

# O arquivo config.py está em src/besx/config.py
# ROOT_DIR deve apontar para a raiz do projeto
CWD = Path(__file__).parent.resolve()
ROOT_DIR = CWD.parent.parent.resolve()

PATH_BATTERIES = CWD / "resources" / "batteries.json"
PATH_DATABASE = ROOT_DIR / "database"
PATH_RESULTS = ROOT_DIR / "results"

try:
    with open(PATH_BATTERIES, "r", encoding="utf-8") as f:
        PERFIS_BATERIA_RAW = json.load(f)
        # Converte para dict de BateriaConfig para validação imediata
        PERFIS_BATERIA = {k: BateriaConfig(**v) for k, v in PERFIS_BATERIA_RAW.items()}
except Exception as e:
    # Fallback básico caso o arquivo não exista ou esteja corrompido
    fallback_perfil = BateriaConfig(
        capacidade_nominal_wh=10000.0,
        capacidade_limite_perda_perc=20.0,
        Tbat_kelvin=298.15,
        Tbat_kelvin_idle=298.15,
        soc_min=0.2, soc_max=0.8
    )
    PERFIS_BATERIA = {"Default_LFP": fallback_perfil}
    from besx.infrastructure.logging.logger import logger
    logger.warning(f"Falha ao carregar batteries.json ({e}). Usando perfil de segurança.")
# Valida o perfil escolhido antes de montar a configuração final
if PERFIL_ATIVO not in PERFIS_BATERIA:
    raise ValueError(
        f"PERFIL_ATIVO='{PERFIL_ATIVO}' não existe. "
        f"Opções disponíveis: {list(PERFIS_BATERIA.keys())}"
    )

# Instância Global de Configuração
CONFIGURACAO = Settings(
    bateria=PERFIS_BATERIA[PERFIL_ATIVO]
)
