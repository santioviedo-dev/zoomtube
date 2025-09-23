import pytest
from pathlib import Path
from zoomtube.utils import uploads_registry

@pytest.fixture(autouse=True)
def patch_state_dir(tmp_path, monkeypatch):
    """Usa un directorio temporal para no tocar el recordings.json real."""
    fake_state_dir = tmp_path / "state"
    fake_uploads_file = fake_state_dir / "uploads.json"

    monkeypatch.setattr(uploads_registry, "STATE_DIR", fake_state_dir)
    monkeypatch.setattr(uploads_registry, "RECORDINGS_FILE", fake_uploads_file)

    yield

