"""Simple CLI command to run pipeline with optional Supabase integration."""

import asyncio
import os

import click

from services.simple_pipeline import run_simplified_pipeline


@click.command(name="simple", help="Run a simplified pipeline that can optionally use Supabase.")
@click.option("--config", default="config/feeds.yaml", help="Path to feeds configuration file")
@click.option("--allowlist", default=None, help="Optional path to allowlist.yaml (overrides env)")
@click.option("--supabase", is_flag=True, help="Use Supabase instead of local SQLite")
def simple_pipeline(config: str, allowlist: str | None, supabase: bool):
    """Run a simplified pipeline that can optionally use Supabase directly."""

    if supabase:
        # Check for Supabase credentials
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY"):
            click.echo(
                "❌ SUPABASE_URL and SUPABASE_ANON_KEY environment variables "
                "required for --supabase mode"
            )
            return

        click.echo("🚀 Running pipeline with Supabase integration...")
    else:
        click.echo("🚀 Running pipeline with local SQLite...")

    async def run():
        # Allowlist override via env variable for extractor
        if allowlist:
            os.environ["T4L_ALLOWLIST_PATH"] = allowlist
        results = await run_simplified_pipeline(config, use_supabase=supabase)

        total_articles = sum(r.get("articles_count", 0) for r in results)
        success_count = sum(1 for r in results if r.get("status") == "success")

        click.echo("\n✅ Pipeline completed:")
        click.echo(f"   Sources processed: {len(results)}")
        click.echo(f"   Successful: {success_count}")
        click.echo(f"   Total articles: {total_articles}")

        if supabase:
            click.echo("   Data saved to: Supabase")
        else:
            click.echo("   Data saved to: Local SQLite")

        for result in results:
            status_icon = "✅" if result.get("status") == "success" else "❌"
            source_key = result.get("source_key", "unknown")
            article_count = result.get("articles_count", 0)
            click.echo(f"   {status_icon} {source_key}: {article_count} articles")

    asyncio.run(run())
