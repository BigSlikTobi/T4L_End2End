from src.services.relevance_filter import FilterDecision, RelevanceFilter


def test_filtering_pipeline_rule_based():
    rf = RelevanceFilter()
    nfl = {"title": "Chiefs win opener", "url": "https://sports/foo/nfl/chiefs", "publisher": "x"}
    nba = {"title": "NBA finals", "url": "https://sports/foo/nba/finals", "publisher": "x"}

    d1, s1 = rf.filter_article(nfl)
    d2, s2 = rf.filter_article(nba)

    assert d1 is FilterDecision.KEEP and s1 >= 0.5
    assert d2 is not FilterDecision.KEEP


def test_allowlisted_claim_extraction_with_provenance(monkeypatch):
    """
    T009: Given an allowlisted claim pattern in an article, ensure claim is added
    with provenance (source URL) and status.

    Pending claim extraction service.
    """
    import pytest

    pytest.xfail("Pending claim extraction and provenance recording (T015–T021)")
