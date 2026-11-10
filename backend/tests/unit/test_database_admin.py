"""Administração desacoplada e destinos explícitos; nenhum teste altera banco."""

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import reset_operation
from admin_config import migration_url


def test_models_do_not_need_application_secrets():
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"DATABASE_URL", "APP_PASSWORD", "APP_SECRET"}
    }
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.shared.models.entities import Base; print(len(Base.metadata.tables))",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "15"


def test_migration_refuses_another_destination(monkeypatch):
    monkeypatch.setattr(
        "admin_config.environment",
        lambda: {
            "MIGRATION_DATABASE_URL": "postgresql+asyncpg://lgd_migrator:test@db/lgd_mantos",
            "DATABASE_URL": "postgresql+asyncpg://lgd_app:test@other/lgd_mantos",
        },
    )
    with pytest.raises(RuntimeError, match="destinos diferentes"):
        migration_url()


@pytest.mark.parametrize(
    "database,host,confirmation",
    [
        ("other", "db", "RECRIAR other"),
        ("lgd_mantos", "other", "RECRIAR lgd_mantos"),
        ("lgd_mantos", "db", "LIMPAR lgd_mantos"),
    ],
)
def test_rebuild_refuses_wrong_target_or_old_confirmation(
    monkeypatch, database, host, confirmation
):
    monkeypatch.setattr(
        reset_operation,
        "migration_url",
        lambda: "postgresql+asyncpg://lgd_migrator:test@db/lgd_mantos",
    )
    with pytest.raises(RuntimeError):
        reset_operation.target(SimpleNamespace(database=database, host=host, confirm=confirmation))
