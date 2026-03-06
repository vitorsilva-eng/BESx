"""
menu.py  —  Menu Inicial Interativo do BESx

Responsabilidade: apresentar ao usuário as opções de configuração antes
de iniciar a simulação. Retorna as escolhas para que main.py possa
atualizar o CONFIGURACAO e instanciar o SimulationManager corretamente.

Opções:
  1. Perfil de bateria  (qualquer chave definida em PERFIS_BATERIA)
  2. Backend de simulação  ("plecs" | "python")
"""

from besx.config import PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

# Constantes de backend exportadas para uso nos outros módulos
BACKEND_PLECS  = "plecs"
BACKEND_PYTHON = "python"

_BACKENDS_DISPONIVEIS = {
    "1": BACKEND_PYTHON,
    "2": BACKEND_PLECS,
}

_DESCRICOES_BACKEND = {
    BACKEND_PYTHON: "Simulador Python  (integração de Coulomb — sem PLECS)",
    BACKEND_PLECS:  "PLECS via XML-RPC (requer PLECS aberto em localhost:1080)",
}


def exibir_menu_inicial() -> tuple[str, str]:
    """
    Exibe o menu interativo em loop até o usuário confirmar.

    Returns:
        tuple: (perfil_ativo, backend)
            - perfil_ativo (str): chave de PERFIS_BATERIA escolhida
            - backend      (str): BACKEND_PYTHON | BACKEND_PLECS
    """
    _imprimir_cabecalho()

    while True:
        perfil_ativo = _selecionar_perfil_bateria()
        backend      = _selecionar_backend()

        if _confirmar_selecao(perfil_ativo, backend):
            return perfil_ativo, backend

        print()
        print("  ↩  Reiniciando configuração...\n")


# ------------------------------------------------------------------ #
#  Seções internas do menu                                            #
# ------------------------------------------------------------------ #

def _imprimir_cabecalho() -> None:
    print()
    print("=" * 58)
    print("      BESx — Battery Energy Storage Simulator")
    print("      Configuração Inicial")
    print("=" * 58)


def _selecionar_perfil_bateria() -> str:
    """Pergunta qual perfil de bateria usar e retorna a chave escolhida."""
    perfis = list(PERFIS_BATERIA.keys())

    print()
    print("┌─ [ 1 / 2 ]  PERFIL DE BATERIA ─────────────────────────────")
    for idx, chave in enumerate(perfis, start=1):
        cfg  = PERFIS_BATERIA[chave]
        ah   = getattr(cfg, "Ah", "?")
        ns   = getattr(cfg, "Ns", "?")
        np_  = getattr(cfg, "Np", "?")
        pwr  = getattr(cfg, "P_bess", 0) / 1000.0
        cap  = getattr(cfg, "capacidade_nominal_wh", 0) / 1000.0
        print(f"│  [{idx}] {chave}")
        print(f"│       {ah} Ah  |  {ns}S × {np_}P  |  {pwr:.0f} kW  |  {cap:.1f} kWh")
    print("└─────────────────────────────────────────────────────────────")

    while True:
        entrada = input(f"\n  Escolha o perfil [1–{len(perfis)}]: ").strip()
        try:
            idx = int(entrada) - 1
            if 0 <= idx < len(perfis):
                escolhido = perfis[idx]
                logger.info(f"Perfil de bateria selecionado: {escolhido}")
                return escolhido
        except ValueError:
            pass
        print(f"  ⚠  Opção inválida. Digite um número entre 1 e {len(perfis)}.")


def _selecionar_backend() -> str:
    """Pergunta qual backend de simulação usar e retorna a constante."""
    print()
    print("┌─ [ 2 / 2 ]  BACKEND DE SIMULAÇÃO ──────────────────────────")
    for key, backend in _BACKENDS_DISPONIVEIS.items():
        print(f"│  [{key}] {_DESCRICOES_BACKEND[backend]}")
    print("└─────────────────────────────────────────────────────────────")

    while True:
        entrada = input("\n  Escolha o backend [1–2]: ").strip()
        if entrada in _BACKENDS_DISPONIVEIS:
            escolhido = _BACKENDS_DISPONIVEIS[entrada]
            logger.info(f"Backend selecionado: {escolhido}")
            return escolhido
        print("  ⚠  Opção inválida. Digite 1 ou 2.")


def _confirmar_selecao(perfil_ativo: str, backend: str) -> bool:
    """Exibe o resumo e pede confirmação. Retorna True se confirmado."""
    cfg = PERFIS_BATERIA[perfil_ativo]
    print()
    print("┌─ RESUMO DA CONFIGURAÇÃO ────────────────────────────────────")
    print(f"│  Bateria : {perfil_ativo}")
    print(f"│  Backend : {_DESCRICOES_BACKEND[backend]}")
    print(f"│  Capacid.: {getattr(cfg, 'Ah', '?')} Ah × "
          f"{getattr(cfg, 'Ns', '?')}S × {getattr(cfg, 'Np', '?')}P  "
          f"({getattr(cfg, 'capacidade_nominal_wh', 0)/1000:.1f} kWh)")
    print(f"│  P_bess  : {getattr(cfg, 'P_bess', 0)/1000:.1f} kW")
    print("└─────────────────────────────────────────────────────────────")

    resp = input("\n  Iniciar simulação com essa configuração? [S/n]: ").strip().lower()
    return resp in ("", "s", "sim", "y", "yes")
