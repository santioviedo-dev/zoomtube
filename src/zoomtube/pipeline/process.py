from datetime import datetime, timedelta
from pathlib import Path

from zoomtube.pipeline import download, upload
from zoomtube import config
from zoomtube.utils.logger import logger
import zoomtube.constants as constants


def run(date=None, check_audio=True):
    """
    Ejecuta el pipeline completo:
    - Descarga grabaciones de Zoom.
    - Sube los videos a YouTube.

    Convenciones:
    - Fecha por defecto: ayer.
    - Tipos de grabación preferidos: DEFAULT_PREFERRED_TYPES.
    - Privacidad en YouTube: unlisted.
    - El título del video en YouTube se resuelve en upload.py
      a partir del topic limpio (no del nombre técnico del archivo).
    """
    if not date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"Procesando pipeline completo para fecha {date}")

    # --- Descarga ---
    download.run(
        date=date,
        min_duration=10,
        preferred_types=constants.DEFAULT_PREFERRED_TYPES,
        output_path=config.RECORDINGS_BASE_PATH,
        check_audio=check_audio,
        silence_threshold=constants.DEFAULT_SILENCE_THRESHOLD_DB,
        silence_ratio=constants.DEFAULT_SILENCE_RATIO,
    )

    # --- Subida ---
    folder = Path(config.RECORDINGS_BASE_PATH) / date
    upload.run_batch(
        folder=folder,
        privacy_status="unlisted",
        tags=[],
        description="",
        # playlist_id=None,
    )
