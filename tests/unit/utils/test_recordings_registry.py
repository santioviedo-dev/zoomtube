# tests/utils/test_recordings_registry.py
import pytest
from pathlib import Path
from zoomtube.utils import recordings_registry


@pytest.fixture(autouse=True)
def patch_state_dir(tmp_path, monkeypatch):
    """Usa un directorio temporal para no tocar el recordings.json real."""
    fake_state_dir = tmp_path / "state"
    fake_recordings_file = fake_state_dir / "recordings.json"

    monkeypatch.setattr(recordings_registry, "STATE_DIR", fake_state_dir)
    monkeypatch.setattr(recordings_registry, "RECORDINGS_FILE", fake_recordings_file)

    yield


def test_register_and_get_all_recordings():
    recordings_registry.register_meeting(
        meeting_id="123",
        topic="Clase Test",
        start_time="2025-09-15T10:00:00Z",
        duration=45,
        files=[{"type": "gallery_view", "status": "available"}],
    )

    records = recordings_registry.get_all_recordings()
    assert len(records) == 1
    assert records[0]["meeting_id"] == "123"
    assert records[0]["files"][0]["status"] == "available"


def test_update_file_status_and_get_file_status():
    recordings_registry.register_meeting(
        meeting_id="456",
        topic="Otra Clase",
        start_time="2025-09-15T12:00:00Z",
        duration=60,
        files=[{"type": "shared_screen_with_speaker_view", "status": "available"}],
    )

    recordings_registry.update_file_status("456", "shared_screen_with_speaker_view", "downloaded")

    status = recordings_registry.get_file_status("456", "shared_screen_with_speaker_view")
    assert status == "downloaded"


def test_get_file_status_not_found():
    recordings_registry.register_meeting(
        meeting_id="789",
        topic="Clase X",
        start_time="2025-09-15T14:00:00Z",
        duration=30,
        files=[{"type": "audio_only", "status": "available"}],
    )

    status = recordings_registry.get_file_status("789", "gallery_view")
    assert status is None


def test_register_overwrites_existing_meeting():
    recordings_registry.register_meeting(
        meeting_id="999",
        topic="Clase Inicial",
        start_time="2025-09-15T16:00:00Z",
        duration=30,
        files=[{"type": "audio_only", "status": "available"}],
    )

    recordings_registry.register_meeting(
        meeting_id="999",
        topic="Clase Actualizada",
        start_time="2025-09-15T16:00:00Z",
        duration=30,
        files=[{"type": "audio_only", "status": "downloaded"}],
    )

    records = recordings_registry.get_all_recordings()
    assert len(records) == 1  # solo una reunión
    assert records[0]["topic"] == "Clase Actualizada"
    assert records[0]["files"][0]["status"] == "downloaded"
