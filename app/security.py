"""Rate limiting, server-side sessions and OTPs. All state is in-memory: run ONE worker process."""
import hashlib
import hmac
import secrets
import threading
import time
from collections import defaultdict, deque

from . import settings

_lock = threading.Lock()


class RateLimiter:
    def __init__(self):
        self.hits = defaultdict(deque)

    def allow(self, key, limit, window):
        now = time.time()
        with _lock:
            q = self.hits[key]
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            if len(self.hits) > 5000:       # crude memory bound
                for k in list(self.hits)[:1000]:
                    if not self.hits[k]:
                        del self.hits[k]
            return True


limiter = RateLimiter()


def safe_equal(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return hmac.compare_digest(hashlib.sha256(a.encode()).digest(), hashlib.sha256(b.encode()).digest())


# --- authenticated sessions: random id in the signed cookie, role looked up server-side (revocable) ---
_sessions = {}   # sid -> (role, expires)


def create_session(role):
    sid = secrets.token_urlsafe(32)
    ttl = settings.ADMIN_SESSION_SECONDS if role == "admin" else settings.FAMILY_SESSION_SECONDS
    with _lock:
        _sessions[sid] = (role, time.time() + ttl)
    return sid


def session_role(sid):
    if not sid:
        return None
    with _lock:
        entry = _sessions.get(sid)
        if not entry:
            return None
        role, exp = entry
        if exp < time.time():
            _sessions.pop(sid, None)
            return None
        return role


def destroy_session(sid):
    with _lock:
        _sessions.pop(sid, None)


# --- one-time passwords for admin 2FA ---
_otps = {}   # token -> {hash, exp, tries}


def create_otp():
    code = f"{secrets.randbelow(10**6):06d}"
    token = secrets.token_urlsafe(24)
    with _lock:
        _otps[token] = {"hash": hashlib.sha256(code.encode()).hexdigest(),
                        "exp": time.time() + settings.OTP_TTL_SECONDS, "tries": 0}
        for t in [t for t, v in _otps.items() if v["exp"] < time.time()]:
            _otps.pop(t, None)
    return token, code


def check_otp(token, code):
    with _lock:
        entry = _otps.get(token or "")
        if not entry or entry["exp"] < time.time():
            _otps.pop(token or "", None)
            return False
        entry["tries"] += 1
        if entry["tries"] > settings.OTP_MAX_TRIES:
            _otps.pop(token, None)
            return False
        ok = hmac.compare_digest(entry["hash"], hashlib.sha256((code or "").strip().encode()).hexdigest())
        if ok:
            _otps.pop(token, None)
        return ok


def clean_text(s, limit):
    s = "".join(ch for ch in str(s or "") if ch == "\n" or ch >= " ")
    return s.strip()[:limit]
