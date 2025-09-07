from __future__ import annotations

import os

from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from sqlalchemy.exc import OperationalError


def upgrade_to_head(alembic_ini_path: str | None = None) -> None:
    cfg_path = alembic_ini_path or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "alembic.ini"
    )
    cfg = Config(cfg_path)
    try:
        command.upgrade(cfg, "head")
        return
    except CommandError as e:
        msg = str(e)
        if "Multiple head revisions" in msg or "Multiple heads" in msg:
            # When branches exist, try upgrading all heads.
            try:
                command.upgrade(cfg, "heads")
                return
            except OperationalError as oe:
                # If objects already exist (e.g., rerun on a pre-populated DB), stamp.
                if "already exists" in str(oe):
                    command.stamp(cfg, "heads")
                    return
                raise
        raise


if __name__ == "__main__":
    upgrade_to_head()
