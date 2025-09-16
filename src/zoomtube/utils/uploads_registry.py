import json
from pathlib import Path
from datetime import datetime
from zoomtube.utils.logger import logger

# Carpeta y archivo de estado
STATE_DIR = Path(__file__).resolve().parents[2] / "state"
UPLOADS_FILE = STATE_DIR / "uploads.json"


def _ensure_file():
    """Crea la carpeta/archivo si no existen."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not UPLOADS_FILE.exists():
        with open(UPLOADS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load() -> list[dict]:
    """Carga el registro completo desde JSON."""
    _ensure_file()
    with open(UPLOADS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]) -> None:
    """Guarda el registro completo en JSON."""
    with open(UPLOADS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_uploaded(local_path: str) -> bool:
    """
    Verifica si un archivo ya fue subido con éxito.
    """
    records = _load()
    for r in records:
        if r["local_path"] == local_path and r["status"] == "success":
            return True
    return False


def register_upload(local_path: str, youtube_id: str, title: str, status: str) -> None:
    """
    Registra una subida (exitosa o fallida).

    Args:
        local_path: ruta al archivo de video en disco.
        youtube_id: ID del video en YouTube (None si falló).
        title: título usado en la subida.
        status: "success" o "failed".
    """
    records = _load()

    entry = {
        "local_path": local_path,
        "youtube_id": youtube_id,
        "title": title,
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
    }
    records.append(entry)
    _save(records)

    logger.info(f"Registro actualizado: {local_path} → {status}")


def get_all_uploads() -> list[dict]:
    """
    Devuelve todos los registros (puede usarse para reportes).
    """
    return _load()
