import pytest
from datetime import datetime
from zoomtube.utils import downloads_registry


@pytest.fixture(autouse=True)
def patch_state_dir(tmp_path, monkeypatch):
    """Usa un directorio temporal para no tocar el `downloads.json` real."""
    fake_state_dir = tmp_path / "state"
    fake_downloads_file = fake_state_dir / "downloads.json"

    monkeypatch.setattr(downloads_registry, "STATE_DIR", fake_state_dir)
    monkeypatch.setattr(downloads_registry, "DOWNLOADS_FILE", fake_downloads_file)

    yield


def test_register_and_get_all_downloads():
    downloads_registry.register_download(
        local_path="recordings/meeting1.mp4",
        topic="Clase Test",
        duration=42,
        status="pending_audio_check",
    )

    records = downloads_registry.get_all_downloads()
    assert len(records) == 1
    rec = records[0]
    assert rec["local_path"] == "recordings/meeting1.mp4"
    assert rec["topic"] == "Clase Test"
    assert rec["duration"] == 42
    assert rec["status"] == "pending_audio_check"
    # `downloaded_at` debe ser un ISO parseable
    datetime.fromisoformat(rec["downloaded_at"])


def test_register_updates_existing():
    local = "recordings/meeting2.mp4"
    downloads_registry.register_download(local_path=local, topic="Primera", duration=10, status="pending_audio_check")
    downloads_registry.register_download(local_path=local, topic="Primera", duration=10, status="success")

    records = downloads_registry.get_all_downloads()
    assert len(records) == 1
    assert records[0]["local_path"] == local
    assert records[0]["status"] == "success"
