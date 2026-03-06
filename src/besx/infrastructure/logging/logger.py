
import logging
import colorlog
import sys

def setup_logger() -> logging.Logger:
    """
    Configura o logger principal com saída colorida no console.
    """
    logger = logging.getLogger("BESx")
    logger.setLevel(logging.DEBUG)

    # Evita duplicar handlers se o logger já estiver configurado
    if logger.hasHandlers():
        return logger

    # Handler do Console (Colorido)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
