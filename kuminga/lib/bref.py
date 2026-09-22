"""Basketball-Reference pages with a content-addressed cache.

Every page fetched is written once to `kuminga/data/bref/html/<key>.html` and recorded
in `kuminga/data/bref/manifest.json` with its URL, fetch time, byte count and sha256. A
cached page is never re-fetched unless `refresh=True`, so an analysis run on the cache is
reproducible and the manifest is the snapshot record. Network hits are throttled to one
every four seconds (Basketball-Reference publishes a limit of twenty a minute).

    from kuminga.lib import bref
    html = bref.fetch("/players/b/ballla01.html")          # key defaults to the path
    bref.manifest()["players_b_ballla01"]["sha256"]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(REPO, "kuminga", "data", "bref", "html")
MANIFEST = os.path.join(REPO, "kuminga", "data", "bref", "manifest.json")
BASE = "https://www.basketball-reference.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0 Safari/537.36")
THROTTLE = 4.0
_last = [0.0]


class BrefError(RuntimeError):
    pass


def key_of(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", path.strip("/").replace(".html", "")).strip("_")


def manifest() -> dict:
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _record(key, url, html):
    m = manifest()
    m[key] = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "bytes": len(html.encode("utf-8")),
              "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest()}
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=1, sort_keys=True)


def fetch(path: str, key: str | None = None, refresh: bool = False) -> str:
    key = key or key_of(path)
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, key + ".html")
    if os.path.exists(f) and not refresh:
        with open(f, encoding="utf-8") as fh:
            return fh.read()
    url = BASE + path
    for attempt in range(4):
        wait = THROTTLE - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            _last[0] = time.time()
            if "<title>" not in html:
                raise BrefError("no title in %s" % url)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(html)
            _record(key, url, html)
            return html
        except urllib.error.HTTPError as e:
            _last[0] = time.time()
            if e.code == 429:
                time.sleep(30 * (attempt + 1))
                continue
            raise BrefError("%s -> HTTP %d" % (url, e.code))
    raise BrefError("%s: rate limited four times" % url)


def strip_comments(html: str) -> str:
    """Basketball-Reference wraps some tables in HTML comments; expose them to a parser."""
    return html.replace("<!--", "").replace("-->", "")
