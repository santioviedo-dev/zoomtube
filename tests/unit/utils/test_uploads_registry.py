import pytest
from pathlib import Path
from zoomtube.utils import uploads_registry
import json


@pytest.fixture(autouse=True)
def patch_state_dir(tmp_path, monkeypatch):
    """Usa un directorio temporal para no tocar el `uploads.json` real."""
    fake_state_dir = tmp_path / "state"
    fake_uploads_file = fake_state_dir / "uploads.json"

    monkeypatch.setattr(uploads_registry, "STATE_DIR", fake_state_dir)
    monkeypatch.setattr(uploads_registry, "UPLOADS_FILE", fake_uploads_file)

    yield


def test_register_and_is_uploaded():
    local_path = "video.mp4"
    youtube_id = "abc123"
    title = "Test Video"
    status = "success"

    # Initially not uploaded
    assert not uploads_registry.is_uploaded(local_path)

    # Register upload
    uploads_registry.register_upload(local_path, youtube_id, title, status)

    # Now should be uploaded
    assert uploads_registry.is_uploaded(local_path)


def test_register_failed_upload():
    local_path = "video2.mp4"
    youtube_id = None
    title = "Failed Video"
    status = "failed"

    uploads_registry.register_upload(local_path, youtube_id, title, status)

    # Failed uploads should not be considered as uploaded
    assert not uploads_registry.is_uploaded(local_path)


def test_get_all_uploads():
    uploads_registry.register_upload("a.mp4", "id1", "Title A", "success")
    uploads_registry.register_upload("b.mp4", None, "Title B", "failed")

    all_uploads = uploads_registry.get_all_uploads()
    assert len(all_uploads) == 2
    assert all_uploads[0]["local_path"] == "a.mp4"
    assert all_uploads[1]["local_path"] == "b.mp4"
    assert all_uploads[0]["status"] == "success"
    assert all_uploads[1]["status"] == "failed"


def test_ensure_file_creates_file():
    fake_uploads_file = uploads_registry.UPLOADS_FILE
    # File should not exist initially
    assert not fake_uploads_file.exists()
    # _ensure_file should create it
    uploads_registry._ensure_file()
    assert fake_uploads_file.exists()
    # Should contain an empty list
    with open(fake_uploads_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []

