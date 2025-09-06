import pytest
import importlib


def _load_article_repo():
    try:
        return importlib.import_module("src.database.repositories.article_repo")
    except Exception as e:
        pytest.xfail(f"Pending ArticleRepository implementation (T025): {e}")


def test_article_repository_interface():
    mod = _load_article_repo()
    Repo = getattr(mod, "ArticleRepository", None)
    if Repo is None:
        pytest.xfail("ArticleRepository not found in src.database.repositories.article_repo (T025)")

    # Expected core methods
    for name in ("upsert", "get_by_url"):
        assert hasattr(Repo, name), f"Missing repository method: {name}"

