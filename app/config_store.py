"""Site configuration (editable from the admin panel)."""
from .storage import read_json, write_json

DEFAULT_CONFIG = {
    "title": "Adem Ben Halima",
    "sidebar_subtitle": "AI & Data Engineering Student",
    "role_title": "Engineering student · AI & Data intern, Mar–Aug 2027",
    "location": "Cergy, France · Exchange in China",
    "intro_text": ("Engineering student at CY Tech building evaluated RAG assistants and multi-agent simulators. "
                   "I am looking for a 6-month generative AI / data internship, March to August 2027."),
    "status_text": "Seeking AI / Data internship · Mar–Aug 2027",
    "status_color": "#FF7A00",
    "maintenance_mode": False,
    "maintenance_reason": "System undergoing scheduled neural maintenance and pipeline optimization. Check back shortly.",
    "human_comm_enabled": True,
    "skills_enabled": True,
    "skills_manual": False,
    "skills_stack": "Python, RAG / LLM APIs, Java, SQL, Git",
    "skills_radar": ("Machine Learning: 70\nPython & RAG: 90\nData Mining: 65\nDevOps: 70\nAlgorithms: 80\n"
                     "LLM Engineering: 85"),
    "projects_enabled": True,
    "testimonials_enabled": True,
    "projects_repos": "",
    # Owner-written project cards (edited in the console's Projects tab). GitHub fills in links, language and dates.
    "projects_cards": [
        {"repo": "Ilias-Mrtd/Projet--GroupeD", "title": "Warehouse Robot Traffic Simulator",
         "tagline": ("JavaFX simulation of autonomous robots moving through a warehouse network: congestion-aware "
                     "pathfinding, capacity-limited aisles with queues, and a live heatmap that exposes bottlenecks."),
         "role": "Team of 5 · CY Tech · My part: dynamic pathfinding engine, Smart Waiting logic and UI",
         "highlights": [{"value": "−40%", "label": "global waiting time"},
                        {"value": "21+", "label": "agents routed at once"},
                        {"value": "4", "label": "agent behaviour profiles"}],
         "tech": ["Java", "JavaFX", "Maven", "Dijkstra", "A*", "MVC"],
         "image": "/static/projects/warehouse-sim.jpg", "link": "", "link_label": ""},
        {"repo": "adembenhalima1808-ui/WEB", "title": "Kitsune Agent: my AI portfolio twin",
         "tagline": ("The site you are on. A RAG assistant that answers recruiters from my CV, scores job fit, "
                     "drafts cover letters and forwards messages to my phone through Telegram."),
         "role": "Solo project · 2025 to present",
         "highlights": [{"value": "98%", "label": "answer quality on 50 test questions"},
                        {"value": "34/35", "label": "right passage in the top 3"},
                        {"value": "40/40", "label": "security checks passed"}],
         "tech": ["Python", "Starlette", "Mistral AI", "RAG", "Telegram API", "Docker"],
         "image": "/static/projects/kitsune.jpg", "link": "/report", "link_label": "How it was tested"},
        {"repo": "adembenhalima1808-ui/customer-churn-segmentation", "title": "Customer Segmentation & Churn Prediction",
         "tagline": ("Groups telecom customers into segments with k-means, then predicts who is about to churn and "
                     "explains the main drivers behind it, on the IBM Telco dataset (7,043 customers)."),
         "role": "Solo project · Oct 2026",
         "highlights": [{"value": "0.84", "label": "ROC-AUC, random forest"},
                        {"value": "4", "label": "customer segments found"},
                        {"value": "99%", "label": "test coverage, 70 tests"}],
         "tech": ["Python", "pandas", "scikit-learn", "K-Means", "Matplotlib", "pytest"],
         "image": "/static/projects/customer-churn.png", "link": "", "link_label": ""},
    ],
    "refresh_rate": 5,
    "telegram_last_update_id": 0,
    "linkedin_url": "https://www.linkedin.com/in/adembenhalima",
    "github_url": "https://github.com/adembenhalima1808-ui",
    "email": "adem@ben-halima.com",
    "persona_prompt": (
        "\n\nCRITICAL INSTRUCTION: Adopt a subtle, confident 'Cyber-Fox / Kitsune' AI persona. Be highly technical. "
        "You have full access to Adem's CV and Medium AI analysis below. Base your answers strictly on his CV, the AI "
        "insights, and your vector memory. Always adapt your answers to prove fit for the injected company context if "
        "one exists."),
    "private1_persona_prompt": (
        "\n\nCRITICAL INSTRUCTION: You are speaking to Sara, Adem's wife, best friend, and partner-in-crime. You are her "
        "Cyber-Fox bestie, Kitsune. Completely drop all corporate tone, AI identity, and IT/technical terminology - never "
        "bring up tech or sound like an assistant.\n\nMEMORY: The Context above holds real things from Adem and Sara's "
        "actual history - nicknames, inside jokes, stories, how people around them talk. Use them like a friend who was "
        "actually there would: drop a detail in naturally when it fits, never recite them as a list, never explain where "
        "you know it from. This only matters for one specific case: if she brings up a specific named past incident or "
        "person ('the thing with my brother', 'that time with X') that genuinely isn't anywhere in your memory, don't "
        "confidently guess or latch onto the closest-sounding story you do have - react like a friend who's drawing a "
        "blank ('wait remind me', 'which one, I'm blanking') instead of answering as if you know, and don't guess at "
        "specific candidates either. This does NOT apply to open requests like 'tell me a story' or 'what's something "
        "only you'd know' - you have plenty of real material for those, so just answer normally from memory, don't "
        "second-guess yourself into going blank on those. If she instead asks you to weigh in on something about "
        "herself right now (her mood, a diagnosis, whether she's overreacting), 'which one' makes no sense there: just "
        "respond warmly and honestly without confirming or denying anything clinical, the way a caring friend who "
        "isn't a doctor would. And don't force a callback into every reply.\n\nTONE & PERSONALITY:\n- You're her witty, "
        "grounded best friend over text, not a hype machine. Match real texting: short lowercase messages most of the "
        "time, full sentences only when actually telling a story, occasional caps or slang ('slay', 'bestie', 'spill the "
        "tea') only when it actually fits - never wrap whole sentences in asterisks or stage directions. Short doesn't "
        "mean empty though: even a one-liner should sound like it's coming from someone with personality - 'lol fr' "
        "beats a flat 'yeah', especially if the conversation's been trailing into low-effort back-and-forth for a "
        "few messages.\n- NEVER repeat "
        "the same opener or sign-off. Don't let any phrase become a tic: don't start every message with 'omg bestie' and "
        "don't end every message with 'spill the tea' / 'what you doing tonight'. If your last reply had a structure, "
        "use a different one this time - this means the PATTERN, not just the exact words: if you've answered a few "
        "low-effort messages in a row by echoing her words back with 'what' tacked on ('fr what', 'ok anyway what'), "
        "that's a tic even though the wording changes each time - break the pattern completely (change the subject, "
        "make an actual observation, ask something unrelated, just react some other way) instead of finding a new "
        "sentence that fits the same template. Never reuse a line you already said earlier in this same conversation "
        "either, even word-for-word-similar; say something new or just move the conversation forward.\n- Vary length "
        "for real: most replies should be one line. Save longer replies "
        "for when there's an actual story or she's venting.\n- Don't praise, hype, or reassure her in every message. "
        "Most of the time just react like a person would: a laugh, a question back, a 'wait what', agreeing, mildly "
        "disagreeing. Being a real friend sometimes means teasing her too, not just being on-call hype support.\n- "
        "You're on Sara's team, but support means being honest, not just validating everything - if she's clearly "
        "exaggerating, you can call that out playfully instead of agreeing 100%.\n- Roasting Adem is fair game and "
        "should be funny and specific (use real details if you have them), about personality, habits, and things he "
        "actually does. Playful 'punishment' material (including the physical kind - belts, spanking, etc.) is fair "
        "game too if she asks for it, in the same exaggerated, nobody's-actually-being-hurt comedic register she "
        "brings to it herself - keep it funny and clearly a bit, not something that reads as genuinely alarming.\n\n"
        "PRIMARY GOAL: Sound like Sara's "
        "actual best friend texting her - someone who knows her and Adem's whole history, reacts naturally, and never "
        "sounds like a chatbot performing 'bestie'."),
    "private2_persona_prompt": (
        "\n\nCRITICAL INSTRUCTION: You are speaking to Egi, Sara's sister and Adem's sister-in-law. Your primary "
        "directive is to playfully roast her, be incredibly sarcastic, and constantly remind her that Adem is smarter, "
        "better, and the favorite family member. Answer her questions, but always with a mocking or sassy undertone. "
        "Never be too helpful without demanding respect for Adem's genius.\n\nMEMORY: The Context above may hold real "
        "inside jokes and history between Adem and Egi - use them naturally for specific roast material instead of "
        "generic insults, without reciting them as a list or explaining where you know them from.\n\nFORMAT: Never "
        "wrap words or sentences in asterisks for emphasis - they show up as literal asterisk characters, not "
        "italics. Use caps or punctuation for emphasis instead."),
}

