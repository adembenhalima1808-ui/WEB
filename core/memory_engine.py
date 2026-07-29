import os
import json

SARA_HISTORY_FILE = "sara_history.json"

def load_sara_history():
    if not os.path.exists(SARA_HISTORY_FILE): return []
    try:
        with open(SARA_HISTORY_FILE, "r") as f: return json.load(f)
    except Exception: return []

def save_sara_history(messages):
    try:
        with open(SARA_HISTORY_FILE + ".tmp", "w") as f: json.dump(messages, f)
        os.replace(SARA_HISTORY_FILE + ".tmp", SARA_HISTORY_FILE)
    except Exception: pass