from __future__ import annotations

import os

from alembic.config import Config
from alembic import command


def upgrade_to_head(alembic_ini_path: str | None = None) -> None:
    cfg_path = alembic_ini_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "alembic.ini")
    cfg = Config(cfg_path)
    command.upgrade(cfg, "head")


if __name__ == "__main__":
    upgrade_to_head()
