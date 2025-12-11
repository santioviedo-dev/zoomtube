import pytest
from pathlib import Path
from zoomtube.pipeline import upload


def test_run_single_file_not_exists(monkeypatch, tmp_path):
    fake_path = tmp_path / "nope.mp4"

    recorded = {}

    def fake_register(local_path, youtube_id, title, status):
        recorded["args"] = (local_path, youtube_id, title, status)

    monkeypatch.setattr(upload, "uploads_registry", type("M", (), {"register_upload": staticmethod(fake_register), "is_uploaded": staticmethod(lambda p: False)}))

    res = upload.run_single(str(fake_path), title="Test")
    assert res is None
    # registered as failed
    assert recorded.get("args") is not None
    assert recorded["args"][3] == "failed"


def test_run_batch_uploads_videos(monkeypatch, tmp_path):
    folder = tmp_path / "videos"
    folder.mkdir()
    # Create one video and one non-video
    (folder / "a.mp4").write_text("x")
    (folder / "b.txt").write_text("nope")

    # Ensure is_uploaded returns False
    monkeypatch.setattr(upload, "uploads_registry", type("M", (), {"is_uploaded": staticmethod(lambda p: False)}))

    # Monkeypatch run_single to return an id
    def fake_run_single(path, title, **kwargs):
        return "vid123"

    monkeypatch.setattr(upload, "run_single", fake_run_single)

    res = upload.run_batch(str(folder))
    assert res == ["vid123"]
