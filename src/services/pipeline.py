from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .feed_ingester import FeedIngester
from .relevance_filter import FilterDecision, RelevanceFilter
from .sitemap_parser import fetch_sitemap, parse_sitemap
from .logger import log_json
from ..database.repositories.article_repo import ArticleRepository
from ..database.repositories.log_repo import ProcessingLogRepository
from ..database.repositories.watermark_repo import WatermarkRepository


class Pipeline:
    def __init__(self) -> None:
        self.ingester = FeedIngester()
        self.filter = RelevanceFilter()
        self.article_repo = ArticleRepository()
        self.log_repo = ProcessingLogRepository()
        self.watermarks = WatermarkRepository()

    async def run_from_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        defaults = cfg.get("defaults", {})
        sources = cfg.get("sources", [])
        results: Dict[str, Any] = {"total": 0, "kept": 0, "rejected": 0, "escalated": 0}

        for src in sources:
            if not src.get("enabled", True):
                continue
            st = await self._process_source(src, defaults)
            for k, v in st.items():
                results[k] = results.get(k, 0) + v
        return results

    async def _process_source(self, src: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, int]:
        st = {"total": 0, "kept": 0, "rejected": 0, "escalated": 0}
        name = src.get("name") or src.get("url")
        source_key = name or "unknown"

        # Load watermark
        wm = self.watermarks.get(source_key)
        last_dt = wm.last_publication_date if wm else None
        last_url = wm.last_url if wm else None

        items: List[Dict[str, Any]] = []
        if src.get("type") == "rss":
            feed_url = src.get("url")
            feed = await self.ingester.fetch_feed(feed_url)
            raw = await self.ingester.extract_articles(feed)
            for r in raw:
                items.append(self.ingester.standardize_article(r))
        elif src.get("type") == "sitemap":
            url = src.get("url") or src.get("url_template")
            xml = await asyncio.to_thread(fetch_sitemap, url)
            urls = parse_sitemap(xml)
            for u in urls:
                items.append({
                    "url": u["url"],
                    "title": u.get("url"),
                    "publisher": src.get("publisher", ""),
                    "publication_date": u.get("lastmod"),
                })
        else:
            log_json("WARNING", "Unsupported source type", source=source_key, type=src.get("type"))
            return st

        # De-dup by URL and incremental watermarking
        seen: set[str] = set()
        def newer_than_watermark(it: Dict[str, Any]) -> bool:
            dt = it.get("publication_date")
            url = it.get("url")
            if last_dt and dt:
                try:
                    from datetime import datetime
                    d = datetime.fromisoformat(str(dt).replace("Z", "+00:00"))
                    return d > last_dt
                except Exception:
                    # fallback to URL check
                    return url != last_url
            if last_url:
                return url != last_url
            return True

        filtered_items: List[Dict[str, Any]] = []
        for it in items:
            url = it.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            if not newer_than_watermark(it):
                continue
            filtered_items.append(it)

        st["total"] = len(filtered_items)

        # Filtering and persistence
        newest_dt = last_dt
        newest_url = last_url
        for it in filtered_items:
            decision, score = self.filter.filter_article(it)
            if decision is FilterDecision.KEEP:
                st["kept"] += 1
                # persist
                obj = self.article_repo.upsert(it)
                self.log_repo.add("INFO", "kept", article_url=it.get("url"), metadata=str({"score": score}))
                # watermark update candidate
                dt = obj.publication_date
                if dt and (newest_dt is None or dt > newest_dt):
                    newest_dt = dt
                    newest_url = obj.url
            elif decision is FilterDecision.REJECT:
                st["rejected"] += 1
            else:
                st["escalated"] += 1

        # Save watermark
        self.watermarks.upsert(source_key, newest_dt, newest_url)
        return st


__all__ = ["Pipeline"]
