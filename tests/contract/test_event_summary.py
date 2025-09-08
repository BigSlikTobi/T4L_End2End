import importlib
import inspect

import pytest


def _load_events_api_module():
    try:
        return importlib.import_module("src.services.events_api")
    except Exception as e:
        pytest.xfail(f"Pending implementation of events API (T019): {e}")


def test_get_event_summary_function_signature_matches_contract():
    mod = _load_events_api_module()

    func = getattr(mod, "get_event_summary", None)
    if func is None:
        pytest.xfail("Function get_event_summary not found in src.services.events_api (T019)")

    assert inspect.isfunction(func), "get_event_summary must be a function"
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    assert len(params) == 1 and params[0].name == "event_id", "get_event_summary(event_id: str) expected"

    hints = getattr(func, "__annotations__", {})
    assert hints.get("event_id") in (str, None), "get_event_summary should type annotate event_id: str"
    ret = hints.get("return")
    # Accept string summary contract-wise
    assert ret in (str, None), "get_event_summary should return str per contract"
