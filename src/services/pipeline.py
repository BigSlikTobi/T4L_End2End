from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

import yaml

from ..database.repositories.article_repo import ArticleRepository
from ..database.repositories.log_repo import ProcessingLogRepository
from ..database.repositories.watermark_repo import WatermarkRepository
from .async_processor import map_async, retry
from .feed_ingester import FeedIngester
from .logger import log_json
from .metrics import Metrics
from .relevance_filter import FilterDecision, RelevanceFilter
from .sitemap_parser import fetch_sitemap, parse_sitemap


class Pipeline:
    def __init__(self) -> None:
        self.ingester = FeedIngester()
        self.filter = RelevanceFilter()
        self.article_repo = ArticleRepository()
        self.log_repo = ProcessingLogRepository()
        self.watermarks = WatermarkRepository()

    @staticmethod
    def _to_aware_utc(dt_obj: Any | None) -> datetime | None:
        """Coerce various datetime-like values to timezone-aware UTC datetimes.

        Accepts datetime or ISO8601 string (with or without 'Z'). Returns None on failure.
        """
        if dt_obj is None:
            return None
        d: datetime | None
        if isinstance(dt_obj, datetime):
            d = dt_obj
        else:
            try:
                d = datetime.fromisoformat(str(dt_obj).replace("Z", "+00:00"))
            except Exception:
                return None
        if d.tzinfo is None:
            return d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)

    async def run_from_config(
        self,
        config_path: str,
        only_publishers: list[str] | None = None,
        only_sources: list[str] | None = None,
    ) -> Dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        defaults = cfg.get("defaults", {})
        sources = cfg.get("sources", [])
        if only_publishers:
            sources = [s for s in sources if (s.get("publisher") or "").strip() in only_publishers]
        if only_sources:
            sources = [s for s in sources if (s.get("name") or "").strip() in only_sources]
        results: Dict[str, Any] = {"total": 0, "kept": 0, "rejected": 0, "escalated": 0}

        for src in sources:
            if not src.get("enabled", True):
                continue
            with Metrics.time("pipeline.process_source"):
                st = await self._process_source(src, defaults)
            for k, v in st.items():
                results[k] = results.get(k, 0) + v
        return results

    async def _process_source(
        self, src: Dict[str, Any], defaults: Dict[str, Any]
    ) -> Dict[str, int]:
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
            max_parallel = int(
                src.get("max_parallel_fetches", defaults.get("max_parallel_fetches", 5))
            )
            timeout = float(src.get("timeout", defaults.get("timeout", 15)))

            async def _fetch_and_parse(url: str) -> List[Dict[str, Any]]:
                f = await retry(lambda: self.ingester.fetch_feed(url), retries=2, timeout=timeout)
                return await self.ingester.extract_articles(f)

            # Support single or list of feeds for a source
            urls = [feed_url] if isinstance(feed_url, str) else (feed_url or [])
            results = await map_async(urls, _fetch_and_parse, limit=max_parallel)
            for raw_list in results:
                for r in raw_list:
                    items.append(self.ingester.standardize_article(r))
        elif src.get("type") == "sitemap":
            url_or_tpl = src.get("url") or src.get("url_template")
            max_parallel = int(
                src.get("max_parallel_fetches", defaults.get("max_parallel_fetches", 5))
            )
            timeout = float(src.get("timeout", defaults.get("timeout", 15)))

            urls_to_fetch = [url_or_tpl] if isinstance(url_or_tpl, str) else (url_or_tpl or [])

            async def _fetch(url: str) -> List[Dict[str, Any]]:
                xml = await asyncio.to_thread(fetch_sitemap, url)
                entries = parse_sitemap(xml)
                out: List[Dict[str, Any]] = []
                for u in entries:
                    out.append(
                        {
                            "url": u["url"],
                            "title": u.get("url"),
                            "publisher": src.get("publisher", ""),
                            "publication_date": u.get("lastmod"),
                        }
                    )
                return out

            results = await map_async(
                urls_to_fetch,
                lambda u: retry(lambda: _fetch(u), retries=2, timeout=timeout),
                limit=max_parallel,
            )
            for batch in results:
                items.extend(batch)
        else:
            log_json("WARNING", "Unsupported source type", source=source_key, type=src.get("type"))
            return st

        # De-dup by URL and incremental watermarking
        seen: set[str] = set()

        def newer_than_watermark(it: Dict[str, Any]) -> bool:
            dt_val = it.get("publication_date")
            url = it.get("url")
            d_curr = self._to_aware_utc(dt_val)
            d_last = self._to_aware_utc(last_dt)
            if d_last and d_curr:
                return d_curr > d_last
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
        Metrics.counter("pipeline.items_total").inc(st["total"])

        # Filtering and persistence
        newest_dt = self._to_aware_utc(last_dt)
        newest_url = last_url
        for it in filtered_items:
            decision, score = self.filter.filter_article(it)
            if decision is FilterDecision.KEEP:
                st["kept"] += 1
                # persist
                obj = self.article_repo.upsert(it)
                self.log_repo.add(
                    "INFO", "kept", article_url=it.get("url"), metadata=str({"score": score})
                )
                # watermark update candidate
                dt = self._to_aware_utc(obj.publication_date)
                if dt and (newest_dt is None or dt > newest_dt):
                    newest_dt = dt
                    newest_url = obj.url
                Metrics.counter("pipeline.items_kept").inc(1)
            elif decision is FilterDecision.REJECT:
                st["rejected"] += 1
                Metrics.counter("pipeline.items_rejected").inc(1)
            else:
                st["escalated"] += 1

        # Save watermark
        self.watermarks.upsert(source_key, newest_dt, newest_url)
        return st


__all__ = ["Pipeline"]
