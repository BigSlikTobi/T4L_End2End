"""Extra coverage for SimplifiedPipeline branches."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.simple_pipeline import SimplifiedPipeline


@pytest.mark.asyncio
async def test_run_source_url_template_expansion_local_rss():
    pipeline = SimplifiedPipeline(use_supabase=False)

    source_config = {
        "url_template": "https://example.com/{YYYY}/{MM}/feed.rss",
        "publisher": "TemplatePub",
        "type": "rss",
    }

    with patch("services.simple_pipeline.FeedIngester") as mock_ingester:
        mock_instance = mock_ingester.return_value
        mock_instance.fetch_feed = AsyncMock(return_value={"status": 200, "content": "<rss></rss>"})
        mock_instance.extract_articles = AsyncMock(return_value=[])

        result = await pipeline.run_source(source_config)

    assert result["status"] == "success"
    assert result["articles_count"] == 0


@pytest.mark.asyncio
async def test_run_with_local_sitemap_nfl_flow():
    pipeline = SimplifiedPipeline(use_supabase=False)

    source_config = {
        "url": "https://www.nfl.com/sitemap.xml",
        "publisher": "NFL.com",
        "type": "sitemap",
    }

    sitemap_urls = [
        {"url": "https://www.nfl.com/news/2025/09/01/article-1", "lastmod": "2025-09-01"},
        {"url": "https://www.nfl.com/news/2025/09/02/article-2", "lastmod": "2025-09-02"},
    ]
    nfl_articles = [
        {
            "title": "A1",
            "url": sitemap_urls[0]["url"],
            "content": "A1 content " * 10,
            "publish_date": "2025-09-01T10:00:00Z",
            "author": "Author 1",
            "publisher": "NFL.com",
        },
        {
            "title": "A2",
            "url": sitemap_urls[1]["url"],
            "content": "A2 content " * 10,
            "publish_date": "2025-09-02T10:00:00Z",
            "author": "Author 2",
            "publisher": "NFL.com",
        },
    ]

    with (
        patch("services.sitemap_parser.fetch_sitemap", return_value="<xml></xml>"),
        patch("services.sitemap_parser.parse_sitemap", return_value=sitemap_urls),
        patch("services.nfl_extractor.extract_nfl_articles", return_value=nfl_articles),
    ):

        result = await pipeline.run_source(source_config)

    assert result["status"] == "success"
    assert result["articles_count"] == 2


@pytest.mark.asyncio
async def test_run_with_supabase_sitemap_nfl_flow():
    pipeline = SimplifiedPipeline(use_supabase=True)

    # Replace supabase repo with a mock
    mock_repo = Mock()
    mock_repo.get_watermark.return_value = None
    mock_repo.save_articles.return_value = True
    mock_repo.update_watermark.return_value = True
    mock_repo.log_processing.return_value = True
    pipeline.supabase_repo = mock_repo

    source_config = {
        "url": "https://www.nfl.com/sitemap.xml",
        "publisher": "NFL.com",
        "type": "sitemap",
    }

    sitemap_urls = [
        {"url": "https://www.nfl.com/news/2025/09/01/article-1", "lastmod": "2025-09-01"},
        {"url": "https://www.nfl.com/news/2025/09/02/article-2", "lastmod": "2025-09-02"},
    ]
    nfl_articles = [
        {
            "title": "A1",
            "url": sitemap_urls[0]["url"],
            "content": "A1 content " * 10,
            "publish_date": "2025-09-01T10:00:00Z",
            "author": "Author 1",
            "publisher": "NFL.com",
        },
        {
            "title": "A2",
            "url": sitemap_urls[1]["url"],
            "content": "A2 content " * 10,
            "publish_date": "2025-09-02T10:00:00Z",
            "author": "Author 2",
            "publisher": "NFL.com",
        },
    ]

    with (
        patch("services.sitemap_parser.fetch_sitemap", return_value="<xml></xml>"),
        patch("services.sitemap_parser.parse_sitemap", return_value=sitemap_urls),
        patch("services.nfl_extractor.extract_nfl_articles", return_value=nfl_articles),
    ):

        result = await pipeline.run_source(source_config)

    assert result["status"] == "success"
    assert result["articles_count"] == 2
    mock_repo.save_articles.assert_called()
    mock_repo.update_watermark.assert_called()
    mock_repo.log_processing.assert_called()
