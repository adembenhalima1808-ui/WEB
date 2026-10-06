"""Excel store for the hidden Derja labelling desk (/derja).

The workbook has three columns, in this order: text, intent, script. Rows are appended in place, so the
file always matches what the labelling desk shows. Every read and write runs under one lock, and saves go
through a temp file, so a crash never leaves a half-written workbook.
"""
import json
import os
import re
import threading
import unicodedata
from collections import Counter
from pathlib import Path

from openpyxl import Workbook, load_workbook

from .security import clean_text

COLUMNS = ("text", "intent", "script")
SCRIPTS = ("arabic", "arabizi", "mixed")
# Dropdown choices shown on the desk: (stored value, label for the person typing). Types typed under "Other"
# are added to the dropdown once they are in the file, so the same type is not spelled two ways.
INTENT_OPTIONS = (
    ("order_status", "Where is my order?"),
    ("delivery_delay", "My delivery is late"),
    ("cancel_order", "Cancel my order"),
    ("change_order", "Change my order (address, size, items)"),
    ("return_refund", "Return or refund"),
    ("wrong_or_damaged", "Wrong or damaged item"),
    ("payment_issue", "Payment problem"),
    ("delivery_fees", "Delivery cost or area"),
    ("product_question", "Price, stock or product details"),
    ("complaint", "General complaint"),
    ("greeting", "Greeting only"),
    ("thanks", "Thanks / goodbye"),
)
INTENT_RE = re.compile(r"^[a-z][a-z0-9_]{1,39}$")
# Arabic, Arabic Supplement and the presentation forms some phone keyboards and copied posts still produce.
ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
LATIN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")   # French accents count as Latin
# Invisible characters that ride along when text is copied from WhatsApp or Messenger: zero-width marks,
# direction marks and embeddings, byte-order mark. They are noise in training data.
INVISIBLE_RE = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2066-\u2069\uFEFF\u00AD]")
# Harakat and tatweel only change how a word looks, not which message it is.
DECORATION_RE = re.compile(r"[\u0640\u064B-\u065F\u0670]")

_lock = threading.Lock()


class LabelerError(Exception):
    """Bad input from the desk. The message is safe to show to the person typing."""


class DuplicateError(LabelerError):
    """The same message is already in the file."""


def detect_script(text):
    """Arabic letters only = arabic, Latin letters only = arabizi (Derja written with Latin letters), both = mixed."""
    has_arabic = bool(ARABIC_RE.search(text))
    has_latin = bool(LATIN_RE.search(text))
    if has_arabic and has_latin:
        return "mixed"
    return "arabic" if has_arabic else "arabizi"


def normalize_intent(raw):
    """'Order Status' -> 'order_status'. Returns None when the label cannot be a clean intent name."""
    s = re.sub(r"[\s\-]+", "_", str(raw or "").strip().lower())
    return s if INTENT_RE.match(s) else None


def clean_message(raw):
    """Text as it is stored: NFC, invisible characters removed, spaces collapsed (line breaks kept)."""
    s = unicodedata.normalize("NFC", clean_text(raw, 1000))
    s = INVISIBLE_RE.sub("", s)
    lines = (" ".join(line.split()) for line in s.split("\n"))
    return "\n".join(line for line in lines if line).strip()


def _dedupe_key(text):
    """Two messages are the same when only case, spacing, punctuation, harakat or tatweel differ."""
    s = DECORATION_RE.sub("", unicodedata.normalize("NFKC", text)).casefold()
    return " ".join(re.findall(r"\w+", s))


def _open(path):
    """Return (workbook, sheet). Creates the file with its header row when it does not exist yet."""
    path = Path(path)
    if not path.exists():
        wb = Workbook()
        ws = wb.active
        ws.title = "messages"
        ws.append(list(COLUMNS))
        _save(wb, path)
        return wb, ws
    wb = load_workbook(path)
    ws = wb.worksheets[0]
    header = tuple(str(c.value or "").strip().lower() for c in ws[1][:len(COLUMNS)])
    if header != COLUMNS:
        raise LabelerError("The Excel file's first row must be: text, intent, script")
    return wb, ws


def _save(wb, path):
    path = Path(path)
    tmp = path.with_name(path.stem + ".tmp.xlsx")
    wb.save(tmp)
    os.replace(tmp, path)


def _rows(ws):
    out = []
    for row in ws.iter_rows(min_row=2, max_col=len(COLUMNS), values_only=True):
        text, intent, script = (str(v or "").strip() for v in row)
        if text:
            out.append({"text": text, "intent": intent, "script": script})
    return out


def read_rows(path):
    with _lock:
        wb, ws = _open(path)
        return _rows(ws)


def intent_options(rows):
    """The fixed dropdown choices, then any other types already used in the file (most used first)."""
    known = {v for v, _ in INTENT_OPTIONS}
    extra = Counter(r["intent"] for r in rows if r["intent"] and r["intent"] not in known)
    opts = [{"value": v, "label": label} for v, label in INTENT_OPTIONS]
    return opts + [{"value": v, "label": v.replace("_", " ").capitalize()} for v, _ in extra.most_common()]


def summary(rows):
    """Row counts per type and per script, so the person typing can see which types still need examples."""
    return {"intents": dict(Counter(r["intent"] for r in rows).most_common()),
            "scripts": dict(Counter(r["script"] for r in rows).most_common())}


def export_bytes(path):
    """The current workbook as bytes, for download."""
    with _lock:
        _open(path)
        return Path(path).read_bytes()


def export_jsonl(path):
    """One JSON object per line ({"text", "intent", "script"}), the format most fine-tuning tools read."""
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in read_rows(path)).encode("utf-8")


def undo_last(path, text):
    """Remove the last row, but only when it is still the message the desk shows as newest."""
    with _lock:
        wb, ws = _open(path)
        last = ws.max_row
        while last > 1 and not str(ws.cell(row=last, column=1).value or "").strip():
            last -= 1
        if last < 2 or str(ws.cell(row=last, column=1).value).strip() != str(text or "").strip():
            raise LabelerError("Only the newest message can be removed. Refresh and try again.")
        ws.delete_rows(last)
        _save(wb, path)


def add_row(path, text, intent):
    """Validate one labelled message and append it. The script is always detected from the text."""
    msg = clean_message(text)
    if len(msg) < 2:
        raise LabelerError("Write the message first.")
    if not (ARABIC_RE.search(msg) or LATIN_RE.search(msg)):
        raise LabelerError("The message needs some letters in it.")

    label = normalize_intent(intent)
    if not label:
        raise LabelerError("Choose a type from the list, or pick Other and type a short name.")

    script_value = detect_script(msg)

    key = _dedupe_key(msg)
    with _lock:
        wb, ws = _open(path)
        if any(_dedupe_key(r["text"]) == key for r in _rows(ws)):
            raise DuplicateError("This message is already in the file.")
        ws.append([msg, label, script_value])
        # Force text cells to string type so a message starting with "=" is never stored as a formula.
        last = ws.max_row
        for col in range(1, len(COLUMNS) + 1):
            ws.cell(row=last, column=col).data_type = "s"
        _save(wb, path)
    return {"text": msg, "intent": label, "script": script_value}
