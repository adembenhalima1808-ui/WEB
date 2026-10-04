"""Projects section: owner-written project cards merged with live GitHub data (cached; works without a token)."""
import logging
import re
import threading
import time
from urllib.parse import urlparse

import requests

from . import settings
from .security import clean_text

log = logging.getLogger("kitsune")
TTL = 3600                                    # unauthenticated API allows 60 calls/hour, one per hour per key is plenty
RETRY = 300                                   # after a failure, try again in 5 minutes
_lock = threading.Lock()
_cache = {}                                   # API path -> (timestamp, data)
REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}")


def username(url):
    p = urlparse(url or "")
    if p.hostname not in ("github.com", "www.github.com"):
        return ""
    parts = [x for x in p.path.split("/") if x]
    return parts[0] if parts and re.fullmatch(r"[A-Za-z0-9-]{1,39}", parts[0]) else ""


def _card(x):
    home = str(x.get("homepage") or "")
    return {
        "repo": str(x.get("full_name", "")),
        "name": str(x.get("name", ""))[:100],
        "description": str(x.get("description") or "")[:240],
        "url": str(x.get("html_url", "")),
        "homepage": home if home.startswith("https://") else "",
        "language": str(x.get("language") or "")[:30],
        "stars": int(x.get("stargazers_count") or 0),
        "topics": [str(t)[:30] for t in (x.get("topics") or [])][:5],
        "pushed": str(x.get("pushed_at") or "")[:10],
    }


def _get(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kitsune-agent"}
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
    r = requests.get("https://api.github.com" + path, headers=headers, timeout=8)
    r.raise_for_status()
    return r.json()


def fetch_repos(user):
    data = _get(f"/users/{user}/repos?per_page=100&sort=pushed&type=owner")
    return [_card(x) for x in data if not (x.get("fork") or x.get("archived") or x.get("private"))]


def fetch_repo(full_name):
    x = _get(f"/repos/{full_name}")
    return None if x.get("private") else _card(x)


def _cached(key, fn, empty):
    with _lock:
        hit = _cache.get(key)
    if hit and time.time() - hit[0] < TTL:
        return hit[1]
    try:
        data, stamp = fn(), time.time()
    except Exception as e:                    # GitHub down, rate-limited or repo gone: keep the last good answer
        log.warning("GitHub %s failed: %s", key, e)
        data, stamp = (hit[1] if hit else empty), time.time() - TTL + RETRY
    with _lock:
        if len(_cache) > 50:
            _cache.clear()
        _cache[key] = (stamp, data)
    return data


def repo_info(full_name):
    return _cached("repo:" + full_name.lower(), lambda: fetch_repo(full_name), None)


def clean_cards(cards):
    """Validate project cards coming from the owner console. Unknown keys are dropped."""
    out = []
    for c in (cards if isinstance(cards, list) else [])[:12]:
        if not isinstance(c, dict):
            continue
        repo = clean_text(c.get("repo"), 141).strip("/")
        if repo.startswith("https://github.com/"):
            repo = repo[len("https://github.com/"):].strip("/")
        if repo and not REPO_RE.fullmatch(repo):
            continue
        title = clean_text(c.get("title"), 80)
        if not (repo or title):
            continue
        image = clean_text(c.get("image"), 200)
        if not re.fullmatch(r"/static/[A-Za-z0-9._/-]+\.(?:jpg|jpeg|png|webp)", image) or ".." in image:
            image = ""                        # CSP only allows same-origin images
        link = clean_text(c.get("link"), 300)
        if not (link.startswith("https://") or re.fullmatch(r"/[A-Za-z0-9._/-]*", link)):
            link = ""
        highlights = []
        for h in (c.get("highlights") or [])[:3]:
            if isinstance(h, dict) and clean_text(h.get("value"), 12):
                highlights.append({"value": clean_text(h.get("value"), 12), "label": clean_text(h.get("label"), 50)})
        out.append({
            "repo": repo, "title": title,
            "tagline": clean_text(c.get("tagline"), 320),
            "role": clean_text(c.get("role"), 140),
            "highlights": highlights,
            "tech": [clean_text(t, 24) for t in (c.get("tech") or [])[:8] if clean_text(t, 24)],
            "image": image, "link": link,
            "link_label": clean_text(c.get("link_label"), 30) or "Live demo",
        })
    return out


BLANK = {"repo": "", "title": "", "tagline": "", "role": "", "highlights": [], "tech": [], "image": "", "link": "",
         "link_label": "Live demo"}


def _merge(card, gh):
    gh = gh or {}
    repo = card["repo"]
    return {
        **card,
        "title": card["title"] or gh.get("name") or repo.split("/")[-1],
        "tagline": card["tagline"] or gh.get("description", ""),
        "tech": card["tech"] or gh.get("topics", []),
        "link": card["link"] or gh.get("homepage", ""),
        "url": gh.get("url") or (f"https://github.com/{repo}" if repo else ""),
        "language": gh.get("language", ""),
        "stars": gh.get("stars", 0),
        "pushed": gh.get("pushed", ""),
    }


def projects(github_url, pick="", cards=None):
    """Owner-written cards when there are any (GitHub fills in the gaps), else the account's public repos:
    the ones named in `pick` in that order, or the 6 most recently pushed."""
    if cards:
        return [_merge(c, repo_info(c["repo"]) if c["repo"] else None) for c in cards]
    user = username(github_url)
    if not user:
        return []
    repos = _cached("user:" + user.lower(), lambda: fetch_repos(user), [])
    names = [n.strip().lower() for n in str(pick or "").replace("\n", ",").split(",") if n.strip()]
    if names:
        by_name = {r["name"].lower(): r for r in repos}
        chosen = [by_name[n] for n in names if n in by_name]
    else:
        chosen = repos[:6]
    return [_merge({**BLANK, "repo": r.get("repo", "")}, r) for r in chosen]


def clear_cache():
    with _lock:
        _cache.clear()
