from __future__ import annotations

import runpy
import sys


def test_running_cli_module_shows_help(monkeypatch):
    argv = ["python", "--help"]
    monkeypatch.setattr(sys, "argv", argv)
    # This executes src/cli/__main__.py as if `python -m src.cli`
    try:
        runpy.run_module("src.cli.__main__", run_name="__main__")
    except SystemExit as e:
        # click exits after showing help with code 0
        assert e.code == 0
