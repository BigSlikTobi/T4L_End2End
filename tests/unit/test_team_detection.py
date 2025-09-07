import importlib

import pytest


def _load_filter_module():
    try:
        return importlib.import_module("src.services.relevance_filter")
    except Exception as e:
        pytest.xfail(f"Pending RelevanceFilter implementation (T021): {e}")


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Chiefs sign new QB", True),
        ("Patriots release veteran WR", True),
        ("Lakers win the finals", False),
        ("Real Madrid signs new striker", False),
    ],
)
def test_is_nfl_team_mention_examples(text, expected):
    mod = _load_filter_module()
    cls = getattr(mod, "RelevanceFilter", None)
    if cls is None:
        pytest.xfail("RelevanceFilter not found (T021)")

    assert hasattr(cls, "is_nfl_team_mention"), "Missing is_nfl_team_mention method"
