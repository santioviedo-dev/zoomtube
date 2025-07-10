import subprocess
import re



def has_sufficient_audio_activity(file_path, total_duration, silence_threshold_db=-35, silence_ratio_threshold=0.9):
    """
    Checks if a video file has sufficient audio activity.

    Args:
        file_path (str): Path to the video file.
        total_duration (float): Total duration of the video in seconds.
        silence_threshold_db (int): Threshold to consider something as silence (more negative = stricter).
        silence_ratio_threshold (float): Maximum tolerated percentage of silence.

    Returns:
        bool: True if there is sufficient audio, False if it is mostly silent.
    """

    try:
        command = [
            "ffmpeg",
            "-i", f"{file_path}",
            "-af", f"silencedetect=noise={silence_threshold_db}dB:d=0.5",
            "-f", "null",
            "-"
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        stderr_output = result.stderr

        silence_starts = [float(m.group(1)) for m in re.finditer(r"silence_start: (\d+(\.\d+)?)", stderr_output)]
        silence_ends = [float(m.group(1)) for m in re.finditer(r"silence_end: (\d+(\.\d+)?)", stderr_output)]

        if not silence_starts and not silence_ends:
            return True  # No silencios detectados

        if len(silence_starts) > len(silence_ends):
            silence_ends.append(total_duration)

        total_silence = sum(end - start for start, end in zip(silence_starts, silence_ends))
        silence_ratio = total_silence / total_duration

        return silence_ratio < silence_ratio_threshold

    except Exception as e:
        print(f"[⚠️ audio analysis failed] {file_path}: {e}")
        return True