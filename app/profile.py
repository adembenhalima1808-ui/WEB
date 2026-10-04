"""Admin "Profile Sync": publish a new CV (YAML and/or PDF) and let the AI draft the site text for review.
Nothing the AI writes goes live until the owner applies it."""
import datetime
import json
import re

from . import mistral, rag, resume, resume_build
from .config_store import load_config, save_config
from .security import clean_text
from .settings import DATA_DIR
from .storage import read_json, read_text, write_json, write_text

MAX_YAML = 200_000
# Site fields the AI may draft, with the longest text each one may hold.
DRAFT_FIELDS = {"sidebar_subtitle": 60, "role_title": 100, "location": 80, "status_text": 80, "intro_text": 600}
PROFILE_RE = re.compile(r"=== PROFILE ===\n.*?(?=\n=== |\Z)", re.S)


def yaml_preview(text):
    """Check uploaded YAML without publishing it. Raises ValueError with a readable message."""
    if len(text) > MAX_YAML:
        raise ValueError("That file is too large for a CV (200 KB max).")
    r = resume_build.parse(text)
    return {"name": r["name"], "title": r["title"],
            "counts": {"experience": len(r["professional_experience"]), "projects": len(r["independent_projects"]),
                       "education": len(r["education"]), "skill_groups": len(r["technical_expertise"]),
                       "languages": len(r["languages"])},
            "text": resume_build.build_text(r)}


def publish_yaml(text):
    preview = yaml_preview(text)
    write_text(resume.UPLOADED_YAML, text)
    resume.sync()
    return preview


def publish_pdf(raw, use_for_chat):
    (DATA_DIR / resume.CUSTOM_PDF).write_bytes(raw)
    if use_for_chat:
        from io import BytesIO
        from pypdf import PdfReader
        try:
            text = "\n".join((p.extract_text() or "") for p in PdfReader(BytesIO(raw)).pages).strip()
        except Exception:
            text = ""
        if len(text) < 200:
            raise ValueError("The PDF was saved for download, but too little text could be read from it for the "
                             "chatbot (is it a scanned image?). The chatbot keeps using the YAML.")
        write_text("resume.txt", text + "\n")
        write_json(resume.STAMP, {**read_json(resume.STAMP, {}), "chat_source": "pdf"})
        resume.clear_cache()


def reset_pdf():
    (DATA_DIR / resume.CUSTOM_PDF).unlink(missing_ok=True)


def status():
    src = resume.source_yaml()
    resume.sync()
    built = DATA_DIR / "resume.txt"
    when = datetime.datetime.fromtimestamp(built.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if built.exists() else None
    uploaded = src == DATA_DIR / resume.UPLOADED_YAML
    return {"yaml_source": "uploaded in admin" if uploaded else src.name if src.exists() else "none",
            "yaml_text": src.read_text(encoding="utf-8") if src.exists() else "",
            "chat_source": read_json(resume.STAMP, {}).get("chat_source", "yaml"),
            "custom_pdf": (DATA_DIR / resume.CUSTOM_PDF).exists(), "updated": when}


def _profile_block():
    m = PROFILE_RE.search(rag.brain_text())
    return m.group(0) if m else ""


def draft():
    """Ask the AI for new site text based on the current CV. Returns current and proposed values; saves nothing."""
    cfg = load_config()
    current = {k: cfg.get(k, "") for k in DRAFT_FIELDS}
    current["profile_block"] = _profile_block()
    prompt = (
        "You update the personal website of the person whose CV is below. Write in English, first person for "
        "intro_text, and use ONLY facts stated in the CV: never invent skills, dates, employers or numbers. "
        "Keep the tone and length of the current values.\n\n"
        f"CV:\n{resume.resume_text()}\n\n"
        f"Current values (JSON):\n{json.dumps(current, ensure_ascii=False)}\n\n"
        "Return ONLY a JSON object with these keys:\n"
        f"- sidebar_subtitle (max {DRAFT_FIELDS['sidebar_subtitle']} chars)\n"
        f"- role_title (max {DRAFT_FIELDS['role_title']} chars)\n"
        f"- location (max {DRAFT_FIELDS['location']} chars)\n"
        f"- status_text (max {DRAFT_FIELDS['status_text']} chars)\n"
        f"- intro_text (2 sentences, max {DRAFT_FIELDS['intro_text']} chars)\n"
        "- profile_block: the '=== PROFILE ===' section rewritten from the CV, same line-by-line 'Label: value' "
        "format as the current one, starting with the line '=== PROFILE ==='.")
    raw = mistral.chat([{"role": "user", "content": prompt}], model=mistral.MEDIUM, temperature=0.2, heavy=True)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
    except ValueError as e:
        raise mistral.MistralError("The AI returned something that is not JSON") from e
    proposed = {k: clean_text(data.get(k), n) for k, n in DRAFT_FIELDS.items()}
    proposed["profile_block"] = _normalize_block(data.get("profile_block"))
    return {"current": current, "proposed": proposed}


def _normalize_block(text):
    text = clean_text(text, 6000)
    text = re.sub(r"^=== PROFILE ===\s*", "", text)
    return "=== PROFILE ===\n" + text if text else ""


def apply(body):
    """Publish the drafts the owner approved (possibly edited). Only known fields are accepted."""
    cfg, changed = load_config(), []
    for k, n in DRAFT_FIELDS.items():
        if k in body:
            v = clean_text(body[k], n)
            if v:
                cfg[k] = v
                changed.append(k)
    if changed:
        save_config(cfg)
    if "profile_block" in body:
        block = _normalize_block(body["profile_block"])
        if block:
            brain = rag.brain_text()
            brain = PROFILE_RE.sub(lambda _: block.rstrip("\n") + "\n", brain, count=1) if PROFILE_RE.search(brain) else block + "\n\n" + brain
            write_text(rag.BRAIN, brain)
            rag.clear_cache()
            changed.append("profile_block")
    return changed
