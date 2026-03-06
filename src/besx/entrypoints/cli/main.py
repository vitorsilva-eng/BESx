import sys
import argparse

from besx.application.simulation import SimulationManager
from besx.entrypoints.cli.menu import exibir_menu_inicial
from besx.config import CONFIGURACAO, PERFIS_BATERIA
from besx.infrastructure.logging.logger import logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BESx Simulation Engine")
    parser.add_argument("--perfil", type=str, help="Perfil da bateria (ex: Sany_314Ah, LiFePO4_78Ah)")
    parser.add_argument("--backend", type=str, choices=["python", "plecs"], help="Backend de simulação")
    parser.add_argument("--resume", type=str, help="Nome da pasta para retomar simulação (ex: sim_20231027_103000)")
    return parser.parse_args()

if __name__ == "__main__":
    logger.info(">>> Iniciando BESx Simulation App <<<")
    
    args = parse_args()

    # --- Lógica de Roteamento ---
    # Se perfil e backend não forem passados simultaneamente, vai para o menu, MESMO que --resume seja passado.
    if args.perfil and args.backend:
        perfil_ativo = args.perfil
        backend = args.backend
        
        if perfil_ativo not in PERFIS_BATERIA:
            logger.error(f"Perfil '{perfil_ativo}' não encontrado. Opções disponíveis: {list(PERFIS_BATERIA.keys())}")
            sys.exit(1)
    else:
        # --- Menu inicial: escolha de bateria e backend ---
        logger.info("Faltam argumentos '--perfil' ou '--backend'. Iniciando fallback para o menu interativo.")
        perfil_ativo, backend = exibir_menu_inicial()

    # Atualiza a configuração com o perfil de bateria escolhido
    CONFIGURACAO.bateria = PERFIS_BATERIA[perfil_ativo]

    resume_folder_msg = f" | Resume: {args.resume}" if args.resume else ""
    logger.info(f"Perfil: {perfil_ativo} | Backend: {backend}{resume_folder_msg}")

    # --- Inicia a simulação ---
    sim = SimulationManager(CONFIGURACAO, backend=backend, resume_folder=args.resume)
    sim.run()
