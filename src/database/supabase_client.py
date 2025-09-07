from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    from supabase import create_client  # type: ignore
except Exception:  # pragma: no cover
    create_client = None  # type: ignore


class SupabaseClient:
    """Thin wrapper around supabase-py with lazy initialization.

    Reads SUPABASE_URL and SUPABASE_ANON_KEY from env by default.
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY")
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            if not (self.url and self.key) or create_client is None:
                raise RuntimeError(
                    "Supabase client not configured. Set SUPABASE_URL and "
                    "SUPABASE_ANON_KEY, and install supabase-py."
                )
            self._client = create_client(self.url, self.key)
        return self._client

    def upsert_article(self, data: Dict[str, Any]) -> Any:
        return self.client.table("articles").upsert(data).execute()

    def log_processing(self, data: Dict[str, Any]) -> Any:
        return self.client.table("processing_log").insert(data).execute()
