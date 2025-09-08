"""Simplified pipeline that can optionally use Supabase directly."""

from __future__ import annotations

from typing import Any, Dict, List

from database.connection import get_sessionmaker
from database.supabase_simple import SimpleSupabaseRepo
from models import (
    ClaimORM,
    ClaimSourceORM,
    EventArticleORM,
    EventORM,
    SourceORM,
)
from services.claim_extractor import extract_allowlisted_claims
from services.confidence import compute_event_confidence
from services.feed_ingester import FeedIngester
from services.pipeline import Pipeline
from services.signature import event_signature


class SimplifiedPipeline:
    """Pipeline that can work with local SQLite or simple Supabase integration."""

    def __init__(self, use_supabase: bool = False):
        self.use_supabase = use_supabase
        self.supabase_repo = SimpleSupabaseRepo() if use_supabase else None
        self.local_pipeline = Pipeline() if not use_supabase else None

    async def run_source(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run pipeline for a single source."""
        # Handle url_template for NFL.com-style dynamic URLs
        url = source_config.get("url")
        if not url and source_config.get("url_template"):
            from datetime import datetime

            now = datetime.now()
            url = (
                source_config["url_template"]
                .replace("{YYYY}", str(now.year))
                .replace("{MM}", f"{now.month:02d}")
            )
            print(f"Expanded URL template: {url}")

        if not url:
            print(f"❌ No URL found for {source_config.get('publisher', 'unknown')}")
            return {
                "source_key": f"{source_config.get('publisher', 'unknown')}:no-url",
                "articles_count": 0,
                "status": "error",
                "error": "No URL provided",
            }

        source_key = f"{source_config.get('publisher', 'unknown')}:{url}"

        print(f"Processing {source_key}")

        # Update source_config with resolved URL
        source_config = source_config.copy()
        source_config["url"] = url

        if self.use_supabase and self.supabase_repo:
            return await self._run_with_supabase(source_config, source_key)
        else:
            return await self._run_with_local(source_config)

    async def _run_with_supabase(
        self, source_config: Dict[str, Any], source_key: str
    ) -> Dict[str, Any]:
        """Run with Supabase integration."""
        try:
            # Get watermark
            last_processed = self.supabase_repo.get_watermark(source_key)
            print(f"Last processed: {last_processed}")

            # Ingest articles using the correct FeedIngester interface
            feed_type = source_config.get("type", "rss")
            print(f"Ingesting from {source_config['url']} (type: {feed_type})")

            if feed_type == "sitemap":
                # Handle sitemap parsing
                from services.nfl_extractor import extract_nfl_articles
                from services.sitemap_parser import fetch_sitemap, parse_sitemap

                xml_text = fetch_sitemap(source_config["url"])
                sitemap_urls = parse_sitemap(xml_text)

                print(f"Found {len(sitemap_urls)} URLs in sitemap")

                # Extract full articles with content (NFL.com specific)
                if "nfl.com" in source_config["url"].lower():
                    max_articles = source_config.get("max_articles", 30)  # Configurable
                    days_back = source_config.get("days_back", 7)  # Configurable
                    nfl_articles = extract_nfl_articles(sitemap_urls, max_articles, days_back)

                    # Convert to standardized format
                    articles = []
                    for article in nfl_articles:
                        articles.append(
                            {
                                "title": article.get("title"),
                                "url": article.get("url"),
                                "content_summary": (
                                    article.get("content", "")[:500] + "..."
                                    if len(article.get("content", "")) > 500
                                    else article.get("content", "")
                                ),
                                "publisher": article.get("publisher"),
                                "publication_date": article.get("publish_date"),
                                "author": article.get("author"),
                            }
                        )
                else:
                    # For other sitemaps, use simple URL extraction
                    articles = []
                    for url_entry in sitemap_urls[:10]:  # Limit for demo
                        articles.append(
                            {
                                "title": f"Article from {source_config.get('publisher')}",
                                "url": url_entry["url"],
                                "content_summary": "Article from sitemap",
                                "publisher": source_config.get("publisher"),
                                "publication_date": url_entry.get("lastmod"),
                            }
                        )

            else:
                # Handle RSS feeds
                ingester = FeedIngester()

                # Fetch feed data
                feed_data = await ingester.fetch_feed(source_config["url"])
                if feed_data.get("status") != 200:
                    raise Exception(f"HTTP {feed_data.get('status')}")

                # Extract articles
                raw_articles = await ingester.extract_articles(feed_data)

                # Standardize articles
                articles = [ingester.standardize_article(raw) for raw in raw_articles]

            print(f"Ingested {len(articles)} articles")

            if not articles:
                self.supabase_repo.log_processing(source_key, "success", "No new articles")
                return {"source_key": source_key, "articles_count": 0, "status": "success"}

            # Convert to dicts for Supabase (use the correct format)
            article_dicts = []
            for article in articles:
                article_dicts.append(
                    {
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "content": article.get(
                            "content_summary"
                        ),  # Use content_summary from standardized format
                        "author": article.get("author"),
                        "published_date": article.get("publication_date"),
                        "source": article.get("url"),  # Source URL
                        "publisher": article.get("publisher"),
                        "tags": [],  # Empty for now
                        "extracted_at": None,  # Will use NOW() in Supabase
                    }
                )

            # Save to Supabase
            success = self.supabase_repo.save_articles(article_dicts)

            if success:
                # Update watermark with current timestamp
                from datetime import datetime

                current_time = datetime.now().isoformat()
                self.supabase_repo.update_watermark(source_key, current_time)

                self.supabase_repo.log_processing(
                    source_key, "success", f"Processed {len(articles)} articles"
                )
                return {
                    "source_key": source_key,
                    "articles_count": len(articles),
                    "status": "success",
                }
            else:
                self.supabase_repo.log_processing(source_key, "error", "Failed to save articles")
                return {"source_key": source_key, "articles_count": 0, "status": "error"}

        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            print(error_msg)
            if self.supabase_repo:
                self.supabase_repo.log_processing(source_key, "error", error_msg)
            return {
                "source_key": source_key,
                "articles_count": 0,
                "status": "error",
                "error": error_msg,
            }

    async def _run_with_local(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run with local SQLite (using existing services directly)."""
        # Use absolute imports when needed inside function scope

        try:
            # Use FeedIngester directly instead of full pipeline
            feed_type = source_config.get("type", "rss")
            print(f"Ingesting from {source_config['url']} (type: {feed_type})")

            if feed_type == "sitemap":
                # Handle sitemap parsing
                from services.nfl_extractor import extract_nfl_articles
                from services.sitemap_parser import fetch_sitemap, parse_sitemap

                xml_text = fetch_sitemap(source_config["url"])
                sitemap_urls = parse_sitemap(xml_text)

                print(f"Found {len(sitemap_urls)} URLs in sitemap")

                # Extract full articles with content (NFL.com specific)
                if "nfl.com" in source_config["url"].lower():
                    max_articles = 30  # Process up to 30 recent articles
                    days_back = 7  # Only articles from last 7 days
                    articles = extract_nfl_articles(sitemap_urls, max_articles, days_back)

                    # Convert to standardized format
                    standardized_articles = []
                    for article in articles:
                        standardized_articles.append(
                            {
                                "title": article.get("title"),
                                "url": article.get("url"),
                                "content_summary": (
                                    article.get("content", "")[:500] + "..."
                                    if len(article.get("content", "")) > 500
                                    else article.get("content", "")
                                ),
                                "publisher": article.get("publisher"),
                                "publication_date": article.get("publish_date"),
                                "author": article.get("author"),
                            }
                        )
                    articles = standardized_articles
                else:
                    # For other sitemaps, use simple URL extraction
                    articles = []
                    for url_entry in sitemap_urls[:10]:  # Limit for demo
                        articles.append(
                            {
                                "title": f"Article from {source_config.get('publisher')}",
                                "url": url_entry["url"],
                                "content_summary": "Article from sitemap",
                                "publisher": source_config.get("publisher"),
                                "publication_date": url_entry.get("lastmod"),
                            }
                        )

            else:
                # Handle RSS feeds
                ingester = FeedIngester()

                # Fetch feed data
                feed_data = await ingester.fetch_feed(source_config["url"])
                if feed_data.get("status") != 200:
                    raise Exception(f"HTTP {feed_data.get('status')}")

                # Extract articles
                raw_articles = await ingester.extract_articles(feed_data)

                # Standardize articles
                articles = [ingester.standardize_article(raw) for raw in raw_articles]

            print(f"Ingested {len(articles)} articles")

            if not articles:
                return {
                    "source_key": f"{source_config.get('publisher')}:{source_config.get('url')}",
                    "articles_count": 0,
                    "status": "success",
                }

            # For local mode, we'll just return the count (could save to SQLite here if needed)
            # Persist minimal event records via signature clustering
            sm = get_sessionmaker()
            with sm() as session:
                created_or_linked = 0
                import hashlib
                from datetime import datetime, timezone

                for a in articles:
                    title = a.get("title") or ""
                    pub = a.get("publication_date")
                    pub_dt = None
                    try:
                        if isinstance(pub, str):
                            from dateutil import parser as dtp  # type: ignore

                            pub_dt = dtp.parse(pub)
                        elif pub:
                            pub_dt = pub
                    except Exception:
                        pub_dt = None

                    sig = event_signature(title, pub_dt)
                    ev = session.query(EventORM).filter_by(signature=sig).one_or_none()
                    now = datetime.now(timezone.utc)
                    if not ev:
                        ev = EventORM(
                            signature=sig,
                            event_date=pub_dt,
                            event_type=None,
                            title=title,
                            summary=a.get("content_summary"),
                            confidence=None,
                            created_at=now,
                            updated_at=now,
                        )
                        session.add(ev)
                        session.flush()
                    else:
                        ev.updated_at = now

                    # Link article using a stable pseudo ID derived from URL to avoid duplicates
                    url = a.get("url") or ""
                    if url:
                        # Stable 31-bit id; negative to avoid clashing with real positive IDs
                        pseudo_id = -(
                            int(hashlib.sha1(url.encode("utf-8")).hexdigest(), 16) % 2147483647
                        )
                    else:
                        pseudo_id = 0

                    exists = (
                        session.query(EventArticleORM)
                        .filter_by(event_id=ev.id, article_id=pseudo_id)
                        .one_or_none()
                    )
                    if not exists:
                        session.add(
                            EventArticleORM(
                                event_id=ev.id, article_id=pseudo_id, relation="primary"
                            )
                        )
                        created_or_linked += 1
                    # Extract allowlisted claims and persist with provenance
                    content_summary = a.get("content_summary") or ""
                    claims = extract_allowlisted_claims(title, content_summary)
                    if claims:
                        # Ensure a Source row exists for the publisher/url combo (simplified)
                        src_name = a.get("publisher") or "unknown"
                        src_url = a.get("url") or None
                        source = (
                            session.query(SourceORM)
                            .filter_by(name=src_name, url=src_url)
                            .one_or_none()
                        )
                        if not source:
                            source = SourceORM(name=src_name, publisher=src_name, url=src_url)
                            session.add(source)
                            session.flush()
                        for c in claims:
                            existing_claim = (
                                session.query(ClaimORM)
                                .filter_by(event_id=ev.id, claim_text=c.text)
                                .one_or_none()
                            )
                            if existing_claim:
                                claim_id = existing_claim.id
                            else:
                                claim_row = ClaimORM(
                                    event_id=ev.id, claim_text=c.text, status=c.status
                                )
                                session.add(claim_row)
                                session.flush()
                                claim_id = claim_row.id
                            session.add(
                                ClaimSourceORM(
                                    claim_id=claim_id,
                                    source_id=source.id,
                                    url=src_url,
                                    citation=c.citation,
                                )
                            )

                # Compute naive confidence after processing batch
                if created_or_linked:
                    # Use a placeholder evidence list; real integration will provide tiers/dates
                    conf = compute_event_confidence([{"source_tier": "C", "published_at": None}])
                    for ev in session.query(EventORM).all():
                        if ev.confidence is None:
                            ev.confidence = conf
                session.commit()

            return {
                "source_key": f"{source_config.get('publisher')}:{source_config.get('url')}",
                "articles_count": len(articles),
                "status": "success",
            }

        except Exception as e:
            print(f"Error processing {source_config.get('url')}: {e}")
            return {
                "source_key": f"{source_config.get('publisher')}:{source_config.get('url')}",
                "articles_count": 0,
                "status": "error",
                "error": str(e),
            }


async def run_simplified_pipeline(
    config_path: str, use_supabase: bool = False
) -> List[Dict[str, Any]]:
    """Run the simplified pipeline."""
    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    pipeline = SimplifiedPipeline(use_supabase=use_supabase)
    results = []

    for source in config.get("sources", []):
        result = await pipeline.run_source(source)
        results.append(result)

    return results
