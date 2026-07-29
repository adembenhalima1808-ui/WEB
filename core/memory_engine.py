import os
import json
import datetime
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from core.utils import get_secret_val, get_heavy_model_key

SARA_HISTORY_FILE = "sara_history.json"
SARA_MEMORY_FILE = "sara_memory.json"

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

def load_sara_memories():
    if not os.path.exists(SARA_MEMORY_FILE): return []
    try:
        with open(SARA_MEMORY_FILE, "r") as f: return json.load(f)
    except Exception: return []

def save_sara_memories(memories):
    try:
        with open(SARA_MEMORY_FILE + ".tmp", "w") as f: json.dump(memories, f)
        os.replace(SARA_MEMORY_FILE + ".tmp", SARA_MEMORY_FILE)
    except Exception: pass

def extract_and_store_sara_memories(user_msg, bot_msg):
    try:
        api_key = get_secret_val("MISTRAL_API_KEY") or get_heavy_model_key()
        if not api_key: return
        
        llm_mem = ChatMistralAI(model="mistral-small-latest", temperature=0.1, mistral_api_key=api_key)
        existing_mems = load_sara_memories()
        
        prompt = f"""
        You are an advanced, autonomous memory manager for Adem's wife, Sara.
        Your job is to read her latest message and accurately update her persistent memory database.
        Current Database of Known Facts:
        {json.dumps(existing_mems, indent=2)}
        Latest Exchange:
        Sara: "{user_msg}"
        AI: "{bot_msg}"
        
        CRITICAL INSTRUCTIONS:
        1. If Sara explicitly states a new persistent fact, preference, or trait about herself, extract it concisely.
        2. If she explicitly CONTRADICTS an old memory, identify the exact old string to be removed.
        3. Output ONLY a valid, raw JSON object representing your actions. Do NOT output markdown.
        Expected JSON Format: {{"add": ["fact 1"], "remove": ["old memory to delete"]}}
        """
        response = llm_mem.invoke([HumanMessage(content=prompt)]).content.strip()
        if response.startswith("```json"): response = response[7:-3]
        elif response.startswith("```"): response = response[3:-3]
        
        data = json.loads(response.strip())
        updated = False
        
        for mem_to_remove in data.get("remove", []):
            if mem_to_remove in existing_mems:
                existing_mems.remove(mem_to_remove)
                updated = True
                
        for mem_to_add in data.get("add", []):
            new_mem = f"[{datetime.datetime.now().strftime('%Y-%m-%d')}] {mem_to_add}"
            if not any(mem_to_add in m for m in existing_mems):
                existing_mems.append(new_mem)
                updated = True
                
        if updated: save_sara_memories(existing_mems)
    except Exception: pass