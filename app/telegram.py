"""Alerts and reply sync (Telegram + optional Discord)."""
import datetime
import re
import time
import requests

from . import settings
from .config_store import load_config, save_config
from .storage import update_json

LIVE = "live_chat.json"
_last_sync = {"t": 0.0}


def send_alert(message):
    """Best-effort delivery. Returns True if Telegram accepted the message."""
    if settings.DISCORD_WEBHOOK:
        try:
            requests.post(settings.DISCORD_WEBHOOK, json={"content": f"KITSUNE PAGER: {message}"[:1900]}, timeout=3)
        except requests.RequestException:
            pass
    if not (settings.TELEGRAM_TOKEN and settings.TELEGRAM_CHAT_ID):
        return False
    safe = message.replace("**", "").replace("*", "")
    try:
        r = requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage", timeout=6,
                          json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": f"KITSUNE PAGER:\n{safe}"[:4000]})
        return bool(r.json().get("ok"))
    except (requests.RequestException, ValueError):
        return False


def clear_webhooks():
    if not settings.TELEGRAM_TOKEN:
        return False
    try:
        r = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/deleteWebhook"
                         "?drop_pending_updates=true", timeout=6)
        return bool(r.json().get("ok"))
    except (requests.RequestException, ValueError):
        return False


_TAG = re.compile(r"\[#([a-f0-9]{6,12})\]")


def sync_replies(min_interval=3.0):
    """Pull Telegram replies; route them to the visitor whose [#id] tag is in the quoted message."""
    if not (settings.TELEGRAM_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    now = time.time()
    if now - _last_sync["t"] < min_interval:
        return
    _last_sync["t"] = now
    cfg = load_config()
    last = int(cfg.get("telegram_last_update_id", 0))
    try:
        res = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/getUpdates"
                           f"?offset={last + 1}&timeout=0", timeout=4).json()
    except (requests.RequestException, ValueError):
        return
    if not (res.get("ok") and res.get("result")):
        return
    replies = []
    for item in res["result"]:
        last = max(last, item["update_id"])
        msg = item.get("message", {})
        if str(msg.get("chat", {}).get("id")) != str(settings.TELEGRAM_CHAT_ID):
            continue
        text = msg.get("text", "")
        quoted = msg.get("reply_to_message", {}).get("text", "")
        m = _TAG.search(quoted)
        if text and not text.startswith("/") and m:
            replies.append((m.group(1), text))
    if replies:
        def _do(d):
            for vid_prefix, text in replies:
                for vid, room in d.items():
                    if vid.startswith(vid_prefix):
                        room["messages"].append({"role": "assistant", "who": "Adem", "content": text[:2000],
                                                 "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                                                 "unix_time": time.time()})
        update_json(LIVE, {}, _do)
    cfg["telegram_last_update_id"] = last
    save_config(cfg)
