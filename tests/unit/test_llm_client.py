import pytest
import importlib


def _load_llm_module():
    try:
        return importlib.import_module("src.services.llm_classifier")
    except Exception as e:
        pytest.xfail(f"Pending LLM classifier implementation (T023): {e}")


def test_llm_classifier_interface():
    mod = _load_llm_module()
    cls = getattr(mod, "LLMClassifier", None)
    if cls is None:
        pytest.xfail("LLMClassifier not found in src.services.llm_classifier (T023)")

    assert hasattr(cls, "classify_title_url"), "Missing classify_title_url method"

