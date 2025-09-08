"""Simplified Supabase integration using the Python client."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client


def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if credentials are available."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        return None

    return create_client(url, key)


class SimpleSupabaseRepo:
    """Simple repository using Supabase client directly."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()

    def save_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Save articles to Supabase articles table."""
        if not self.client:
            return False

        try:
            # No work to do
            if not articles:
                return False

            table = self.client.table("articles")

            # Prefer upsert with conflict on URL, ignoring duplicates so the batch doesn't fail
            try:
                # Some versions of supabase-py/postgrest support ignore_duplicates
                table.upsert(articles, on_conflict="url", ignore_duplicates=True).execute()
                # Treat as success even if all were duplicates (result.data may be empty)
                return True
            except TypeError:
                # Fallback for older client signature without ignore_duplicates
                table.upsert(articles, on_conflict="url").execute()
                return True
            except Exception:
                # As a last resort, fall back to per-row insert and ignore duplicates
                inserted_any = False
                for row in articles:
                    try:
                        table.insert(row).execute()
                        inserted_any = True
                    except Exception as ex:
                        # Ignore unique violations on url; re-raise only for other errors
                        msg = str(ex)
                        if "duplicate key value" in msg or "23505" in msg:
                            continue
                        raise
                return inserted_any or True  # If all were duplicates, still a logical success
        except Exception as e:
            print(f"Failed to save articles to Supabase: {e}")
            return False

    def get_watermark(self, source_key: str) -> Optional[str]:
        """Get the last processed timestamp for a source."""
        if not self.client:
            return None

        try:
            result = (
                self.client.table("watermarks")
                .select("last_processed")
                .eq("source_key", source_key)
                .execute()
            )

            if result.data:
                return result.data[0]["last_processed"]
            return None
        except Exception as e:
            print(f"Failed to get watermark: {e}")
            return None

    def update_watermark(self, source_key: str, timestamp: str) -> bool:
        """Update the watermark for a source."""
        if not self.client:
            return False

        try:
            result = (
                self.client.table("watermarks")
                .upsert({"source_key": source_key, "last_processed": timestamp})
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Failed to update watermark: {e}")
            return False

    def log_processing(self, source_key: str, status: str, message: str = "") -> bool:
        """Log processing status."""
        if not self.client:
            return False

        try:
            result = (
                self.client.table("processing_logs")
                .insert(
                    {
                        "source_key": source_key,
                        "status": status,
                        "message": message,
                        "timestamp": "now()",
                    }
                )
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Failed to log processing: {e}")
            return False


def convert_article_to_dict(article) -> Dict[str, Any]:
    """Convert article object to dict for Supabase insertion."""
    return {
        "title": article.title,
        "url": article.url,
        "content": article.content,
        "author": article.author,
        "published_date": article.published_date.isoformat() if article.published_date else None,
        "source": article.source,
        "publisher": article.publisher,
        "tags": article.tags,
        "extracted_at": article.extracted_at.isoformat() if article.extracted_at else None,
    }
