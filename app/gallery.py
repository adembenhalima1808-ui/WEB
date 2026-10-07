"""Sara's private photo timeline: upload, caption and serve pictures behind her passphrase."""
import re
import secrets

from .config_store import load_config, save_config
from .security import clean_text
from .settings import DATA_DIR

PHOTO_DIR = DATA_DIR / "sara_photos"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 8_000_000
ID_RE = re.compile(r"[0-9a-f]{24}\.(jpg|png|webp)")


def _ext_for(raw):
    if raw.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    return None


def save_upload(raw):
    """Validate and store an uploaded photo. Returns its id (filename), or raises ValueError."""
    if len(raw) > MAX_BYTES:
        raise ValueError("Please upload an image under 8 MB.")
    ext = _ext_for(raw)
    if not ext:
        raise ValueError("Please upload a JPEG, PNG or WebP image.")
    photo_id = f"{secrets.token_hex(12)}.{ext}"
    (PHOTO_DIR / photo_id).write_bytes(raw)
    return photo_id


def photo_path(photo_id):
    """Safely resolve a stored photo's path. None if the id is invalid or the file is gone."""
    if not isinstance(photo_id, str) or not ID_RE.fullmatch(photo_id):
        return None
    p = PHOTO_DIR / photo_id
    return p if p.is_file() else None


def clean(items):
    """Validate the photo list coming from the owner console. Drops entries whose file is gone."""
    out = []
    for p in (items if isinstance(items, list) else [])[:60]:
        if not isinstance(p, dict) or not photo_path(p.get("id")):
            continue
        out.append({"id": p["id"], "caption": clean_text(p.get("caption"), 400),
                    "date": clean_text(p.get("date"), 40)})
    return out


def current():
    cfg = load_config()
    items = cfg.get("sara_photos")
    return items if isinstance(items, list) else []


def save(items):
    cleaned = clean(items)
    cfg = load_config()
    cfg["sara_photos"] = cleaned
    save_config(cfg)
    keep = {p["id"] for p in cleaned}
    for f in PHOTO_DIR.glob("*"):
        if f.name not in keep:
            try:
                f.unlink()
            except OSError:
                pass
    return cleaned