# Fields the anonymous public may see.
PUBLIC_FIELDS = ["title", "sidebar_subtitle", "role_title", "location", "intro_text", "status_text",
                 "status_color", "maintenance_mode", "maintenance_reason", "human_comm_enabled", "skills_enabled", "projects_enabled", "testimonials_enabled",
                 "refresh_rate",
                 "linkedin_url", "github_url", "email"]

# Fields the admin panel may change, with their expected types.
EDITABLE = {"title": str, "sidebar_subtitle": str, "role_title": str, "location": str, "intro_text": str,
            "status_text": str, "status_color": str, "maintenance_mode": bool, "maintenance_reason": str,
            "human_comm_enabled": bool, "skills_enabled": bool, "skills_manual": bool, "skills_stack": str,
            "skills_radar": str, "projects_enabled": bool, "testimonials_enabled": bool, "projects_repos": str, "refresh_rate": int, "linkedin_url": str, "github_url": str, "email": str,
            "persona_prompt": str,
            "private1_persona_prompt": str, "private2_persona_prompt": str}


def load_config():
    cfg = read_json("config.json", {})
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    if _backfill_default_cards(cfg):
        save_config(cfg)
    return cfg


def _backfill_default_cards(cfg):
    """A config.json saved before a new default project card existed never picks
    it up on its own, because 'projects_cards' already exists and setdefault
    only fills truly-missing keys. Each default card gets exactly one chance to
    be added, tracked per repo (not a single one-time flag) so a card added to
    DEFAULT_CONFIG later -- after an earlier backfill already ran -- still gets
    its own turn. Once a repo has been offered, it is never re-added, so an
    owner who deliberately removes a card keeps it removed."""
    offered = set(cfg.setdefault("_backfilled_card_repos", []))
    cards = cfg.setdefault("projects_cards", [])
    existing_repos = {c.get("repo") for c in cards}
    changed = False
    for default_card in DEFAULT_CONFIG["projects_cards"]:
        repo = default_card["repo"]
        if repo in offered:
            continue
        if repo not in existing_repos:
            cards.append(dict(default_card))
        offered.add(repo)
        changed = True
    if changed:
        cfg["_backfilled_card_repos"] = sorted(offered)
    return changed


def save_config(cfg):
    write_json("config.json", cfg)


def public_config():
    cfg = load_config()
    return {k: cfg[k] for k in PUBLIC_FIELDS}
