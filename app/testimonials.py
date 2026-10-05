"""Recommendations: shown as cards on the public page and quoted word for word by the chatbot."""
import re

from .config_store import load_config
from .security import clean_text

LINKEDIN_RECS = "https://www.linkedin.com/in/adembenhalima/details/recommendations/"

DEFAULT_TESTIMONIALS = [
    {"name": "Sabrine Loussaief", "title": "Manager, GoMyCode Sousse",
     "relation": "Managed Adem directly as a Game Development Instructor",
     "date": "September 2026",
     "highlight": "I am confident that Adem would be a valuable addition to a professional team.",
     "text": ("I have had the opportunity to work with Adem at GoMyCode, where he has demonstrated strong technical "
              "skills, a genuine interest in computer science, and a strong willingness to learn and grow.\n\n"
              "During his experience as a Game Development Instructor, Adem developed solid skills in programming, "
              "problem-solving, and technical communication. He is able to explain technical concepts clearly, work "
              "effectively with others, and adapt to different situations and challenges.\n\n"
              "Beyond his technical abilities, Adem is a serious, motivated, collaborative, and professional "
              "individual. He demonstrates curiosity, adaptability, and a continuous desire to improve his knowledge "
              "and explore new technologies.\n\n"
              "I am confident that Adem would be a valuable addition to a professional team and that an internship in "
              "Computer Science, Software Development, or a related field would provide him with an excellent "
              "opportunity to further develop his technical and professional skills."),
     "letter": True, "linkedin_url": LINKEDIN_RECS},
    {"name": "Rim Hamdi", "title": "Manager, team leadership and operations",
     "relation": "Managed Adem directly",
     "date": "September 2026",
     "highlight": ("I really appreciated his professionalism, discipline, and commitment to delivering quality work "
                   "on time."),
     "text": ("I had the pleasure of working with Adem and I really appreciated his professionalism, discipline, and "
              "commitment to delivering quality work on time.\n\n"
              "He is highly competent in what he does and communicates clearly and respectfully with all members.\n\n"
              "I highly recommend him to anyone looking for a skilled, responsible and professional web developer."),
     "letter": False, "linkedin_url": LINKEDIN_RECS},
]


def clean(items):
    """Validate testimonials coming from the owner console. Unknown keys are dropped."""
    out = []
    for t in (items if isinstance(items, list) else [])[:8]:
        if not isinstance(t, dict):
            continue
        name, text = clean_text(t.get("name"), 80), clean_text(t.get("text"), 3000)
        if not (name and text):
            continue
        url = clean_text(t.get("linkedin_url"), 300)
        if not re.fullmatch(r"https://(?:www\.)?linkedin\.com/[A-Za-z0-9._~%/?=&-]*", url):
            url = ""
        out.append({
            "name": name, "title": clean_text(t.get("title"), 120), "relation": clean_text(t.get("relation"), 140),
            "date": clean_text(t.get("date"), 40), "highlight": clean_text(t.get("highlight"), 300), "text": text,
            "letter": bool(t.get("letter")), "linkedin_url": url,
        })
    return out


def current():
    cfg = load_config()
    return cfg["testimonials"] if isinstance(cfg.get("testimonials"), list) else DEFAULT_TESTIMONIALS


def for_prompt():
    """Word-for-word recommendations for the chatbot, so it quotes people instead of paraphrasing them."""
    items = current()
    if not items:
        return ""
    lines = ["=== RECOMMENDATIONS ===\nWhen relevant, quote the one or two most relevant sentences word for word, with the person's name "
             "and role, never paraphrased into stronger claims. Do not paste whole recommendations: the full texts are "
             "on this page under 'What people say'."]
    for t in items:
        src = " and ".join(s for s in (["signed recommendation letter"] if t.get("letter") else []) +
                           (["LinkedIn recommendation"] if t.get("linkedin_url") else []))
        lines.append(f"{t['name']} ({t['title']}; {t['relation']}; {src or 'recommendation'}, {t['date']}):\n"
                     f"\"{t['text']}\"")
    return "\n\n".join(lines)
