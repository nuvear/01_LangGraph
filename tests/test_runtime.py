"""Offline tests for the shared classroom runtime; no provider requests."""
from pathlib import Path
import os
import stat

import pytest

from course_support import runtime


def test_safe_write_creates_new_file(tmp_path):
    path = runtime.safe_write_text(tmp_path, "draft.txt", "Synthetic draft")
    assert path.read_text() == "Synthetic draft"
    if os.name == "posix":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


@pytest.mark.parametrize("name", ["../escape.txt", "/tmp/escape.txt", "draft.md", "folder/draft.txt", "note..txt"])
def test_unsafe_names_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        runtime.safe_write_text(tmp_path, name, "No side effect")
    assert not list(tmp_path.iterdir())


def test_existing_file_is_not_overwritten(tmp_path):
    path = runtime.safe_write_text(tmp_path, "draft.txt", "Original")
    with pytest.raises(FileExistsError):
        runtime.safe_write_text(tmp_path, "draft.txt", "Replacement")
    assert path.read_text() == "Original"


def test_symlink_is_rejected(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "-outside.txt")
    outside.write_text("Keep")
    (tmp_path / "linked.txt").symlink_to(outside)
    with pytest.raises(ValueError):
        runtime.safe_write_text(tmp_path, "linked.txt", "Replace")
    assert outside.read_text() == "Keep"


def test_live_false_does_not_read_credentials(monkeypatch):
    def forbidden():
        raise AssertionError("Offline model guard should run before reading configuration.")
    monkeypatch.setattr(runtime, "values", forbidden)
    with pytest.raises(ValueError, match="--live"):
        runtime.get_model(live=False)


def test_thread_config_isolated():
    first = runtime.execution_config("thread-a")
    second = runtime.execution_config("thread-b")
    assert first["configurable"]["thread_id"] == "thread-a"
    assert second["configurable"]["thread_id"] == "thread-b"
    assert first["recursion_limit"] == 40
    assert "configurable" not in runtime.execution_config()
