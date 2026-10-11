"""Video surprises Egi drops for Sara: upload, caption, pick a reveal moment, and serve them
behind a family passphrase. A video stays a countdown card for Sara, Egi and the admin panel
until its reveal time passes, then it plays - same list, same endpoint, only the clock changes."""
import re
import secrets
import time

from .config_store import load_config, save_config
from .security import clean_text
from .settings import DATA_DIR

VIDEO_DIR = DATA_DIR / "sara_videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 40_000_000
ID_RE = re.compile(r"[0-9a-f]{24}\.(mp4|webm|mov)")
REVEAL_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")


def _ext_for(raw):
    if raw[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"
    head = raw[4:8]
    if head == b"ftyp":
        return "mov" if raw[8:12] == b"qt  " else "mp4"
    if head in (b"moov", b"free", b"wide", b"skip", b"mdat"):
        return "mov"
    return None


def save_upload(raw):
    """Validate and store an uploaded video. Returns its id (filename), or raises ValueError."""
    if len(raw) > MAX_BYTES:
        raise ValueError("Please upload a video under 40 MB.")
    ext = _ext_for(raw)
    if not ext:
        raise ValueError("Please upload an MP4, WebM or MOV video.")
    video_id = f"{secrets.token_hex(12)}.{ext}"
    (VIDEO_DIR / video_id).write_bytes(raw)
    return video_id


def video_path(video_id):
    """Safely resolve a stored video's path. None if the id is invalid or the file is gone."""
    if not isinstance(video_id, str) or not ID_RE.fullmatch(video_id):
        return None
    p = VIDEO_DIR / video_id
    return p if p.is_file() else None


def revealed(entry, now=None):
    reveal_at = entry.get("reveal_at", "")
    if not REVEAL_RE.fullmatch(reveal_at or ""):
        return True
    return (now or time.strftime("%Y-%m-%dT%H:%M")) >= reveal_at


def _sorted(items):
    """Newest upload first."""
    return sorted(items, key=lambda v: v.get("created_at", 0), reverse=True)


def clean(items):
    """Validate the video list coming from the owner console. Drops entries whose file is gone."""
    out = []
    for v in (items if isinstance(items, list) else [])[:30]:
        if not isinstance(v, dict) or not video_path(v.get("id")):
            continue
        reveal_at = clean_text(v.get("reveal_at"), 16)
        out.append({"id": v["id"], "caption": clean_text(v.get("caption"), 300),
                    "reveal_at": reveal_at if REVEAL_RE.fullmatch(reveal_at) else "",
                    "created_at": v.get("created_at") if isinstance(v.get("created_at"), (int, float)) else time.time()})
    return _sorted(out)


def current():
    cfg = load_config()
    items = cfg.get("sara_videos")
    return _sorted(items) if isinstance(items, list) else []


def current_with_status():
    """Same list, each entry stamped with whether its reveal moment has arrived yet."""
    now = time.strftime("%Y-%m-%dT%H:%M")
    return [{**v, "revealed": revealed(v, now)} for v in current()]


def save(items):
    cleaned = clean(items)
    cfg = load_config()
    cfg["sara_videos"] = cleaned
    save_config(cfg)
    keep = {v["id"] for v in cleaned}
    for f in VIDEO_DIR.glob("*"):
        if f.name not in keep:
            try:
                f.unlink()
            except OSError:
                pass
    return cleaned
