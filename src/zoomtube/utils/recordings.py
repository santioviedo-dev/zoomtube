# src/zoom2yt/utils/recordings.py
import os
from pathlib import Path
from typing import List, Dict, Optional


def select_preferred_recording(files: List[Dict]) -> Optional[Dict]:
    """
    Selecciona la mejor grabación MP4 según prioridad de tipo de vista.
    """
    preferred_types = [
        "shared_screen_with_gallery_view",
        "shared_screen_with_speaker_view",
        "active_speaker",
        "gallery_view",
    ]
    for view_type in preferred_types:
        rec = next(
            (f for f in files if f.get("file_type") == "MP4" and f.get("recording_type") == view_type),
            None
        )
        if rec:
            return rec
    return None


def get_unique_filename(output_path: Path, base_name: str) -> Path:
    """
    Genera un nombre único para no sobreescribir archivos existentes.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    counter = 1
    file_path = output_path / base_name
    name, ext = os.path.splitext(base_name)

    while file_path.exists():
        file_path = output_path / f"{name} ({counter}){ext}"
        counter += 1

    return file_path


def sanitize_filename(name: str) -> str:
    """
    Limpia un string para que sea un nombre de archivo válido.
    """
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip()
