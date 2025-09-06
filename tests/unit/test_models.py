import pytest
import importlib


def _load_models_module():
    try:
        return importlib.import_module("src.models.article")
    except Exception as e:
        pytest.xfail(f"Pending Article model implementation (T016): {e}")


def test_article_model_fields_and_validation():
    mod = _load_models_module()
    Article = getattr(mod, "Article", None)
    if Article is None:
        pytest.xfail("Article model not found in src.models.article (T016)")

    # Required fields per spec
    art = Article(
        url="https://example.com/a",
        title="Example",
        publisher="Example News",
        publication_date="2025-09-06T10:00:00Z",
        content_summary=None,
    )
    assert art.url.startswith("http"), "url must be a valid HTTP(S) URL"

    with pytest.raises(Exception):
        Article(
            url="not-a-url",
            title="Bad",
            publisher="X",
            publication_date="2025-09-06T10:00:00Z",
        )

