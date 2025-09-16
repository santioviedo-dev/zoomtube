from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zoomtube.utils.audio import has_sufficient_audio_activity

from zoomtube.clients import zoom_client
from zoomtube.utils.logger import logger
from zoomtube.utils.recordings import (
    get_unique_filename,
    sanitize_filename,
)
from zoomtube.constants import (
    DEFAULT_SILENCE_THRESHOLD_DB,
    DEFAULT_SILENCE_RATIO,
)
from zoomtube.config import get_download_dir


def run(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date: Optional[str] = None,
    min_duration: int = 10,
    max_duration: Optional[int] = None,
    output_path: Optional[str] = None,
    recording_types: Optional[list[str]] = None,
    preferred_types: Optional[list[str]] = None,
    check_audio: bool = False,
    silence_threshold: int = DEFAULT_SILENCE_THRESHOLD_DB,
    silence_ratio: float = DEFAULT_SILENCE_RATIO,
) -> None:
    """
    Descargar grabaciones de Zoom y guardarlas en disco.

    Args:
        start_date: fecha inicio (YYYY-MM-DD)
        end_date: fecha fin (YYYY-MM-DD)
        date: atajo para un único día (YYYY-MM-DD)
        min_duration: duración mínima en minutos
        max_duration: duración máxima en minutos
        output_path: carpeta de destino
        recording_types: tipos de grabación (inclusivo, descarga todas las coincidencias)
        preferred_types: tipos de grabación con prioridad (descarga solo la primera coincidencia)
        check_audio: si True, descarta grabaciones con poco audio
        silence_threshold: umbral en dB para detectar silencio
        silence_ratio: proporción máxima de silencio tolerada (0–1)
    """

    # Resolver fechas
    if date:
        start_date = end_date = date
    elif not start_date and not end_date:
        default_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = end_date = default_date

    # Carpeta destino
    target_dir = Path(output_path) if output_path else get_download_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Buscando grabaciones de {start_date} a {end_date}")
    logger.info(f"Destino: {target_dir}")

    # Token y usuarios
    token = zoom_client.get_access_token()
    users = zoom_client.list_users(token)

    for user in users:
        user_id = user.get("id")
        if not user_id:
            continue

        logger.debug(f"Consultando grabaciones de usuario {user_id}")

        meetings = zoom_client.list_recordings(
            token=token,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            min_duration=min_duration,
            max_duration=max_duration,
            recording_types=recording_types,
            preferred_types=preferred_types,
        )

        for meeting in meetings:
            topic = sanitize_filename(meeting.get("topic", "sin_titulo"))
            duration = meeting.get("duration", 0)
            files = meeting.get("recording_files", [])

            if not files:
                logger.warning(f"Reunión sin grabaciones válidas: {topic}")
                continue

            for file_info in files:
                file_url = file_info.get("download_url")
                if not file_url:
                    logger.warning(f"Grabación sin URL: {topic}")
                    continue

                dest_path = get_unique_filename(target_dir, f"{topic}.mp4")

                try:
                    logger.info(f"Descargando {topic} ({duration} min) → {dest_path}")
                    zoom_client.download_recording(token, file_url, dest_path)

                    # Chequeo opcional de audio
                    if check_audio:
                        duration_secs = duration * 60
                        if not has_sufficient_audio_activity(
                            dest_path,
                            duration_secs,
                            silence_threshold_db=silence_threshold,
                            silence_ratio_threshold=silence_ratio,
                        ):
                            logger.warning(f"Descartada por silencio: {dest_path}")
                            dest_path.unlink(missing_ok=True)
                            continue

                except Exception as e:
                    logger.error(f"Error descargando {topic}: {e}")
