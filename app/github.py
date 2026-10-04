"""Public GitHub repos for the Projects section (cached; works without a token)."""
import logging
import re
import threading
import time
from urllib.parse import urlparse

import requests

from . import settings

log = logging.getLogger("kitsune")
TTL = 3600                                    # unauthenticated API allows 60 calls/hour, one per hour is plenty
RETRY = 300                                   # after a failure, try again in 5 minutes
_lock = threading.Lock()
_cache = {"user": None, "t": 0.0, "repos": []}


def username(url):
    p = urlparse(url or "")
    if p.hostname not in ("github.com", "www.github.com"):
        return ""
    parts = [x for x in p.path.split("/") if x]
    return parts[0] if parts and re.fullmatch(r"[A-Za-z0-9-]{1,39}", parts[0]) else ""


def _card(x):
    home = str(x.get("homepage") or "")
    return {
        "name": str(x.get("name", ""))[:100],
        "description": str(x.get("description") or "")[:240],
        "url": str(x.get("html_url", "")),
        "homepage": home if home.startswith("https://") else "",
        "language": str(x.get("language") or "")[:30],
        "stars": int(x.get("stargazers_count") or 0),
        "topics": [str(t)[:30] for t in (x.get("topics") or [])][:5],
        "pushed": str(x.get("pushed_at") or "")[:10],
    }


def fetch_repos(user):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kitsune-agent"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    r = requests.get(f"https://api.github.com/users/{user}/repos", headers=headers, timeout=8,
                     params={"per_page": 100, "sort": "pushed", "type": "owner"})
    r.raise_for_status()
    return [_card(x) for x in r.json() if not (x.get("fork") or x.get("archived") or x.get("private"))]


def projects(github_url, pick=""):
    """Repos to show: the names listed in `pick` (in that order), else the 6 most recently pushed."""
    user = username(github_url)
    if not user:
        return []
    with _lock:
        fresh = _cache["user"] == user and time.time() - _cache["t"] < TTL
        repos = _cache["repos"] if _cache["user"] == user else []
    if not fresh:
        try:
            repos = fetch_repos(user)
            stamp = time.time()
        except Exception as e:                # GitHub down or rate-limited: keep serving the last good list
            log.warning("GitHub repos for %s failed: %s", user, e)
            stamp = time.time() - TTL + RETRY
        with _lock:
            _cache.update(user=user, t=stamp, repos=repos)
    names = [n.strip().lower() for n in str(pick or "").replace("\n", ",").split(",") if n.strip()]
    if names:
        by_name = {r["name"].lower(): r for r in repos}
        return [by_name[n] for n in names if n in by_name]
    return repos[:6]


def clear_cache():
    with _lock:
        _cache.update(user=None, t=0.0, repos=[])
