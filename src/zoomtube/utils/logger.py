# src/zoom2yt/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import platform

def _get_log_dir() -> Path:
    """
    Devuelve el directorio de logs según SO.
    """
    system = platform.system().lower()

    if system == "windows":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        log_dir = base / "zoom2yt" / "logs"
    elif system == "darwin":  # macOS
        log_dir = Path.home() / "Library" / "Logs" / "zoom2yt"
    else:  # Linux y otros
        log_dir = Path.home() / ".local" / "share" / "zoom2yt" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_logger(name: str = "zoom2yt", verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """
    Configura un logger con salida a consola y archivo rotativo.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # ya configurado

    logger.setLevel(logging.DEBUG)

    # --- Consola ---
    console_handler = logging.StreamHandler()

    if quiet:
        console_handler.setLevel(logging.ERROR)
    elif verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)

    # --- Archivo ---
    log_file = _get_log_dir() / "zoom2yt.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_fmt)

    # Agregar handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Logger por defecto
logger = get_logger()
