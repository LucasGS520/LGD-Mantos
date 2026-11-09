"""Ferramentas administrativas recusam destinos e cópias inseguros antes de gravar."""

import importlib.util
import json
from pathlib import Path

import pytest


def script(name):
    path = Path(__file__).resolve().parents[3] / "deploy" / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capture_refuses_running_api_and_preserves_destination(tmp_path, monkeypatch):
    backup = script("backup")
    destination = tmp_path / "new"
    responses = iter(["backend-id", json.dumps([{"State": {"Running": True}}])])
    monkeypatch.setattr(backup.subprocess, "check_output", lambda *args, **kwargs: next(responses))
    with pytest.raises(RuntimeError, match="Pare o backend"):
        backup.capture(["docker", "compose"], destination)
    assert not destination.exists()


def test_capture_never_overwrites_existing_backup(tmp_path):
    with pytest.raises(RuntimeError, match="nenhum backup existente"):
        script("backup").capture([], tmp_path)


def test_restore_refuses_incomplete_copy_without_creating_photos(tmp_path):
    (tmp_path / "INCOMPLETE").write_text("", encoding="utf-8")
    target = tmp_path / "photos"
    with pytest.raises(RuntimeError, match="incompleto"):
        script("verify_backup").verify(tmp_path, "never-used", target)
    assert not target.exists()
