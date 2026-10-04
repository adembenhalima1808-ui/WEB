"""Environment-driven settings. Nothing secret is ever hard-coded here."""
import os
import secrets
import logging
from pathlib import Path

log = logging.getLogger("kitsune")

ROOT = Path(__file__).resolve().parent.parent


def _load_env_file(path):
    """Read KEY=VALUE lines from a .env file. Values in .env override inherited environment variables."""
    if not path or not Path(path).is_file():
        return
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        if key and value.strip():
            os.environ[key] = value.strip()


_load_env_file(os.getenv("ENV_FILE", ROOT / ".env"))

DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
FRONTEND_DIR = ROOT / "frontend"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip().strip('"').strip("'")


SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(48)
    log.warning("SECRET_KEY not set: using a random one (sessions reset on every restart).")

ADMIN_PASSWORD = env("ADMIN_PASSWORD")      # required to enable admin login
SARA_PASSPHRASE = env("SARA_PASSPHRASE")    # unset = Sara's area disabled
EGI_PASSPHRASE = env("EGI_PASSPHRASE")      # unset = Egi's area disabled

# Words typed into the public company box that open a private door (the door still needs a secret).
SARA_TRIGGER = env("SARA_TRIGGER", "wife").lower()
EGI_TRIGGER = env("EGI_TRIGGER", "egi").lower()
ADMIN_TRIGGER = env("ADMIN_TRIGGER", "sudo override").lower()

MISTRAL_API_KEY = env("MISTRAL_API_KEY")
MISTRAL_MEDIUM_KEY = env("MISTRAL_MEDIUM_KEY") or MISTRAL_API_KEY

TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN.lower().startswith("bot"):
    TELEGRAM_TOKEN = TELEGRAM_TOKEN[3:]
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK = env("DISCORD_WEBHOOK")
GITHUB_TOKEN = env("GITHUB_TOKEN")          # optional: only raises the GitHub API rate limit

COOKIE_SECURE = env("COOKIE_SECURE", "1") not in ("0", "false", "False")
TRUST_PROXY = env("TRUST_PROXY", "0") in ("1", "true", "True")
# Dev helper: print the admin OTP to the server log when Telegram is not configured.
DEV_PRINT_OTP = env("DEV_PRINT_OTP", "0") in ("1", "true", "True")

ADMIN_SESSION_SECONDS = 8 * 3600
FAMILY_SESSION_SECONDS = 24 * 3600
OTP_TTL_SECONDS = 300
OTP_MAX_TRIES = 5

MISTRAL_BASE = env("MISTRAL_BASE", "https://api.mistral.ai/v1")

# The CV source. Edit it and the site rebuilds resume.txt + resume.pdf on the next request.
# Order: RESUME_YAML if set, else the YAML uploaded from the admin panel (DATA_DIR/resume.yaml), else tools/resume.yaml.
RESUME_YAML = Path(env("RESUME_YAML")).expanduser() if env("RESUME_YAML") else None
DEFAULT_RESUME_YAML = ROOT / "tools" / "resume.yaml"
