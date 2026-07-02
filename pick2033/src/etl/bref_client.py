"""Shared Basketball-Reference fetch layer for all pick2033 ETL.

Contract:
- Cache-first: raw HTML persists to data/raw/bref/{cache_key}.html forever.
  Re-parses never re-fetch; delete a cache file to force a refetch.
- Throttle applies to NETWORK fetches only (config: data.bref_throttle_seconds,
  3.5-4.0s band -- B-Ref bans aggressive scrapers, hard limit 20 req/min).
- Retry x3 with exponential backoff on 429/5xx, honoring Retry-After.
- 403 fails loudly: it means we are blocked and must stop, not retry.
- Every network fetch is recorded in data/raw/bref/manifest.json with a UTC
  timestamp so data versions are auditable.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "data" / "raw" / "bref"
MANIFEST_PATH = CACHE_DIR / "manifest.json"
BASE_URL = "https://www.basketball-reference.com"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_last_fetch_time = 0.0


class BrefBlockedError(RuntimeError):
    """Raised on HTTP 403: we are blocked; stop the run, do not retry."""


def _throttle_seconds() -> float:
    params = yaml.safe_load((PROJECT_ROOT / "config" / "model_params.yaml").read_text())
    t = float(params["data"]["bref_throttle_seconds"])
    if t < 3.5:
        raise ValueError(f"bref throttle {t}s below the 3.5s floor")
    return t


def _record_manifest(cache_key: str, url: str) -> None:
    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
    manifest[cache_key] = {
        "url": url,
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=1, sort_keys=True))


def strip_comment_tables(html: str) -> str:
    """B-Ref wraps many tables in HTML comments; expose them for parsing."""
    return html.replace("<!--", "").replace("-->", "")


def fetch(path: str, cache_key: str) -> str:
    """Return page HTML for a B-Ref path (e.g. '/leagues/NBA_2005.html'),
    from cache when available, else from the network (throttled)."""
    global _last_fetch_time
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    url = BASE_URL + path
    throttle = _throttle_seconds()
    for attempt in range(4):
        wait = throttle - (time.monotonic() - _last_fetch_time)
        if wait > 0:
            time.sleep(wait)
        resp = requests.get(url, headers=HEADERS, timeout=40)
        _last_fetch_time = time.monotonic()
        if resp.status_code == 403:
            raise BrefBlockedError(f"403 from B-Ref on {url}; stopping run")
        if resp.status_code == 200:
            resp.encoding = "utf-8"   # B-Ref serves UTF-8; requests guesses latin-1 without this
            html = resp.text
            cache_file.write_text(html, encoding="utf-8")
            _record_manifest(cache_key, url)
            return html
        if resp.status_code == 429 or resp.status_code >= 500:
            retry_after = resp.headers.get("Retry-After")
            backoff = float(retry_after) if retry_after else throttle * (2 ** (attempt + 1))
            time.sleep(backoff)
            continue
        resp.raise_for_status()
    raise RuntimeError(f"exhausted retries fetching {url}")
