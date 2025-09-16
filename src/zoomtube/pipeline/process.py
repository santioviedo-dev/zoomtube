from datetime import datetime, timedelta
from pathlib import Path
from zoomtube.pipeline import download, upload
from zoomtube import config
from zoomtube.utils.logger import logger
import zoomtube.constants as constsants


def run(date=None, check_audio=True):
    """
    Descarga grabaciones de Zoom y las sube automáticamente a YouTube.
    - Fecha por defecto: ayer.
    - Tipos de grabación: shared_screen_with_speaker_view y speaker_view.
    - Privacidad en YouTube: unlisted.
    - Título: mismo que el de la grabación (nombre de archivo).
    """
    if not date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"Procesando pipeline completo para fecha {date}")

    # --- Descarga ---
    download.run(
        date=date,
        min_duration=10,
        preferred_types=constsants.DEFAULT_PREFERRED_TYPES,
        output_path=config.RECORDINGS_BASE_PATH,
        check_audio=check_audio,
        silence_threshold=config.DEFAULT_SILENCE_THRESHOLD_DB,
        silence_ratio=config.DEFAULT_SILENCE_RATIO,
    )

    # --- Subida ---
    folder = Path(config.RECORDINGS_BASE_PATH) / date
    upload.run_batch(
        folder=folder,
        privacy_status="unlisted",
        tags=[],
        description="",
        playlist_id=None,
    )
