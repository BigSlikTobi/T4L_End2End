"""Tests for Supabase integration."""

import os
from unittest.mock import Mock, patch

from src.database.supabase_simple import SimpleSupabaseRepo


class TestSimpleSupabaseRepo:
    @patch("src.database.supabase_simple.create_client")
    def test_init_success(self, mock_create_client):
        """Test successful repository initialization."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            assert repo.client == mock_client
            mock_create_client.assert_called_once_with("https://test.supabase.co", "test_key")

    def test_init_missing_url(self):
        """Test initialization with missing URL."""
        with patch.dict(os.environ, {"SUPABASE_ANON_KEY": "test_key"}, clear=True):
            # Should create repo with None client
            repo = SimpleSupabaseRepo()
            assert repo.client is None

    def test_init_missing_key(self):
        """Test initialization with missing key."""
        with patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co"}, clear=True):
            # Should create repo with None client
            repo = SimpleSupabaseRepo()
            assert repo.client is None

    @patch("src.database.supabase_simple.create_client")
    def test_save_articles_success(self, mock_create_client):
        """Test successful article saving."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": 1}, {"id": 2}])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()

            articles = [
                {"title": "Article 1", "url": "https://example.com/1", "publisher": "Test"},
                {"title": "Article 2", "url": "https://example.com/2", "publisher": "Test"},
            ]

            result = repo.save_articles(articles)

            assert result is True  # Returns bool, not count
            mock_client.table.assert_called_with("articles")
            mock_table.insert.assert_called_once_with(articles)

    @patch("src.database.supabase_simple.create_client")
    def test_save_articles_empty_list(self, mock_create_client):
        """Test saving empty articles list."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.save_articles([])
            assert result is False  # Returns False for empty list

    @patch("src.database.supabase_simple.create_client")
    def test_save_articles_exception(self, mock_create_client):
        """Test article saving with exception."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.side_effect = Exception("Database error")
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()

            articles = [{"title": "Article 1", "url": "https://example.com/1"}]

            # The method catches exceptions and returns False
            result = repo.save_articles(articles)
            assert result is False

    @patch("src.database.supabase_simple.create_client")
    def test_get_watermark_exists(self, mock_create_client):
        """Test getting existing watermark."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"last_processed": "2025-09-07T10:00:00Z"}])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.get_watermark("test_source")

            assert result == "2025-09-07T10:00:00Z"
            mock_table.eq.assert_called_with("source_key", "test_source")

    @patch("src.database.supabase_simple.create_client")
    def test_get_watermark_not_exists(self, mock_create_client):
        """Test getting non-existent watermark."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.get_watermark("test_source")

            assert result is None

    @patch("src.database.supabase_simple.create_client")
    def test_update_watermark_insert(self, mock_create_client):
        """Test updating watermark (insert case)."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": 1}])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.update_watermark("test_source", "2025-09-07T10:00:00Z")

            expected_data = {"source_key": "test_source", "last_processed": "2025-09-07T10:00:00Z"}
            mock_table.upsert.assert_called_once_with(expected_data)
            assert result is True

    @patch("src.database.supabase_simple.create_client")
    def test_log_processing_success(self, mock_create_client):
        """Test successful processing log."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": 1}])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.log_processing("test_source", "success", "All good")

            # Check that insert was called with correct structure
            call_args = mock_table.insert.call_args[0][0]
            assert call_args["source_key"] == "test_source"
            assert call_args["status"] == "success"
            assert call_args["message"] == "All good"
            assert call_args["timestamp"] == "now()"
            assert result is True

    @patch("src.database.supabase_simple.create_client")
    def test_log_processing_with_error(self, mock_create_client):
        """Test processing log with error."""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[{"id": 1}])
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
        ):
            repo = SimpleSupabaseRepo()
            result = repo.log_processing("test_source", "error", "Connection failed")

            call_args = mock_table.insert.call_args[0][0]
            assert call_args["status"] == "error"
            assert call_args["message"] == "Connection failed"
            assert result is True

    def test_client_none_handling(self):
        """Test handling when client is None."""
        repo = SimpleSupabaseRepo(client=None)

        # All methods should return False/None when client is None
        assert repo.save_articles([{"title": "test"}]) is False
        assert repo.get_watermark("test") is None
        assert repo.update_watermark("test", "timestamp") is False
        assert repo.log_processing("test", "success") is False
