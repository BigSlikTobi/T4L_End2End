"""Tests for NFL.com article extractor."""

from unittest.mock import Mock, patch

import requests

from src.services.nfl_extractor import NFLArticleExtractor


class TestNFLArticleExtractor:
    def test_init(self):
        """Test extractor initialization."""
        extractor = NFLArticleExtractor()
        assert extractor.session is not None
        # Just check that User-Agent is set, don't match exact value
        assert "User-Agent" in extractor.session.headers

    def test_is_recent_today(self):
        """Test is_recent with today's date."""
        extractor = NFLArticleExtractor()
        # Create URL with today's date pattern
        today_url = "https://www.nfl.com/news/2025/09/07/todays-article"
        assert extractor.is_recent(today_url, 7) is True

    def test_is_recent_within_range(self):
        """Test is_recent with date within range."""
        extractor = NFLArticleExtractor()
        # Create URL with recent date pattern
        recent_url = "https://www.nfl.com/news/2025/09/06/recent-article"
        assert extractor.is_recent(recent_url, 7) is True

    def test_is_recent_outside_range(self):
        """Test is_recent with date outside range."""
        extractor = NFLArticleExtractor()
        # Create URL with old date pattern
        old_url = "https://www.nfl.com/news/2024/01/01/old-article"
        assert extractor.is_recent(old_url, 7) is False

    def test_is_recent_invalid_date(self):
        """Test is_recent with invalid date format."""
        extractor = NFLArticleExtractor()
        # No date pattern found in "invalid-date", should return True
        assert extractor.is_recent("invalid-date", 7) is True

    def test_is_recent_none_date(self):
        """Test is_recent with None date."""
        extractor = NFLArticleExtractor()
        # The method expects a URL string, not a date string
        assert extractor.is_recent("", 7) is True  # No date pattern found, returns True

    @patch("src.services.nfl_extractor.requests.Session.get")
    def test_extract_article_content_success(self, mock_get):
        """Test successful article content extraction."""
        # Mock HTML content
        mock_html = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <div>
                        <p>This is the first paragraph of the article content which is long.</p>
                        <p>This is the second paragraph which is also long.</p>
                    </div>
                </article>
                <div class="author">John Doe</div>
                <time datetime="2025-09-07T10:00:00Z">September 7, 2025</time>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.content = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        extractor = NFLArticleExtractor()
        result = extractor.extract_article_content("https://www.nfl.com/news/test-article")

        assert result is not None
        assert result["title"] == "Test Article"
        assert "first paragraph" in result["content"]
        assert result["author"] == "John Doe"
        assert result["url"] == "https://www.nfl.com/news/test-article"
        assert result["publish_date"] == "2025-09-07T10:00:00Z"

    @patch("src.services.nfl_extractor.requests.Session.get")
    def test_extract_article_content_http_error(self, mock_get):
        """Test article extraction with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        extractor = NFLArticleExtractor()
        result = extractor.extract_article_content("https://www.nfl.com/news/not-found")

        assert result is None
        mock_get.assert_called_once()

    @patch("src.services.nfl_extractor.requests.Session.get")
    def test_extract_article_content_timeout(self, mock_get):
        """Test article extraction with timeout."""
        mock_get.side_effect = requests.Timeout("Timeout")

        extractor = NFLArticleExtractor()
        result = extractor.extract_article_content("https://www.nfl.com/news/timeout")

        assert result is None

    @patch("src.services.nfl_extractor.requests.Session.get")
    def test_extract_article_content_request_exception(self, mock_get):
        """Test article extraction with request exception."""
        mock_get.side_effect = requests.RequestException("Connection error")

        extractor = NFLArticleExtractor()
        result = extractor.extract_article_content("https://www.nfl.com/news/error")

        assert result is None

    @patch("src.services.nfl_extractor.requests.Session.get")
    def test_extract_article_content_minimal_html(self, mock_get):
        """Test extraction with minimal HTML structure."""
        mock_html = """
        <html>
            <head><title>Minimal Article</title></head>
            <body>
                <article>
                    <p>Some basic content that is longer than twenty characters.</p>
                </article>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.content = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        extractor = NFLArticleExtractor()
        result = extractor.extract_article_content("https://www.nfl.com/news/minimal")

        assert result is not None
        assert result["title"] == "Minimal Article"
        assert "Some basic content" in result["content"]
        assert result["author"] is None
        assert result["publish_date"] is None

    @patch.object(NFLArticleExtractor, "extract_article_content")
    @patch.object(NFLArticleExtractor, "is_recent")
    def test_process_sitemap_urls_success(self, mock_is_recent, mock_extract):
        """Test successful processing of sitemap URLs."""
        mock_sitemap_urls = [
            {"url": "https://www.nfl.com/news/article-1", "lastmod": "2025-09-07"},
            {"url": "https://www.nfl.com/news/article-2", "lastmod": "2025-09-06"},
            {"url": "https://www.nfl.com/news/article-3", "lastmod": "2025-09-01"},  # Old article
        ]

        mock_articles = [
            {
                "title": "Article 1",
                "url": "https://www.nfl.com/news/article-1",
                "content": "Content 1",
            },
            {
                "title": "Article 2",
                "url": "https://www.nfl.com/news/article-2",
                "content": "Content 2",
            },
        ]

        # First two articles are recent, third is not
        mock_is_recent.side_effect = [True, True, False]
        # Return articles for the first two URLs
        mock_extract.side_effect = [mock_articles[0], mock_articles[1]]

        extractor = NFLArticleExtractor()
        result = extractor.process_sitemap_urls(mock_sitemap_urls, max_articles=10, days_back=7)

        assert len(result) == 2
        assert result[0]["title"] == "Article 1"
        assert result[1]["title"] == "Article 2"
        # Should only extract from recent articles
        assert mock_extract.call_count == 2

    @patch.object(NFLArticleExtractor, "extract_article_content")
    @patch.object(NFLArticleExtractor, "is_recent")
    def test_process_sitemap_urls_max_articles_limit(self, mock_is_recent, mock_extract):
        """Test processing with max_articles limit."""
        mock_sitemap_urls = [
            {"url": "https://www.nfl.com/news/article-1", "lastmod": "2025-09-07"},
            {"url": "https://www.nfl.com/news/article-2", "lastmod": "2025-09-06"},
            {"url": "https://www.nfl.com/news/article-3", "lastmod": "2025-09-05"},
        ]

        # All articles are recent
        mock_is_recent.return_value = True
        mock_extract.return_value = {"title": "Test Article", "content": "Test Content"}

        extractor = NFLArticleExtractor()
        result = extractor.process_sitemap_urls(mock_sitemap_urls, max_articles=2, days_back=7)

        assert len(result) == 2
        # Should only extract from first 2 articles due to max_articles limit
        assert mock_extract.call_count == 2

    @patch.object(NFLArticleExtractor, "extract_article_content")
    @patch.object(NFLArticleExtractor, "is_recent")
    def test_process_sitemap_urls_extraction_failures(self, mock_is_recent, mock_extract):
        """Test processing with some extraction failures."""
        mock_sitemap_urls = [
            {"url": "https://www.nfl.com/news/article-1", "lastmod": "2025-09-07"},
            {"url": "https://www.nfl.com/news/article-2", "lastmod": "2025-09-06"},
        ]

        # Both articles are recent
        mock_is_recent.return_value = True
        # First extraction succeeds, second fails
        mock_extract.side_effect = [
            {"title": "Article 1", "content": "Content 1"},
            None,  # Extraction failed
        ]

        extractor = NFLArticleExtractor()
        result = extractor.process_sitemap_urls(mock_sitemap_urls, max_articles=10, days_back=7)

        assert len(result) == 1
        assert result[0]["title"] == "Article 1"

    @patch.object(NFLArticleExtractor, "is_recent")
    def test_process_sitemap_urls_no_recent_articles(self, mock_is_recent):
        """Test processing when no articles are recent."""
        mock_sitemap_urls = [
            {"url": "https://www.nfl.com/news/article-1", "lastmod": "2025-08-01"},
            {"url": "https://www.nfl.com/news/article-2", "lastmod": "2025-08-02"},
        ]

        # No articles are recent
        mock_is_recent.return_value = False

        extractor = NFLArticleExtractor()
        result = extractor.process_sitemap_urls(mock_sitemap_urls, max_articles=10, days_back=7)

        assert len(result) == 0

    def test_process_sitemap_urls_empty_list(self):
        """Test processing with empty sitemap URLs list."""
        extractor = NFLArticleExtractor()
        result = extractor.process_sitemap_urls([], max_articles=10, days_back=7)

        assert len(result) == 0

    @patch.object(NFLArticleExtractor, "process_sitemap_urls")
    def test_extract_nfl_articles_function(self, mock_process):
        """Test the standalone extract_nfl_articles function."""
        from src.services.nfl_extractor import extract_nfl_articles

        mock_sitemap_urls = [{"url": "test", "lastmod": "2025-09-07"}]
        mock_articles = [{"title": "Test", "content": "Content"}]
        mock_process.return_value = mock_articles

        result = extract_nfl_articles(mock_sitemap_urls, max_articles=5, days_back=7)

        assert result == mock_articles
        mock_process.assert_called_once_with(mock_sitemap_urls, 5, 7)
