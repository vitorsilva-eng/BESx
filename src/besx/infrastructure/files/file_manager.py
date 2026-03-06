
import os
import datetime
import shutil
from typing import Optional
from besx.infrastructure.logging.logger import logger

class FileManager:
    def __init__(self, base_path: Optional[str] = None, resume_folder: Optional[str] = None) -> None:
        """
        Gerencia a estrutura de pastas e arquivos da simulação.
        
        Cria uma nova pasta para cada execução baseada no timestamp,
        ou reutiliza uma pasta existente se resume_folder for fornecido.
        Ex: results/sim_20231027_103000/
        """
        from besx.config import PATH_RESULTS
        self.base_path = base_path or PATH_RESULTS
        
        if resume_folder:
            self.sim_folder = os.path.join(self.base_path, resume_folder)
            # Extrai o timestamp da pasta (assume formato padrão sim_YYYYMMDD_HHMMSS)
            if resume_folder.startswith("sim_"):
                self.timestamp = resume_folder[4:]
            else:
                self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.sim_folder = os.path.join(self.base_path, f"sim_{self.timestamp}")
        
        # Subpastas
        self.plots_folder = os.path.join(self.sim_folder, "plots")
        self.debug_folder = os.path.join(self.sim_folder, "debug")
        self.data_folder = os.path.join(self.sim_folder, "data")
        
        self._create_structure()
        
    def _create_structure(self) -> None:
        """Cria as pastas necessárias."""
        os.makedirs(self.plots_folder, exist_ok=True)
        os.makedirs(self.debug_folder, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)
        logger.info(f"Diretório da simulação criado: {self.sim_folder}")

    def get_debug_path(self, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de debug."""
        return os.path.join(self.debug_folder, filename)

    def get_plot_path(self, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de plot."""
        return os.path.join(self.plots_folder, filename)

    def get_data_path(self, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de dados (ex: .mat intermediário)."""
        return os.path.join(self.data_folder, filename)
    
    def save_report(self, content: str, filename: str = "report.txt") -> str:
        """Salva o relatório final da simulação."""
        report_path = os.path.join(self.sim_folder, filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path
