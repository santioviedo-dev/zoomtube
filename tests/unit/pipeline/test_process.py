import pytest
from types import SimpleNamespace
from zoomtube.pipeline import process


def test_run_invokes_download_and_upload(monkeypatch):
    calls = {"download": 0, "upload": 0}

    def fake_download(**kwargs):
        calls["download"] += 1

    def fake_upload(folder, **kwargs):
        calls["upload"] += 1

    monkeypatch.setattr(process, "download", SimpleNamespace(run=fake_download))
    monkeypatch.setattr(process, "upload", SimpleNamespace(run_batch=fake_upload))

    # Run should call both
    process.run(date="2025-01-02", check_audio=False)
    assert calls["download"] == 1
    assert calls["upload"] == 1

 
