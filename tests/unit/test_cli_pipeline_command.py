from __future__ import annotations

from click.testing import CliRunner

from src.cli.commands.pipeline import pipeline as pipeline_cmd


def test_pipeline_cli_invokes_run(monkeypatch, tmp_path):
    # Create a minimal config
    cfg = tmp_path / "feeds.yaml"
    cfg.write_text(
        """
version: 1
defaults: {max_parallel_fetches: 1}
sources:
  - name: Dummy
    type: rss
    url: https://example.com/rss
    publisher: Test
    enabled: false
        """,
        encoding="utf-8",
    )

    class FakePipeline:
        async def run_from_config(self, *args, **kwargs):
            return {"total": 0, "kept": 0, "rejected": 0, "escalated": 0}

    # Patch Pipeline constructor in the command module scope
    monkeypatch.setattr("src.cli.commands.pipeline.Pipeline", lambda: FakePipeline())

    runner = CliRunner()
    res = runner.invoke(pipeline_cmd, ["--config", str(cfg), "--only-publisher", "ESPN"])
    assert res.exit_code == 0
    assert "'total': 0" in res.output
