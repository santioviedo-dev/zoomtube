import json
from pathlib import Path
from datetime import datetime
from zoomtube.utils.logger import logger

# Carpeta y archivo de estado
STATE_DIR = Path(__file__).resolve().parents[2] / "state"
DOWNLOADS_FILE = STATE_DIR / "downloads.json"


def _ensure_file():
    """Crea la carpeta/archivo si no existen."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not DOWNLOADS_FILE.exists():
        with open(DOWNLOADS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load() -> list[dict]:
    """Carga el registro completo desde JSON."""
    _ensure_file()
    with open(DOWNLOADS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]) -> None:
    """Guarda el registro completo en JSON."""
    with open(DOWNLOADS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_download(local_path: str, topic: str, duration: int, status: str) -> None:
    """
    Registra o actualiza una descarga de grabación.

    Args:
        local_path: ruta donde se guardó la grabación.
        topic: nombre/título de la reunión.
        duration: duración en minutos.
        status: uno de:
            - "pending_audio_check"
            - "success"
            - "discarded_silence"
            - "failed"
    """
    records = _load()

    # Buscar si ya existe el registro para este archivo
    existing = next((r for r in records if r["local_path"] == local_path), None)

    entry = {
        "local_path": local_path,
        "topic": topic,
        "duration": duration,
        "downloaded_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
    }

    if existing:
        # Actualizar en lugar de duplicar
        records = [r if r["local_path"] != local_path else entry for r in records]
        action = "actualizado"
    else:
        records.append(entry)
        action = "creado"

    _save(records)
    logger.info(f"Registro de descarga {action}: {local_path} → {status}")


def get_all_downloads() -> list[dict]:
    """
    Devuelve todos los registros (puede usarse para reportes).
    """
    return _load()
