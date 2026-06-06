from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


def test_alembic_upgrade_and_downgrade(isolated_database_env: str) -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))

    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.downgrade(config, "base")
