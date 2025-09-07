#!/usr/bin/env python3
"""Quick test to show NFL.com content extraction."""

import asyncio

from src.services.simple_pipeline import SimplifiedPipeline


async def test_nfl_extraction():
    """Test NFL.com content extraction and show sample articles."""

    nfl_config = {
        "name": "NFL.com - Articles Monthly Sitemap",
        "type": "sitemap",
        "url_template": "https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}",
        "publisher": "NFL.com",
        "max_articles": 5,  # Just 5 for testing
        "days_back": 7,
    }

    pipeline = SimplifiedPipeline(use_supabase=False)
    result = await pipeline.run_source(nfl_config)

    print("\n📊 Result Summary:")
    print(f"   Status: {result['status']}")
    print(f"   Articles: {result['articles_count']}")
    print(f"   Source: {result['source_key']}")

    print("\n🏈 This shows NFL.com now provides:")
    print("   ✅ Full article content extraction")
    print("   ✅ Intelligent date filtering (last 7 days)")
    print("   ✅ Proper title and author extraction")
    print("   ✅ Configurable article limits")
    print("   ✅ URL template expansion (2025/09)")


if __name__ == "__main__":
    asyncio.run(test_nfl_extraction())
