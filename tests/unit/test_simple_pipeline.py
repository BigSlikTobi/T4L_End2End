"""Tests for the simplified pipeline functionality."""

from unittest.mock import AsyncMock, mock_open, patch

import pytest

from src.services.simple_pipeline import SimplifiedPipeline, run_simplified_pipeline


class TestSimplifiedPipeline:
    def test_init(self):
        """Test pipeline initialization."""
        # Check actual implementation
        pipeline = SimplifiedPipeline(use_supabase=False)
        assert pipeline.use_supabase is False
        # The actual implementation creates a local_pipeline when needed
        assert hasattr(pipeline, "supabase_repo")

        pipeline_sb = SimplifiedPipeline(use_supabase=True)
        assert pipeline_sb.use_supabase is True

    @pytest.mark.asyncio
    async def test_run_source_no_url(self):
        """Test handling of source with no URL."""
        pipeline = SimplifiedPipeline(use_supabase=False)

        source_config = {
            "publisher": "Test Publisher"
            # No url or url_template
        }

        result = await pipeline.run_source(source_config)

        assert result["status"] == "error"
        assert result["articles_count"] == 0
        assert "No URL provided" in result["error"]

    @pytest.mark.asyncio
    async def test_run_source_with_basic_url(self):
        """Test source with basic URL."""
        pipeline = SimplifiedPipeline(use_supabase=False)

        source_config = {
            "url": "https://example.com/rss",
            "publisher": "Test Publisher",
            "type": "rss",
        }

        # Mock the ingester and its methods
        with patch("src.services.feed_ingester.FeedIngester") as mock_ingester:
            mock_instance = mock_ingester.return_value
            mock_instance.fetch_feed = AsyncMock(
                return_value={"status": 200, "content": "<rss></rss>"}
            )
            mock_instance.extract_articles = AsyncMock(return_value=[])

            result = await pipeline.run_source(source_config)

            assert result["status"] == "success"
            assert result["articles_count"] == 0


@pytest.mark.asyncio
async def test_run_simplified_pipeline():
    """Test the main pipeline runner function."""
    mock_config = {
        "sources": [{"url": "https://example.com/rss", "publisher": "Test", "type": "rss"}]
    }

    with (
        patch("builtins.open", mock_open(read_data="mock yaml content")),
        patch("yaml.safe_load") as mock_yaml,
        patch.object(SimplifiedPipeline, "run_source") as mock_run_source,
    ):

        mock_yaml.return_value = mock_config
        mock_run_source.return_value = {"status": "success", "articles_count": 5}

        results = await run_simplified_pipeline("config.yaml", use_supabase=False)

        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["articles_count"] == 5
