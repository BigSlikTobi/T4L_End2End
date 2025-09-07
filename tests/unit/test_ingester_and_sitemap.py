from __future__ import annotations

from textwrap import dedent

from src.services.feed_ingester import FeedIngester
from src.services.sitemap_parser import apply_dynamic_template, parse_sitemap


def test_standardize_article_handles_variants():
    ing = FeedIngester()
    raw = {
        "link": "https://example.com/a",
        "title": "Hello",
        "publisher": "X",
        "summary": "S",
    }
    art = ing.standardize_article(raw)
    assert art["url"] == "https://example.com/a"
    assert art["title"] == "Hello"
    assert art["publisher"] == "X"
    assert art["content_summary"] == "S"

    # Fallbacks
    raw2 = {"url": "u", "source": "Y", "description": "D"}
    art2 = ing.standardize_article(raw2)
    assert art2["url"] == "u"
    assert art2["publisher"] == "Y"
    assert art2["content_summary"] == "D"


def test_apply_dynamic_template_and_parse_sitemap():
    # Template unchanged when placeholders absent
    assert apply_dynamic_template("https://example.com/static.xml").endswith("static.xml")

    xml = dedent(
        """
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://ex.com/1</loc><lastmod>2025-09-07</lastmod></url>
          <url><loc>https://ex.com/2</loc></url>
        </urlset>
        """
    ).strip()
    items = parse_sitemap(xml)
    assert items[0]["url"] == "https://ex.com/1"
    assert items[0]["lastmod"] == "2025-09-07"
    assert items[1]["url"] == "https://ex.com/2"
