"""Tiny atomic JSON storage (same files the Streamlit version used, but in DATA_DIR)."""
import json
import os
import threading
from .settings import DATA_DIR

_lock = threading.RLock()

DEFAULT_ANALYTICS = {"total_visits": 0, "companies_logged": [], "messages_sent": 0,
                     "cover_letters_generated": 0, "cv_downloads": 0}


def _path(name):
    return DATA_DIR / name


def read_json(name, default):
    with _lock:
        p = _path(name)
        if not p.exists():
            return json.loads(json.dumps(default))
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return json.loads(json.dumps(default))


def write_json(name, data):
    with _lock:
        p = _path(name)
        tmp = p.with_suffix(p.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(tmp, p)


def update_json(name, default, fn):
    """Read-modify-write under one lock."""
    with _lock:
        data = read_json(name, default)
        result = fn(data)
        write_json(name, data)
        return result


def increment_metric(metric, value=None):
    def _do(d):
        for k, v in DEFAULT_ANALYTICS.items():
            d.setdefault(k, json.loads(json.dumps(v)))
        if metric == "companies_logged":
            if value and value not in d["companies_logged"]:
                d["companies_logged"].append(value)
        else:
            d[metric] = d.get(metric, 0) + 1
    update_json("analytics.json", DEFAULT_ANALYTICS, _do)


def read_text(name, default=""):
    with _lock:
        p = _path(name)
        try:
            return p.read_text(encoding="utf-8") if p.exists() else default
        except Exception:
            return default


def write_text(name, text):
    with _lock:
        p = _path(name)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p)
