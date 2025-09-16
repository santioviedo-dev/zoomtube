import os
from pathlib import Path
from typing import List, Optional
from googleapiclient.http import MediaFileUpload

from zoomtube.clients import youtube_client
from zoomtube.utils.logger import logger
from zoomtube.constants import VIDEO_EXTENSIONS
from zoomtube.utils.recordings import sanitize_filename, get_unique_filename
from zoomtube.utils import uploads_registry  # nuevo import


def run_single(
    path: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    privacy_status: str = "unlisted",
    playlist_id: Optional[str] = None,
    schedule: Optional[str] = None,
) -> Optional[str]:
    """
    Sube un solo video a YouTube y lo registra en uploads.json.

    Args:
        path: ruta al archivo de video
        title: título del video (si None, se usa el nombre del archivo)
        description: descripción opcional
        tags: lista de tags
        privacy_status: public | private | unlisted
        playlist_id: playlist opcional para añadir el video
        schedule: fecha/hora de publicación (YYYY-MM-DD HH:MM)

    Returns:
        video_id de YouTube o None si falla
    """
    file_path = Path(path)
    title = title or sanitize_filename(file_path.stem)

    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Archivo inválido: {file_path}")
        uploads_registry.register_upload(str(file_path), None, title, "failed")
        return None

    # Chequear si ya se subió
    if uploads_registry.is_uploaded(str(file_path)):
        logger.info(f"Ya estaba subido: {file_path}")
        return None

    youtube = youtube_client.get_authenticated_service()
    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    if schedule:
        # Nota: hay que convertir el string a formato RFC3339 (pendiente en youtube_client)
        body["status"]["publishAt"] = schedule

    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Progreso: {int(status.progress() * 100)}%")

        if response:
            video_id = response.get("id")
            logger.info(f"✅ Subida completada: {video_id}")
            uploads_registry.register_upload(str(file_path), video_id, title, "success")
            return video_id
    except Exception as e:
        logger.error(f"❌ Error subiendo {file_path}: {e}")
        uploads_registry.register_upload(str(file_path), None, title, "failed")

    return None


def run_batch(
    folder: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    privacy_status: str = "unlisted",
    playlist_id: Optional[str] = None,
    schedule: Optional[str] = None,
) -> List[str]:
    """
    Sube múltiples videos desde una carpeta.
    Omite los que ya estén subidos según uploads.json.
    """
    folder_path = Path(folder)

    if not folder_path.exists() or not folder_path.is_dir():
        logger.error(f"Carpeta inválida: {folder}")
        return []

    video_ids = []
    for file_name in os.listdir(folder_path):
        if not any(file_name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            continue

        file_path = folder_path / file_name
        title = sanitize_filename(file_path.stem)

        # Saltar si ya estaba subido
        if uploads_registry.is_uploaded(str(file_path)):
            logger.info(f"Ya estaba subido (omitido): {file_path}")
            continue

        video_id = run_single(
            path=str(file_path),
            title=title,
            description=description,
            tags=tags,
            privacy_status=privacy_status,
            playlist_id=playlist_id,
            schedule=schedule,
        )

        if video_id:
            video_ids.append(video_id)

    return video_ids
