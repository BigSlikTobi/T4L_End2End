from __future__ import annotations

from click.testing import CliRunner

from src.cli import cli
from src.cli.commands.filter import filter_cmd
from src.cli.commands.ingest import ingest
from src.cli.commands.pipeline import pipeline


def test_filter_command_runs_with_minimal_args():
    runner = CliRunner()
    res = runner.invoke(filter_cmd, ["--title", "Patriots", "--url", "https://ex.com/nfl"])
    assert res.exit_code == 0


def test_ingest_help_and_pipeline_help():
    runner = CliRunner()
    assert runner.invoke(ingest, ["--help"]).exit_code == 0
    assert runner.invoke(pipeline, ["--help"]).exit_code == 0


def test_root_cli_help():
    runner = CliRunner()
    # Invoke the group object directly with explicit --help
    res = runner.invoke(cli, ["--help"])  # type: ignore[arg-type]
    assert res.exit_code == 0
