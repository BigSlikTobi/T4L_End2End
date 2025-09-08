import importlib
import inspect
from typing import Any, Dict

import pytest


def _load_events_api_module():
    try:
        return importlib.import_module("src.services.events_api")
    except Exception as e:
        pytest.xfail(f"Pending implementation of events API (T018): {e}")


def test_get_event_details_function_signature_matches_contract():
    mod = _load_events_api_module()

    func = getattr(mod, "get_event", None)
    if func is None:
        pytest.xfail("Function get_event not found in src.services.events_api (T018)")

    assert inspect.isfunction(func), "get_event must be a function"
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    assert len(params) == 1 and params[0].name == "event_id", "get_event(event_id: str) expected"

    hints = getattr(func, "__annotations__", {})
    assert hints.get("event_id") in (str, None), "get_event should type annotate event_id: str"
    ret = hints.get("return")
    assert ret in (Dict[str, Any], dict), "get_event should return Dict[str, Any] per contract"
