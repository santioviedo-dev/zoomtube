# src/zoomtube/utils/audio.py
import subprocess
import re
import time
from pathlib import Path
from zoomtube.utils.logger import logger
from zoomtube import config


def has_sufficient_audio_activity(
    file_path: str,
    total_duration: float,
    silence_threshold_db: int = -35,
    silence_ratio_threshold: float = 0.9,
) -> bool:
    """
    Verifica si un video tiene suficiente actividad de audio usando ffmpeg.

    Args:
        file_path: ruta al archivo de video.
        total_duration: duración total del video en segundos.
        silence_threshold_db: umbral de silencio en dB (más negativo = más estricto).
        silence_ratio_threshold: proporción máxima de silencio tolerada (0–1).

    Returns:
        True si el video tiene suficiente audio, False si es mayormente silencio.
        Si el análisis falla, devuelve True para no bloquear el pipeline.
    """
    file_path = Path(file_path)

    for attempt in range(3):
        try:
            command = [
                config.FFMPEG_BIN,  # configurable desde .env o default "ffmpeg"
                "-i", str(file_path),
                "-af", f"silencedetect=noise={silence_threshold_db}dB:d=0.5",
                "-f", "null",
                "-"
            ]
            result = subprocess.run(
                command,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                text=True
            )
            stderr_output = result.stderr

            silence_starts = [
                float(m.group(1)) for m in re.finditer(r"silence_start: (\d+(\.\d+)?)", stderr_output)
            ]
            silence_ends = [
                float(m.group(1)) for m in re.finditer(r"silence_end: (\d+(\.\d+)?)", stderr_output)
            ]

            if not silence_starts and not silence_ends:
                logger.debug(f"Audio analysis {file_path}: no silence detected")
                return True

            if len(silence_starts) > len(silence_ends):
                silence_ends.append(total_duration)

            total_silence = sum(end - start for start, end in zip(silence_starts, silence_ends))
            silence_ratio = total_silence / total_duration

            logger.debug(
                f"Audio analysis {file_path}: silence_ratio={silence_ratio:.2f}, "
                f"threshold={silence_ratio_threshold}"
            )

            return silence_ratio < silence_ratio_threshold

        except Exception as e:
            logger.warning(f"Audio analysis attempt {attempt+1} failed for {file_path}: {e}")
            time.sleep(0.5)

    # Si falla todos los intentos, aceptamos el archivo por seguridad
    logger.error(f"Audio analysis failed after retries for {file_path}, keeping file")
    return True
