from __future__ import annotations

import json

from click.testing import CliRunner

import src.cli as cli_mod
from src.cli.commands.health import health_cmd


def test_cli_import_and_help():
    # Importing the CLI module executes definitions for coverage
    assert hasattr(cli_mod, "cli")
    runner = CliRunner()
    # Help on bare group works (even without subcommands attached here)
    result = runner.invoke(cli_mod.cli, ["--help"])  # type: ignore[arg-type]
    assert result.exit_code == 0


def test_health_command_outputs_json():
    runner = CliRunner()
    result = runner.invoke(health_cmd)
    assert result.exit_code == 0
    data = json.loads(result.output.strip())
    assert "timestamp" in data and "database" in data
