
from besx.application.simulation import SimulationManager
from besx.entrypoints.cli.menu import exibir_menu_inicial
from besx.config import CONFIGURACAO, PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

if __name__ == "__main__":
    logger.info(">>> Iniciando BESx Simulation App <<<")

    # --- Menu inicial: escolha de bateria e backend ---
    perfil_ativo, backend = exibir_menu_inicial()

    # Atualiza a configuração com o perfil de bateria escolhido
    CONFIGURACAO.bateria = PERFIS_BATERIA[perfil_ativo]

    logger.info(f"Perfil: {perfil_ativo} | Backend: {backend}")

    # --- Inicia a simulação ---
    sim = SimulationManager(CONFIGURACAO, backend=backend)
    sim.run()
