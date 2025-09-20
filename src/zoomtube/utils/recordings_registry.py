import json
from pathlib import Path
from datetime import datetime
from zoomtube.utils.logger import logger

# Carpeta y archivo de estado
STATE_DIR = Path(__file__).resolve().parents[2] / "state"
RECORDINGS_FILE = STATE_DIR / "recordings.json"


def _ensure_file():
    """Crea la carpeta/archivo si no existen."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not RECORDINGS_FILE.exists():
        with open(RECORDINGS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _load() -> list[dict]:
    """Carga todas las reuniones registradas."""
    _ensure_file()
    with open(RECORDINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: list[dict]) -> None:
    """Guarda todas las reuniones en el archivo JSON."""
    with open(RECORDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_meeting(meeting_id: str, topic: str, start_time: str, duration: int, files: list[dict]) -> None:
    """
    Registra una reunión con todos sus archivos listados desde Zoom.

    Args:
        meeting_id: ID de la reunión en Zoom.
        topic: título de la reunión.
        start_time: fecha/hora de inicio (string ISO).
        duration: duración en minutos.
        files: lista de dicts con { "type": str, "status": str }
               status inicial puede ser "available"
    """
    records = _load()

    # Armar entrada
    entry = {
        "meeting_id": meeting_id,
        "topic": topic,
        "start_time": start_time,
        "duration": duration,
        "files": files,
        "registered_at": datetime.now().isoformat(timespec="seconds"),
    }

    # Reemplazar si ya existía
    records = [r for r in records if r["meeting_id"] != meeting_id]
    records.append(entry)

    _save(records)
    logger.debug(f"Reunión registrada en recordings.json: {topic} ({meeting_id})")


def update_file_status(meeting_id: str, file_type: str, status: str) -> None:
    """
    Actualiza el estado de un archivo dentro de una reunión.
    Ej: status = "downloaded", "discarded_audio", "skipped_by_preference"
    """
    records = _load()

    for r in records:
        if r["meeting_id"] == meeting_id:
            for f in r["files"]:
                if f["type"] == file_type:
                    f["status"] = status
            break

    _save(records)
    logger.debug(f"Estado actualizado: meeting {meeting_id}, file {file_type} → {status}")


def get_all_recordings() -> list[dict]:
    """Devuelve todas las reuniones registradas."""
    return _load()
def get_file_status(meeting_id: str, file_type: str) -> str | None:
    """
    Devuelve el estado actual de un archivo en una reunión, o None si no existe.
    """
    records = _load()

    for r in records:
        if r["meeting_id"] == meeting_id:
            for f in r["files"]:
                if f["type"] == file_type:
                    return f.get("status")
    return None


