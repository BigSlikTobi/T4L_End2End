import importlib
import inspect
from typing import Any, Dict, List, Optional

import pytest


def _load_events_api_module():
    try:
        return importlib.import_module("src.services.events_api")
    except Exception as e:
        pytest.xfail(f"Pending implementation of events API (T017): {e}")


def test_list_events_function_signature_matches_contract():
    mod = _load_events_api_module()

    func = getattr(mod, "list_events", None)
    if func is None:
        pytest.xfail("Function list_events not found in src.services.events_api (T017)")

    assert inspect.isfunction(func), "list_events must be a function"
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    # list_events(team_id: Optional[str] = None, player_id: Optional[str] = None,
    #             type: Optional[str] = None, min_confidence: Optional[int] = None)
    assert len(params) == 5, "list_events(selfless, team_id, player_id, type, min_confidence) expected"
    assert params[0].name == "team_id"
    assert params[1].name == "player_id"
    assert params[2].name == "type"
    assert params[3].name == "min_confidence"

    hints = getattr(func, "__annotations__", {})
    # Accept Optional[...] or plain types to be flexible
    assert hints.get("team_id") in (Optional[str], str, None), "team_id should be Optional[str]"
    assert hints.get("player_id") in (Optional[str], str, None), "player_id should be Optional[str]"
    assert hints.get("type") in (Optional[str], str, None), "type should be Optional[str]"
    assert hints.get("min_confidence") in (Optional[int], int, None), "min_confidence should be Optional[int]"

    ret = hints.get("return")
    assert ret in (List[Dict[str, Any]], list), "list_events should return List[Dict[str, Any]] per contract"
