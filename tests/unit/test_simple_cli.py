"""Tests for simplified CLI commands."""

import os
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from cli.commands.simple import simple_pipeline


class TestSimplePipelineCommand:
    def test_simple_pipeline_local_mode(self):
        """Test simple pipeline command in local mode."""
        runner = CliRunner()

        async_results = [
            {"status": "success", "articles_count": 5, "source_key": "test_source"},
            {"status": "success", "articles_count": 0, "source_key": "another_source"},
        ]

        with patch(
            "cli.commands.simple.run_simplified_pipeline", new_callable=AsyncMock
        ) as mock_run:
            mock_run.return_value = async_results

            result = runner.invoke(simple_pipeline, ["--config", "test_config.yaml"])

            assert result.exit_code == 0
            out = result.output
            assert "🚀 Running pipeline with local SQLite..." in out
            # Summary lines
            assert "Sources processed: 2" in out
            assert "Successful: 2" in out
            assert "Total articles: 5" in out
            # Per-source lines
            assert "✅ test_source: 5 articles" in out
            assert "✅ another_source: 0 articles" in out

    def test_simple_pipeline_supabase_mode_valid_creds(self):
        """Test simple pipeline command in Supabase mode with valid credentials."""
        runner = CliRunner()

        with (
            patch(
                "cli.commands.simple.run_simplified_pipeline", new_callable=AsyncMock
            ) as mock_run,
            patch.dict(
                os.environ,
                {"SUPABASE_URL": "https://test.supabase.co", "SUPABASE_ANON_KEY": "test_key"},
            ),
        ):

            mock_run.return_value = [
                {"status": "success", "articles_count": 10, "source_key": "supabase_source"}
            ]

            result = runner.invoke(simple_pipeline, ["--config", "test_config.yaml", "--supabase"])

            assert result.exit_code == 0
            out = result.output
            assert "🚀 Running pipeline with Supabase integration..." in out
            assert "Data saved to: Supabase" in out

    def test_simple_pipeline_supabase_mode_invalid_creds(self):
        """Test simple pipeline command in Supabase mode with invalid credentials."""
        runner = CliRunner()

        with patch.dict(os.environ, {}, clear=True):  # Clear env vars
            result = runner.invoke(simple_pipeline, ["--config", "test_config.yaml", "--supabase"])

            assert result.exit_code == 0  # Command returns but shows error message
            assert "❌ SUPABASE_URL and SUPABASE_ANON_KEY" in result.output
