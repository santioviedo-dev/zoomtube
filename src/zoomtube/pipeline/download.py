from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zoomtube.utils.audio import has_sufficient_audio_activity
from zoomtube.utils import downloads_registry, recordings_registry
import zoomtube.constants as constants

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
    También registra TODAS las grabaciones encontradas (aunque no se descarguen).
    """

    # Resolver fechas
    if date:
        start_date = end_date = date
    elif not start_date and not end_date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = end_date = date

    # Carpeta destino
    target_dir = Path(output_path) if output_path else get_download_dir()
    if date:
        target_dir = target_dir / date
    elif start_date and end_date:
        target_dir = target_dir / f"{start_date}_to_{end_date}"
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
        )

        for meeting in meetings:
            meeting_id = meeting.get("id")
            topic = sanitize_filename(meeting.get("topic", "sin_titulo"))
            duration = meeting.get("duration", 0)
            start_time = meeting.get("start_time")
            files = meeting.get("recording_files", [])

            if not files:
                logger.warning(f"Reunión sin grabaciones válidas: {topic}")
                continue

            # Registrar todas como disponibles
            recordings_registry.register_meeting(
                meeting_id=meeting_id,
                topic=topic,
                start_time=start_time,
                duration=duration,
                files=[{"type": f.get("recording_type"), "status": "available"} for f in files],
            )

            # Selección de qué descargar
            files_to_process = []

            if preferred_types:
                # Buscar la primera que exista en orden de preferencia
                if preferred_types == []:
                    preferred_types = constants.ZOOM_RECORDING_TYPES
                chosen = None
                for pref in preferred_types:
                    chosen = next((f for f in files if f.get("recording_type") == pref), None)
                    if chosen:
                        files_to_process = [chosen]
                        break
                # Las demás se marcan como omitidas
                for f in files:
                    if f not in files_to_process:
                        recordings_registry.update_file_status(meeting_id, f.get("recording_type"), "skipped_by_preference")

            elif recording_types:
                # Incluir solo las que coinciden
                files_to_process = [f for f in files if f.get("recording_type") in recording_types]
                for f in files:
                    if f not in files_to_process:
                        recordings_registry.update_file_status(meeting_id, f.get("recording_type"), "skipped_by_preference")
            else:
                # Si no se especifica, procesar todas
                files_to_process = files

            # Descargar/analizar cada archivo elegido
            for file_info in files_to_process:
                file_type = file_info.get("recording_type")
                file_url = file_info.get("download_url")
                if not file_url:
                    logger.warning(f"Grabación sin URL: {topic} ({file_type})")
                    recordings_registry.update_file_status(meeting_id, file_type, "failed")
                    continue

                if recordings_registry.get_file_status(meeting_id, file_type) in ["downloaded", "success"]:
                    logger.info(f"Ya descargado: {topic} ({file_type}), se omite.")
                    continue
                
                
                # comprobar si ya existe el archivo con esa ruta
                
                if preferred_types:
                    file_path = target_dir / f"{topic}.mp4"
                else:
                    file_path = target_dir / f"{topic} [{file_type}].mp4" # Parece que no está entrando acá nunca
                    # logger.debug(f"Comprobando existencia de archivo en {file_path}") 
                    
                
                if file_path.exists():
                    res = input(f"El archivo ya existe en la ruta: {file_path}, deseas descargarlo ahí de todas maneras?. (S/N): ")
                    if res.strip().lower() != 's':
                        logger.info(f"Se omite la descarga de {topic} ({file_type}) porque ya existe el archivo.")
                        recordings_registry.update_file_status(meeting_id, file_type, "skipped_existing")
                        continue
                
                dest_path = get_unique_filename(target_dir, f"{topic}{f" ({file_type})" if not preferred_types else ""}.mp4")

                try:
                    logger.info(f"Descargando {topic} ({duration} min) [{file_type}] → {dest_path}")
                    zoom_client.download_recording(token, file_url, dest_path)

                    # Registrar inmediatamente como pendiente
                    downloads_registry.register_download(
                        str(dest_path), topic, duration, "pending_audio_check"
                    )
                    recordings_registry.update_file_status(meeting_id, file_type, "downloaded")

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
                            downloads_registry.register_download(
                                str(dest_path), topic, duration, "discarded_silence"
                            )
                            recordings_registry.update_file_status(meeting_id, file_type, "discarded_audio")
                            dest_path.unlink(missing_ok=True)
                            continue

                    # Si pasa audio o no se chequea → éxito
                    downloads_registry.register_download(
                        str(dest_path), topic, duration, "success"
                    )

                except Exception as e:
                    logger.error(f"Error descargando {topic}: {e}")
                    downloads_registry.register_download(
                        str(dest_path), topic, duration, "failed"
                    )
                    recordings_registry.update_file_status(meeting_id, file_type, "failed")
