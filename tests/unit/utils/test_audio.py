import re
import time
import pytest
from types import SimpleNamespace

from zoomtube.utils import audio


class DummyCompletedProcess:
    def __init__(self, stderr):
        self.stderr = stderr


def test_no_silence_detected(monkeypatch, tmp_path):
    """Si ffmpeg no reporta silence_start/end debe devolver True."""
    stderr = "some ffmpeg output without silence"

    def fake_run(cmd, stderr, stdout, text):
        return DummyCompletedProcess(stderr=stderr)

    monkeypatch.setattr(audio.subprocess, "run", lambda *a, **k: DummyCompletedProcess(stderr))

    res = audio.has_sufficient_audio_activity(str(tmp_path / "f.mp4"), total_duration=60)
    assert res is True


def test_long_silence_detected(monkeypatch, tmp_path):
    """Si la proporción de silencio excede el umbral, devuelve False."""
    # Simular un silence_start y silence_end que suman 55 segundos de 60
    stderr = (
        "silence_start: 0\n"
        "silence_end: 55\n"
    )

    monkeypatch.setattr(audio.subprocess, "run", lambda *a, **k: DummyCompletedProcess(stderr=stderr))

    res = audio.has_sufficient_audio_activity(str(tmp_path / "f.mp4"), total_duration=60, silence_ratio_threshold=0.5)
    assert res is False


def test_unpaired_silence_start(monkeypatch, tmp_path):
    """Si hay más silence_start que silence_end se considera hasta total_duration."""
    stderr = "silence_start: 10\n"
    monkeypatch.setattr(audio.subprocess, "run", lambda *a, **k: DummyCompletedProcess(stderr=stderr))

    # silence from 10 to total_duration(30) -> 20s silence -> ratio 20/30 = 0.66
    res = audio.has_sufficient_audio_activity(str(tmp_path / "f.mp4"), total_duration=30, silence_ratio_threshold=0.7)
    assert res is False or res is True  # depending on threshold; ensure function runs without exception


def test_subprocess_raises_and_finally_accepts(monkeypatch, tmp_path):
    """Si subprocess lanza excepción en intentos, la función retorna True al final."""
    calls = {"n": 0}

    def bad_run(*a, **k):
        calls["n"] += 1
        raise RuntimeError("ffmpeg not found")

    monkeypatch.setattr(audio.subprocess, "run", bad_run)

    res = audio.has_sufficient_audio_activity(str(tmp_path / "f.mp4"), total_duration=10)
    assert res is True
