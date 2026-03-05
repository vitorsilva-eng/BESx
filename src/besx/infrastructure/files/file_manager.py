
import os
import datetime
import shutil
from besx.infrastructure.logging.logger import logger

class FileManager:
    def __init__(self, base_path=None):
        """
        Gerencia a estrutura de pastas e arquivos da simulação.
        
        Cria uma nova pasta para cada execução baseada no timestamp.
        Ex: results/sim_20231027_103000/
        """
        from besx.config import PATH_RESULTS
        self.base_path = base_path or PATH_RESULTS
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sim_folder = os.path.join(self.base_path, f"sim_{self.timestamp}")
        
        # Subpastas
        self.plots_folder = os.path.join(self.sim_folder, "plots")
        self.debug_folder = os.path.join(self.sim_folder, "debug")
        self.data_folder = os.path.join(self.sim_folder, "data")
        
        self._create_structure()
        
    def _create_structure(self):
        """Cria as pastas necessárias."""
        os.makedirs(self.plots_folder, exist_ok=True)
        os.makedirs(self.debug_folder, exist_ok=True)
        os.makedirs(self.data_folder, exist_ok=True)
        logger.info(f"Diretório da simulação criado: {self.sim_folder}")

    def get_debug_path(self, filename):
        """Retorna o caminho completo para um arquivo de debug."""
        return os.path.join(self.debug_folder, filename)

    def get_plot_path(self, filename):
        """Retorna o caminho completo para um arquivo de plot."""
        return os.path.join(self.plots_folder, filename)

    def get_data_path(self, filename):
        """Retorna o caminho completo para um arquivo de dados (ex: .mat intermediário)."""
        return os.path.join(self.data_folder, filename)
    
    def save_report(self, content, filename="report.txt"):
        """Salva o relatório final da simulação."""
        report_path = os.path.join(self.sim_folder, filename)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path
