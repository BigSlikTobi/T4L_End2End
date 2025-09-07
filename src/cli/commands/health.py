from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import click
from sqlalchemy import text

from ...database.connection import get_engine


@click.command(name="health")
def health_cmd() -> None:
    """Run basic health checks and print a JSON status."""

    status: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": os.getenv("APP_VERSION", "dev"),
    }

    # Database check
    db_result: dict[str, object] = {"ok": False}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_result["ok"] = True
    except Exception as e:  # pragma: no cover - environment dependent
        db_result["error"] = str(e)
    status["database"] = db_result

    # OpenAI configuration check (non-fatal)
    try:
        from ...services.openai_client import OpenAIClient  # noqa: F401

        openai_import = True
    except Exception:  # pragma: no cover - optional dependency
        openai_import = False
    status["openai"] = {
        "configured": bool(os.getenv("OPENAI_API_KEY")) and openai_import,
        "import_ok": openai_import,
    }

    # Supabase configuration check (non-fatal)
    try:
        from ...database.supabase_client import create_client  # type: ignore  # noqa: F401

        supabase_import = True
    except Exception:  # pragma: no cover - optional dependency
        supabase_import = False
    status["supabase"] = {
        "configured": bool(os.getenv("SUPABASE_URL")) and bool(os.getenv("SUPABASE_ANON_KEY")) and supabase_import,
        "import_ok": supabase_import,
    }

    click.echo(json.dumps(status))


__all__ = ["health_cmd"]
