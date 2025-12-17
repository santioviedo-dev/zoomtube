import os
from pathlib import Path
from typing import List, Optional

from zoomtube.clients import youtube_client
from zoomtube.utils.logger import logger
from zoomtube.constants import VIDEO_EXTENSIONS
from zoomtube.utils.recordings import sanitize_filename
from zoomtube.utils import uploads_registry


def run_single(
    path: str,
    title: Optional[str] = None,
    description: str = "",
    tags: Optional[List[str]] = None,
    privacy_status: str = "unlisted",
    # playlist_id: Optional[str] = None,
    # schedule: Optional[str] = None,
) -> Optional[str]:
    """
    Sube un solo video a YouTube y lo registra en uploads.json.
    """
    file_path = Path(path)

    clean_title = title or sanitize_filename(file_path.stem)

    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Archivo inválido: {file_path}")
        uploads_registry.register_upload(str(file_path), None, clean_title, "failed")
        return None

    if uploads_registry.is_uploaded(str(file_path)):
        logger.info(f"Ya estaba subido: {file_path}")
        return None

    try:
        video_id = youtube_client.upload_video(
            file_path=file_path,
            title=clean_title,
            description=description,
            tags=tags,
            privacy_status=privacy_status,
            # Nota: ver implementación de playlist_id y schedule
        )

        uploads_registry.register_upload(str(file_path), video_id, clean_title, "success")
        logger.info(f"✅ Subida completada: {video_id}")
        return video_id

    except Exception as e:
        logger.error(f"❌ Error subiendo {file_path}: {e}")
        uploads_registry.register_upload(str(file_path), None, clean_title, "failed")
        return None


def run_batch(
    folder: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    privacy_status: str = "unlisted",
    # playlist_id: Optional[str] = None,
    # schedule: Optional[str] = None,
) -> List[str]:
    """
    Sube múltiples videos desde una carpeta.
    Omite los que ya estén subidos según uploads.json.
    """
    folder_path = Path(folder)

    if not folder_path.exists() or not folder_path.is_dir():
        logger.error(f"Carpeta inválida: {folder}")
        return []

    video_ids: List[str] = []

    for file_name in os.listdir(folder_path):
        if not any(file_name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            continue

        file_path = folder_path / file_name


        stem = file_path.stem
        stem = stem.split("__", 1)[0]
        title = sanitize_filename(stem)

        if uploads_registry.is_uploaded(str(file_path)):
            logger.info(f"Ya estaba subido (omitido): {file_path}")
            continue

        video_id = run_single(
            path=str(file_path),
            title=title,
            description=description,
            tags=tags,
            privacy_status=privacy_status,
            # playlist_id=playlist_id,
            # schedule=schedule,
        )

        if video_id:
            video_ids.append(video_id)

    return video_ids
