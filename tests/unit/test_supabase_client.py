from __future__ import annotations

import os

import pytest

from src.database.supabase_client import SupabaseClient


def test_supabase_client_not_configured_raises():
    # Ensure no env is set
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_ANON_KEY", None)
    client = SupabaseClient()
    with pytest.raises(RuntimeError):
        _ = client.client
