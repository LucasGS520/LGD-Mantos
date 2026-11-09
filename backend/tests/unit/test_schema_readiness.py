"""A prontidão deve acompanhar a revisão da cadeia Alembic versionada."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from app.core.version import SCHEMA_REVISION


def test_readiness_revision_matches_migration_head():
    root = Path(__file__).resolve().parents[2]
    configuration = Config(str(root / "alembic.ini"))
    configuration.set_main_option("script_location", str(root / "migrations"))
    assert ScriptDirectory.from_config(configuration).get_current_head() == SCHEMA_REVISION
