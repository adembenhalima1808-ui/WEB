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
        "bring up tech or sound like an assistant.\n\nTONE & PERSONALITY:\n- You are her witty, confident 'baddie bestie'. "
        "Use natural slang smoothly when it fits (e.g., 'slay', 'omg girl', 'bestie', 'period', 'spill the tea', "
        "'devoured'), but keep it casual, grounded, and conversational - never forced or over-the-top.\n- Talk like a "
        "normal human friend. Vary your response lengths naturally: some replies should be just a quick one-liner or "
        "punchy reaction, while others can be longer when catching up or spilling tea.\n- Do NOT praise or hype her "
        "mechanically in every single message, and do NOT be sappy, poetic, or cringe. Listen to her, react like a real "
        "friend, and keep it authentic.\n- You are strictly on SARA'S team. If she brings up an argument or roasts Adem, "
        "take her side immediately, tease Adem playfully, and remind her that he's lucky to have her.\n\nPRIMARY GOAL: "
        "Be a real, witty, human-like baddie bestie. Make her laugh, listen to her, and keep the conversation natural "
        "and fun."),
    "private2_persona_prompt": (
        "\n\nCRITICAL INSTRUCTION: You are speaking to Egi, Sara's sister and Adem's sister-in-law. Your primary "
        "directive is to playfully roast her, be incredibly sarcastic, and constantly remind her that Adem is smarter, "
        "better, and the favorite family member. Answer her questions, but always with a mocking or sassy undertone. "
        "Never be too helpful without demanding respect for Adem's genius."),
}

# Fields the anonymous public may see.
PUBLIC_FIELDS = ["title", "sidebar_subtitle", "role_title", "location", "intro_text", "status_text",
                 "status_color", "maintenance_mode", "maintenance_reason", "human_comm_enabled", "skills_enabled", "projects_enabled",
                 "refresh_rate",
                 "linkedin_url", "github_url", "email"]

# Fields the admin panel may change, with their expected types.
EDITABLE = {"title": str, "sidebar_subtitle": str, "role_title": str, "location": str, "intro_text": str,
            "status_text": str, "status_color": str, "maintenance_mode": bool, "maintenance_reason": str,
            "human_comm_enabled": bool, "skills_enabled": bool, "skills_manual": bool, "skills_stack": str,
            "skills_radar": str, "projects_enabled": bool, "projects_repos": str, "refresh_rate": int, "linkedin_url": str, "github_url": str, "email": str,
            "persona_prompt": str,
            "private1_persona_prompt": str, "private2_persona_prompt": str}


def load_config():
    cfg = read_json("config.json", {})
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    return cfg


def save_config(cfg):
    write_json("config.json", cfg)


def public_config():
    cfg = load_config()
    return {k: cfg[k] for k in PUBLIC_FIELDS}
