"""Sara's running collection of things Adem said, shown as a scrolling marquee on her private page."""
from .config_store import load_config
from .security import clean_text

DEFAULT_QUOTES = [
    {"text": "A soldier is never afraid of mud\nLike a sword is never afraid of blood", "date": "24/05", "time": "22:57"},
    {"text": "i don't have infinite aura, aura has infinite me", "date": "31/05", "time": "16:03"},
    {"text": "we were talking abt earthly food not heavenly food (cake)", "date": "31/05", "time": "19:52"},
    {"text": "ezebi", "date": "", "time": ""},
    {"text": "i'm the firefighter you're the pump, i use your water to fight the fire inside of you", "date": "10/06", "time": "23:28"},
    {"text": "my dick is made of protons because it only gives positive energy", "date": "11/06", "time": "22:07"},
    {"text": "funny for my own success", "date": "13/06", "time": "01:34"},
    {"text": "normal is me, normal is npc", "date": "15/06", "time": "22:03"},
    {"text": "looks before looking", "date": "16/06", "time": "01:46"},
    {"text": "fat wife, fat life", "date": "17/06", "time": "19:55"},
    {"text": "my queen never lights her own cigarettes, the sun of my life, the moon of my nights, the star of my sky, for you i would die, shit that was good", "date": "19/06", "time": "10:56"},
    {"text": "the greater the mass, the greater the ass", "date": "19/06", "time": ""},
    {"text": "i'm so autistic because you're so majestic", "date": "19/06", "time": "10:58"},
    {"text": "i know my way towards my food", "date": "22/06", "time": "01:14"},
    {"text": "being romantic is deep in my dna. it's not the only thing that's deep. or actually; write it down as: being romantic is deep in my dna. see, we both have something deep inside us now.", "date": "23/06", "time": "20:34"},
    {"text": "youre amzing, lovely, cute and lovable", "date": "23/06", "time": "20:35"},
    {"text": "you see this is the type of shit you make me do sara (what am i doing), existing", "date": "23/06", "time": "20:38"},
    {"text": "maybe god exists and he answered my prayers. maybe youre my prayers. write that shit down.", "date": "23/06", "time": "20:50"},
    {"text": "you came to paris with nothing and you left with a full heart", "date": "24/06", "time": "12:33"},
    {"text": "fight hate with love", "date": "??/05", "time": "??:??"},
    {"text": "this is the plan; its called no plan", "date": "24/06", "time": "15:18"},
    {"text": "(you came to paris with nothing and you left with a full heart), well you didnt leave now", "date": "24/06", "time": "15:27"},
    {"text": "i started smoking double because cigarettes taste like you", "date": "25/06", "time": "01:35"},
    {"text": "in the collection, youre a whole other collection", "date": "25/06", "time": "02:18"},
    {"text": "i'm very deep into enemy territory", "date": "25/06", "time": "05:13"},
    {"text": "i'll get two leashes, one for you and one for the beast", "date": "15/06", "time": "07:08"},
    {"text": "the fatter the mass, the fatter the ass", "date": "26/06", "time": "22:48"},
    {"text": "the fatter the ass, the longer the dance", "date": "27/06", "time": "20:03"},
    {"text": "i either take all or i take none", "date": "27/06", "time": "20:06"},
    {"text": "ill start driving today, you'll get there yesterday", "date": "27/06", "time": "20:11"},
    {"text": "I employ no phantom sprites nor secret arts for this; I am simply pure and unbridled fire", "date": "07/07", "time": "01:12"},
    {"text": "The grander the seat, the mightier the mass", "date": "07/07", "time": "01:14"},
    {"text": "Mine engine of delight is forged of purest protons; it yieldeth naught but positive energy", "date": "07/07", "time": "01:14"},
    {"text": "men will bark and egi will fart", "date": "16/07", "time": "13:22"},
    {"text": "you know what they say- if you're slick with your dick you're slick with your words", "date": "16/07", "time": "17:56"},
    {"text": "why be a knight when you can be a ninja", "date": "17/07", "time": "02:40"},
    {"text": "the better the dance the higher the fence", "date": "03/10", "time": "09:49"},
]


def clean(items):
    """Validate the quote list coming from the owner console."""
    out = []
    for q in (items if isinstance(items, list) else [])[:200]:
        if not isinstance(q, dict):
            continue
        text = clean_text(q.get("text"), 500)
        if not text:
            continue
        out.append({"text": text, "date": clean_text(q.get("date"), 10), "time": clean_text(q.get("time"), 10)})
    return out


def current():
    cfg = load_config()
    items = cfg.get("sara_quotes")
    return items if isinstance(items, list) else DEFAULT_QUOTES
