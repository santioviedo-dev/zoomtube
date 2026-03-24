import subprocess
import re
import time
from pathlib import Path
import os
import platform

from zoomtube.utils.logger import logger


class AudioAnalyzer:
    def __init__(
        self,
        ffmpeg_path: str = None,
        silence_threshold_db: int = -35,
        silence_ratio_threshold: float = 0.9,
        retries: int = 3,
    ):
        self.ffmpeg_path = ffmpeg_path or self._default_ffmpeg_path()
        self.silence_threshold_db = silence_threshold_db
        self.silence_ratio_threshold = silence_ratio_threshold
        self.retries = retries

    def _default_ffmpeg_path(self) -> str:
        if platform.system() == "Windows":
            base_dir = Path(__file__).resolve().parents[2]
            return str(base_dir / "bin" / "ffmpeg.exe")
        return "ffmpeg"

    def has_audio(self, file_path: str, total_duration: float) -> bool:
        file_path = Path(file_path)

        for attempt in range(self.retries):
            try:
                result = subprocess.run(
                    self._build_command(file_path),
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    text=True,
                )

                return self._analyze_output(result.stderr, total_duration, file_path)

            except Exception as e:
                logger.warning(
                    f"Audio analysis attempt {attempt+1} failed for {file_path}: {e}"
                )
                time.sleep(0.5)

        logger.error(f"Audio analysis failed after retries for {file_path}, keeping file")
        return True

    def _build_command(self, file_path: Path):
        null_device = "NUL" if os.name == "nt" else "/dev/null"

        return [
            self.ffmpeg_path,
            "-i", str(file_path),
            "-af", f"silencedetect=noise={self.silence_threshold_db}dB:d=0.5",
            "-f", "null",
            null_device,
        ]

    def _analyze_output(self, stderr_output: str, total_duration: float, file_path: Path) -> bool:
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
            f"threshold={self.silence_ratio_threshold}"
        )

        return silence_ratio < self.silence_ratio_threshold