import pytest
from pathlib import Path
from zoomtube.pipeline import download


def test_run_no_users(monkeypatch, tmp_path):
    """Si `zoom_client.list_users` devuelve vacío, `run` termina sin errores y crea la carpeta destino."""
    # Mock zoom_client functions
    class DummyClient:
        @staticmethod
        def get_access_token():
            return "token"

        @staticmethod
        def list_users(token):
            return []

    monkeypatch.setattr(download, "zoom_client", DummyClient)

    # Force download directory to tmp
    monkeypatch.setattr(download, "get_download_dir", lambda: Path(tmp_path))

    # Should not raise
    download.run(date="2025-01-01")
    # target folder should exist
    assert (Path(tmp_path) / "2025-01-01").exists()
