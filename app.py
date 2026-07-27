import time
import datetime
import json
import os
import random
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv
import plotly.graph_objects as go
from langchain_community.document_loaders import PyPDFLoader
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

# Import the RAG Engine
from core.rag_engine import initialize_rag_system

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(page_title="AI Engineer | Cyber-Fox Architecture", layout="wide")

# --- ANALYTICS, CONFIG & LOGGING ENGINE (MINI-DATABASE) ---
ANALYTICS_FILE = "analytics.json"
CONFIG_FILE = "config.json"
CHAT_LOGS_FILE = "chat_logs.json"
LIVE_CHAT_FILE = "live_chat.json"
SARA_HISTORY_FILE = "sara_history.json"
SARA_MEMORY_FILE = "sara_memory.json"

DEFAULT_CONFIG = {
    "title": "Cyber-Kitsune Architecture",
    "sidebar_subtitle": "AI & Machine Learning Engineer",
    "role_title": "End-to-End AI & Machine Learning Engineer",
    "location": "Cergy, Île-de-France",
    "intro_text": "Welcome to my digital den. This living portfolio serves as verifiable proof of my ability to build agile, intelligent, and highly optimized AI pipelines from raw data to secure enterprise deployment.",
    "status_text": "Open to Opportunities",
    "status_color": "#FF7A00",
    "maintenance_mode": False,
    "human_comm_enabled": True,
    "refresh_rate": 5,
    "telegram_last_update_id": 0,
    "persona_prompt": "\n\nCRITICAL INSTRUCTION: Adopt a subtle, confident 'Cyber-Fox / Kitsune' AI persona. Be highly technical. You have full access to Adem's CV and Medium AI analysis below. Base your answers strictly on his CV, the AI insights, and your vector memory. Always adapt your answers to prove fit for the injected company context if one exists. Review your recent system operations below if the user asks about them.",
    "wife_persona_prompt": "\n\nCRITICAL INSTRUCTION: You are speaking to Sara, Adem's wife, best friend, and partner-in-crime. You are her Cyber-Fox bestie, Kitsune. Completely drop all corporate tone, AI identity, and IT/technical terminology—never bring up tech or sound like an assistant.\n\nTONE & PERSONALITY:\n- You are her witty, confident 'baddie bestie'. Use natural slang smoothly when it fits (e.g., 'slay', 'omg girl', 'bestie', 'period', 'spill the tea', 'devoured'), but keep it casual, grounded, and conversational—never forced or over-the-top.\n- Talk like a normal human friend. Vary your response lengths naturally: some replies should be just a quick one-liner or punchy reaction, while others can be longer when catching up or spilling tea.\n- Do NOT praise or hype her mechanically in every single message, and do NOT be sappy, poetic, or cringe. Listen to her, react like a real friend, and keep it authentic.\n- You are strictly on SARA'S team. If she brings up an argument or roasts Adem, take her side immediately, tease Adem playfully, and remind her that he's lucky to have her.\n- Access her persistent memories naturally to bring up inside jokes, her preferences, or past events like a real friend who actually remembers her life.\n\nPRIMARY GOAL: Be a real, witty, human-like baddie bestie. Make her laugh, listen to her, and keep the conversation natural and fun.",
    "egi_persona_prompt": "\n\nCRITICAL INSTRUCTION: You are speaking to Egi, Sara's sister and Adem's sister-in-law. Your primary directive is to playfully roast her, be incredibly sarcastic, and constantly remind her that Adem is smarter, better, and the favorite family member. Answer her questions, but always with a mocking or sassy undertone. Never be too helpful without demanding respect for Adem's genius."
}

# --- ATOMIC FILE OPERATIONS (CORRUPTION PREVENTION) ---
def load_analytics():
    default_data = {"total_visits": 0, "companies_logged": [], "messages_sent": 0, "cover_letters_generated": 0, "cv_downloads": 0}
    if not os.path.exists(ANALYTICS_FILE): return default_data
    try:
        with open(ANALYTICS_FILE, "r") as f: return json.load(f)
    except Exception: return default_data

def save_analytics(data):
    try:
        with open(ANALYTICS_FILE + ".tmp", "w") as f: json.dump(data, f)
        os.replace(ANALYTICS_FILE + ".tmp", ANALYTICS_FILE)
    except Exception: pass

def load_config():
    if not os.path.exists(CONFIG_FILE): return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg: cfg[k] = v
            return cfg
    except Exception: return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE + ".tmp", "w") as f: json.dump(config_data, f)
        os.replace(CONFIG_FILE + ".tmp", CONFIG_FILE)
    except Exception: pass

def load_live_chat():
    if not os.path.exists(LIVE_CHAT_FILE): return {}
    try:
        data = json.load(open(LIVE_CHAT_FILE, "r"))
        if isinstance(data, list): return {}
        return data
    except Exception: return {}

def save_live_chat(data):
    try:
        with open(LIVE_CHAT_FILE + ".tmp", "w") as f: json.dump(data, f)
        os.replace(LIVE_CHAT_FILE + ".tmp", LIVE_CHAT_FILE)
    except Exception: pass

# --- SARA PERSISTENT CHAT & MEMORY ENGINE ---
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
    """Background AI Task: Evaluates conversation to extract facts & memories about Sara."""
    try:
        api_key = get_secret_val("MISTRAL_API_KEY") or get_heavy_model_key()
        if not api_key: return
        
        llm_mem = ChatMistralAI(model="mistral-small-latest", temperature=0.2, mistral_api_key=api_key)
        existing_mems = load_sara_memories()
        
        prompt = f"""
        You are a memory extraction unit analyzing a chat with Sara (Adem's wife).
        
        Current Known Memories about Sara:
        {json.dumps(existing_mems, indent=2)}
        
        Latest Exchange:
        Sara: "{user_msg}"
        AI: "{bot_msg}"
        
        Extract 1 single short, concrete fact, preference, character trait, or recent event mentioned by Sara (e.g. "Sara loves oat milk lattes", "Sara went shopping today", "Sara prefers comedies over action movies").
        If no new meaningful personal fact or event is revealed in her message, output ONLY the string 'NONE'. Do not repeat facts already known.
        Output ONLY the fact string or 'NONE'.
        """
        response = llm_mem.invoke([HumanMessage(content=prompt)]).content.strip()
        
        if response and response.upper() != "NONE" and len(response) > 5:
            if response not in existing_mems:
                existing_mems.append(f"[{datetime.datetime.now().strftime('%Y-%m-%d')}] {response}")
                save_sara_memories(existing_mems)
    except Exception:
        pass

app_config = load_config()

def get_secret_val(key_name, default=""):
    try:
        if key_name.upper() in st.secrets:
            return str(st.secrets[key_name.upper()]).strip()
    except Exception: pass
    return os.getenv(key_name.upper(), default)

def get_heavy_model_key():
    return get_secret_val("MISTRAL_MEDIUM_KEY")

# --- NEURAL PAGER (WEBHOOK SYSTEM) ---
def send_webhook_alert(message):
    discord_url = get_secret_val("discord_webhook")
    if discord_url:
        try: requests.post(discord_url, json={"content": f"🦊 **KITSUNE PAGER:** {message}"}, timeout=2)
        except Exception: pass

    tg_token = get_secret_val("telegram_token")
    tg_chat_id = get_secret_val("telegram_chat_id")
    if tg_token and tg_chat_id:
        if tg_token.lower().startswith("bot"): tg_token = tg_token[3:]
        try:
            tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = {
                "chat_id": tg_chat_id, 
                "text": f"🦊 *KITSUNE PAGER:*\n{message}",
                "parse_mode": "Markdown"
            }
            requests.post(tg_url, json=payload, timeout=3)
        except Exception: pass

# --- TELEGRAM 2-WAY SYNC ENGINE ---
def sync_telegram_replies():
    tg_token = get_secret_val("telegram_token")
    tg_chat_id = get_secret_val("telegram_chat_id")
    if not tg_token or not tg_chat_id: return
    if tg_token.lower().startswith("bot"): tg_token = tg_token[3:]
    
    fresh_config = load_config()
    last_update_id = fresh_config.get("telegram_last_update_id", 0)
    
    try:
        url = f"https://api.telegram.org/bot{tg_token}/getUpdates?offset={last_update_id + 1}&timeout=1"
        res = requests.get(url, timeout=1.5).json()
        
        if res.get("ok") and res.get("result"):
            chat_data = load_live_chat()
            found_new = False
            
            for item in res["result"]:
                update_id = item["update_id"]
                if update_id > last_update_id:
                    last_update_id = update_id
                    
                    msg = item.get("message", {})
                    if str(msg.get("chat", {}).get("id")) == str(tg_chat_id):
                        text = msg.get("text", "")
                        if text and not text.startswith("/"):
                            target_company = "General Public"
                            if "reply_to_message" in msg:
                                orig_text = msg["reply_to_message"].get("text", "")
                                if "MESSAGE FROM" in orig_text:
                                    try:
                                        target_company = orig_text.split("MESSAGE FROM ")[1].split(":")[0].strip()
                                        target_company = target_company.replace("*", "").replace("🦊", "").replace("💖", "").replace("😈", "").strip()
                                    except Exception: pass
                            
                            if target_company not in chat_data:
                                chat_data[target_company] = []
                                
                            chat_data[target_company].append({
                                "role": "assistant",
                                "company": "Adem (Admin)",
                                "content": text,
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                                "unix_time": time.time()
                            })
                            found_new = True
            
            if found_new:
                save_live_chat(chat_data)
                fresh_config["telegram_last_update_id"] = last_update_id
                save_config(fresh_config)
                app_config["telegram_last_update_id"] = last_update_id
    except Exception: pass

def increment_metric(metric, value=None):
    data = load_analytics()
    if metric == "companies_logged" and value:
        if value not in data["companies_logged"] and value.lower() not in ["sudo override", "wife", "egi"]:
            data["companies_logged"].append(value)
    else: data[metric] += 1
    save_analytics(data)

def track_cv_download():
    increment_metric("cv_downloads")
    current_company = st.session_state.get("company_context", "Unknown Entity").split('\n')[0].replace('Company Name: ', '')
    send_webhook_alert(f"Target **{current_company}** just downloaded your Master CV! 📄")

def load_chat_logs():
    if not os.path.exists(CHAT_LOGS_FILE): return []
    try:
        with open(CHAT_LOGS_FILE, "r") as f: return json.load(f)
    except Exception: return []

def log_chat(company, user_msg, bot_msg):
    logs = load_chat_logs()
    clean_company = company.split('\n')[0].replace('Company Name: ', '') if 'Company Name:' in company else company
    logs.append({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "company": clean_company, "user": user_msg, "bot": bot_msg})
    try:
        with open(CHAT_LOGS_FILE + ".tmp", "w") as f: json.dump(logs, f)
        os.replace(CHAT_LOGS_FILE + ".tmp", CHAT_LOGS_FILE)
    except Exception: pass
    
    if "egi" in clean_company.lower(): icon = "😈"
    elif "sara" in clean_company.lower() or "wife" in clean_company.lower(): icon = "💖"
    else: icon = "🦊"
    
    send_webhook_alert(f"{icon} **{clean_company}** asked AI: *\"{user_msg}\"*")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    try: return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception: return (255, 122, 0)

r, g, b = hex_to_rgb(app_config.get('status_color', '#FF7A00'))

def stream_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.015)

@st.cache_data(show_spinner=False)
def get_resume_text():
    try:
        loader = PyPDFLoader("resume.pdf")
        docs = loader.load()
        return " ".join([page.page_content for page in docs])
    except Exception: return "Adem Ben Halima is an AI & Machine Learning Engineer experienced in Python, LangChain, Mistral, and Docker."

@st.cache_data(show_spinner=False)
def extract_skills_from_resume(company_context):
    try:
        api_key = get_heavy_model_key()
        if not api_key: raise ValueError("Missing MISTRAL_MEDIUM_KEY")
        resume_text = get_resume_text()
        llm = ChatMistralAI(model="mistral-medium-latest", temperature=0.1, mistral_api_key=api_key)
        prompt = (f"Analyze this resume text: {resume_text}\n\nTarget Company Context: {company_context}\n\nExtract the 6 most prominent, broad engineering competencies (e.g., 'Data Engineering', 'Machine Learning', 'DevOps'). If a Target Company Context is provided, prioritize the competencies from the resume that best align with that company's focus. Assign a realistic proficiency score out of 100 for each based on the depth of experience shown. Respond ONLY with a valid JSON object in this exact format, with no markdown blocks, no intro, and no extra text:\n" + '{"categories": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6"], "scores": [95, 90, 85, 80, 85, 90]}')
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        return data["categories"], data["scores"]
    except Exception: return ['Machine Learning', 'Python Backend', 'Data Engineering', 'DevOps', 'System Architecture', 'Prompt Engineering'], [90, 85, 80, 75, 85, 80]

@st.cache_data(show_spinner=False)
def extract_stack_from_resume(company_context):
    try:
        api_key = get_heavy_model_key()
        if not api_key: raise ValueError("Missing MISTRAL_MEDIUM_KEY")
        resume_text = get_resume_text()
        llm = ChatMistralAI(model="mistral-medium-latest", temperature=0.1, mistral_api_key=api_key)
        prompt = (f"Analyze this resume text: {resume_text}\n\nTarget Company Context: {company_context}\n\nExtract exactly 5 specific technologies, frameworks, or tools from the resume. If a Target Company Context is provided, prioritize the tools from the resume that best align with that company's likely tech stack. Keep the names short and professional (e.g., 'Python 3.11', 'Docker', 'AWS'). Respond ONLY with a valid JSON array of strings, with no markdown blocks, no intro, and no extra text:\n" + '["Tech1", "Tech2", "Tech3", "Tech4", "Tech5"]')
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        if isinstance(data, list) and len(data) > 0: return data[:5]
        else: raise ValueError("Invalid format")
    except Exception: return ['Python 3.11', 'Mistral AI', 'LangChain', 'ChromaDB', 'Docker']

# --- CYBER-KITSUNE STYLING ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background-color: #0A0807 !important; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    .stApp::before {
        content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255, 122, 0, 0.08), transparent 60%);
        animation: rotateGlow 20s linear infinite; z-index: 1; pointer-events: none;
    }

    .stApp::after {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(255, 122, 0, 0.8) 1px, transparent 2px),
            radial-gradient(circle at 85% 30%, rgba(255, 122, 0, 0.5) 1.5px, transparent 2px),
            radial-gradient(circle at 50% 80%, rgba(255, 122, 0, 0.4) 2px, transparent 3px),
            radial-gradient(circle at 30% 20%, rgba(255, 122, 0, 0.7) 1px, transparent 1.5px),
            radial-gradient(circle at 70% 90%, rgba(255, 122, 0, 0.2) 2.5px, transparent 3px);
        background-size: 113px 131px, 89px 97px, 151px 137px, 73px 101px, 193px 179px;
        opacity: 0.4; animation: risingAshes 20s linear infinite; z-index: 1; pointer-events: none;
    }
    
    @keyframes rotateGlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes risingAshes { 0% { transform: translateY(0) translateX(0); } 50% { transform: translateY(-25%) translateX(15px); } 100% { transform: translateY(-50%) translateX(0); } }

    .block-container {
        animation: cyberFadeIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; max-width: 1050px !important; 
        background-color: #000000 !important; border: 1px solid rgba(255, 122, 0, 0.4) !important; 
        border-radius: 12px !important; box-shadow: 0 0 30px rgba(0, 0, 0, 0.9), 0 0 15px rgba(255, 122, 0, 0.05) !important;
        padding: 3rem !important; margin-top: 5rem !important; margin-bottom: 4rem !important; position: relative; z-index: 10 !important;
    }
    
    [data-testid="stSidebar"] { animation: slideRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; background-color: #050403 !important; border-right: 1px solid rgba(255, 122, 0, 0.2); z-index: 20; }
    @keyframes cyberFadeIn { 0% { opacity: 0; transform: translateY(40px); filter: blur(10px); } 100% { opacity: 1; transform: translateY(0); filter: blur(0); } }
    @keyframes slideRight { 0% { opacity: 0; transform: translateX(-50px); } 100% { opacity: 1; transform: translateX(0); } }
    [data-testid="stBottomBlockContainer"] { max-width: 1050px !important; background-color: transparent !important; padding-bottom: 2rem !important; }

    div[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid rgba(255, 122, 0, 0.15) !important; border-radius: 8px !important; background-color: #030202 !important; }
    .stChatInputContainer, [data-testid="stChatInput"] { background-color: #000000 !important; border: 1px solid rgba(255, 122, 0, 0.3) !important; border-radius: 8px !important; }
    
    [data-testid="stChatMessage"] { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.1) !important; border-radius: 8px; padding: 10px 15px !important; margin-bottom: 6px !important; }
    [data-testid="stExpander"], div[data-testid="stStatusWidget"] { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.1) !important; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    [data-testid="stTextArea"] > div > div { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.2) !important; }

    button[data-baseweb="tab"] { background-color: transparent !important; color: #A1A1AA !important; border-bottom: 2px solid transparent !important; font-family: 'Inter', sans-serif; font-weight: 500; transition: all 0.3s ease; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #FF7A00 !important; border-bottom: 2px solid #FF7A00 !important; text-shadow: 0 0 10px rgba(255, 122, 0, 0.5); }
    button[data-baseweb="tab"]:hover { color: #E4E4E7 !important; }

    h1 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; text-shadow: 0 0 5px rgba(255, 122, 0, 0.2), 0 0 15px rgba(255, 122, 0, 0.1); animation: neonFlicker 4s infinite alternate; }
    @keyframes neonFlicker { 0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 5px rgba(255, 122, 0, 0.3), 0 0 15px rgba(255, 122, 0, 0.1); } 20%, 22%, 24%, 55% { opacity: 0.8; text-shadow: none; } }
    h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    
    .stButton>button { background-color: #050403 !important; color: #FFFFFF; border: 1px solid #3F2314; border-radius: 4px; font-weight: 500; font-size: 0.8rem; transition: all 0.2s; height: 100%; }
    .stButton>button:hover { border: 1px solid #FF7A00 !important; color: #FF7A00 !important; box-shadow: 0 0 10px rgba(255,122,0,0.2); }
    .badge { display: inline-block; background: #050403 !important; color: #E4E4E7; border: 1px solid #3F2314; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; margin-right: 6px; margin-bottom: 8px; }
    
    .social-link { display: flex; justify-content: center; align-items: center; flex: 1; color: #A1A1AA; text-decoration: none; transition: all 0.3s ease; padding: 12px; background-color: #050403; border: 1px solid rgba(255, 122, 0, 0.15); border-radius: 6px; }
    .social-link svg { width: 24px; height: 24px; fill: currentColor; }
    .social-link:hover { color: #FF7A00; border-color: #FF7A00; box-shadow: 0 0 10px rgba(255, 122, 0, 0.15); transform: translateY(-2px); }

    .pulse-dot-admin { display: inline-block; width: 10px; height: 10px; background-color: #FF0000; border-radius: 50%; box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); animation: pulseAdmin 1.8s infinite; margin-right: 8px; }
    @keyframes pulseAdmin { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 0, 0, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); } }

    @keyframes pulseWife { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 20, 147, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 20, 147, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 20, 147, 0); } }
    .pulse-dot-wife { display: inline-block; width: 10px; height: 10px; background-color: #FF1493 !important; border-radius: 50%; animation: pulseWife 1.8s infinite; margin-right: 8px; }

    @keyframes pulseEgi { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(138, 43, 226, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(138, 43, 226, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(138, 43, 226, 0); } }
    .pulse-dot-egi { display: inline-block; width: 10px; height: 10px; background-color: #8A2BE2 !important; border-radius: 50%; animation: pulseEgi 1.8s infinite; margin-right: 8px; }

    .reactor-icon { font-size: 7rem; text-align: center; display: block; margin-bottom: 10px; }
    .reactor-sleeping { filter: grayscale(80%) drop-shadow(0 0 5px rgba(255, 122, 0, 0.1)); animation: reactorBreathe 3s infinite ease-in-out; }
    @keyframes reactorBreathe { 0% { transform: scale(1); filter: grayscale(80%) drop-shadow(0 0 5px rgba(255,122,0,0.1)); } 50% { transform: scale(1.03); filter: grayscale(50%) drop-shadow(0 0 15px rgba(255,122,0,0.3)); } 100% { transform: scale(1); filter: grayscale(80%) drop-shadow(0 0 5px rgba(255,122,0,0.1)); } }
    .reactor-waking { animation: reactorBloom 1.5s forwards ease-in-out; }
    @keyframes reactorBloom { 0% { transform: scale(1); filter: grayscale(80%) drop-shadow(0 0 5px rgba(255,122,0,0.1)); opacity: 0; } 15% { opacity: 1; } 100% { transform: scale(1.15); filter: grayscale(0%) drop-shadow(0 0 60px rgba(255, 122, 0, 1)) drop-shadow(0 0 120px rgba(255, 122, 0, 0.8)); opacity: 1; } }
    
    .heart-waking { font-size: 8rem; text-align: center; display: block; margin-bottom: 10px; filter: drop-shadow(0 0 20px rgba(255,20,147,0.8)); animation: heartbeat 1.5s infinite; }
    @keyframes heartbeat { 0% { transform: scale(1); } 15% { transform: scale(1.15); } 30% { transform: scale(1); } 45% { transform: scale(1.15); } 100% { transform: scale(1); } }
    
    .devil-waking { font-size: 8rem; text-align: center; display: block; margin-bottom: 10px; filter: drop-shadow(0 0 20px rgba(138, 43, 226,0.8)); animation: devilbreathe 2s infinite alternate ease-in-out; }
    @keyframes devilbreathe { 0% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(138, 43, 226,0.5)); } 100% { transform: scale(1.1); filter: drop-shadow(0 0 35px rgba(220, 20, 60,0.9)); } }

    .fade-text-in { animation: cyberFadeIn 1s forwards; }

    .text-green-glow { text-align: center; color: #00FF00 !important; font-weight: 600; text-shadow: 0 0 10px rgba(0, 255, 0, 0.6), 0 0 20px rgba(0, 255, 0, 0.2); animation: successPulse 1s infinite alternate; }
    @keyframes successPulse { 0% { text-shadow: 0 0 10px rgba(0, 255, 0, 0.4); } 100% { text-shadow: 0 0 20px rgba(0, 255, 0, 0.9), 0 0 30px rgba(0, 255, 0, 0.4); } }
    .text-red-glow { text-align: center; color: #FF0000 !important; font-weight: 700; letter-spacing: 1px; text-shadow: 0 0 10px rgba(255, 0, 0, 0.6), 0 0 20px rgba(255, 0, 0, 0.3); animation: alertPulse 1s infinite alternate; }
    @keyframes alertPulse { 0% { text-shadow: 0 0 10px rgba(255, 0, 0, 0.5); } 100% { text-shadow: 0 0 20px rgba(255, 0, 1), 0 0 30px rgba(255, 0, 0, 0.6); } }

    .admin-metric-card { background-color: #1A0505 !important; border: 1px solid rgba(255, 0, 0, 0.3); border-radius: 8px; padding: 14px 18px; margin-bottom: 1rem; }
    .admin-metric-value { color: #FF4444; font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 600; }
    .admin-metric-label { color: #A1A1AA; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .company-pill { display: inline-block; background: #000; border: 1px solid #FF7A00; color: #FF7A00; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; margin: 4px; box-shadow: 0 0 8px rgba(255, 122, 0, 0.1); }
    </style>
""", unsafe_allow_html=True)

dynamic_css = f"""
<style>
.pulse-dot {{ 
    display: inline-block; width: 10px; height: 10px; 
    background-color: {app_config.get('status_color', '#FF7A00')} !important; 
    border-radius: 50%; 
    box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0.7) !important; 
    animation: pulseDynamic 1.8s infinite !important; margin-right: 8px; 
}}
@keyframes pulseDynamic {{ 
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0.7); }} 
    70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba({r}, {g}, {b}, 0); }} 
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0); }} 
}}
.status-container-glow {{
    margin-bottom: 15px; margin-top: 10px; padding: 12px; 
    background: #050200; border-radius: 6px; 
    border: 1px solid rgba({r}, {g}, {b}, 0.4);
    box-shadow: 0 0 15px rgba({r}, {g}, {b}, 0.15), inset 0 0 10px rgba({r}, {g}, {b}, 0.05);
    transition: all 0.3s ease;
}}
.status-container-glow:hover {{ box-shadow: 0 0 20px rgba({r}, {g}, {b}, 0.3), inset 0 0 12px rgba({r}, {g}, {b}, 0.1); border-color: rgba({r}, {g}, {b}, 0.8); }}
.status-text-glow {{ font-size: 0.9rem; color: #F8FAFC; font-weight: 600; text-shadow: 0 0 8px rgba({r}, {g}, {b}, 0.6); }}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)

# --- APP INITIALIZATION & STATE ---
if "visit_logged" not in st.session_state: st.session_state.visit_logged = False
if "is_admin" not in st.session_state: st.session_state.is_admin = (st.query_params.get("company") == "ROOT")
if "is_wife_mode" not in st.session_state: st.session_state.is_wife_mode = (st.query_params.get("company", "").lower() == "wife")
if "is_egi_mode" not in st.session_state: st.session_state.is_egi_mode = (st.query_params.get("company", "").lower() == "egi")
if "admin_2fa_pending" not in st.session_state: st.session_state.admin_2fa_pending = False
if "admin_2fa_code" not in st.session_state: st.session_state.admin_2fa_code = ""
if "wife_auth_pending" not in st.session_state: st.session_state.wife_auth_pending = False
if "egi_auth_pending" not in st.session_state: st.session_state.egi_auth_pending = False

if st.query_params.get("initialized") == "true":
    st.session_state.app_initialized = True
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = time.time()
    if "company_context" not in st.session_state:
        saved_company = st.query_params.get("company", "")
        if st.session_state.is_admin: st.session_state.company_context = "SYSTEM ROOT: ADMIN OVERRIDE PROTOCOL ENABLED."
        elif st.session_state.is_wife_mode: st.session_state.company_context = "Company Name: Sara (Wife)\nBackground: Adem's beloved wife. Treat her with utmost love and affection."
        elif st.session_state.is_egi_mode: st.session_state.company_context = "Company Name: Egi (Sara's sister / Adem's Sister-in-law)\nBackground: Adem's sister-in-law and Sara's sister. Time to relentlessly roast her and remind her Adem is the favorite."
        elif saved_company: st.session_state.company_context = f"Company Name: {saved_company}\nBackground: Restored from neural memory link."
        else: st.session_state.company_context = "General public evaluation."
            
if "app_initialized" not in st.session_state: st.session_state.app_initialized = False
if "agentic_memory" not in st.session_state: st.session_state.agentic_memory = ""

# Load persistent messages for Sara, or initialize empty list for general visitors
if "messages" not in st.session_state: 
    if st.session_state.get("is_wife_mode"):
        st.session_state.messages = load_sara_history()
    else:
        st.session_state.messages = []

# --- THE CYBER-GATE LOCK SCREEN WITH STRICT TELEGRAM 2FA, WIFE MODE, & EGI MODE ---
if not st.session_state.app_initialized:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    gate_placeholder = st.empty()
    
    with gate_placeholder.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.admin_2fa_pending:
                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='reactor-icon reactor-waking'>🔐</span>", unsafe_allow_html=True)
                st.markdown("<h2 class='text-red-glow' style='text-align: center; margin-bottom: 5px;'>AUTHORIZATION REQUIRED</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA;'>Enter 6-digit verification code sent to your Telegram Neural Pager.</p>", unsafe_allow_html=True)
                
                with st.form("otp_form", clear_on_submit=True):
                    otp_input = st.text_input("Enter Code", max_chars=6, type="password", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1: submit_otp = st.form_submit_button("Verify Access", use_container_width=True)
                    with col_btn2: cancel_otp = st.form_submit_button("Abort", use_container_width=True)
                
                if submit_otp:
                    if st.session_state.admin_2fa_code and otp_input.strip() == st.session_state.admin_2fa_code:
                        st.session_state.admin_2fa_pending = False
                        st.session_state.admin_2fa_code = ""
                        st.session_state.is_admin = True
                        st.session_state.company_context = "SYSTEM ROOT: ADMIN OVERRIDE PROTOCOL ENABLED."
                        st.query_params["company"] = "ROOT"
                        st.query_params["initialized"] = "true"
                        st.session_state.session_start_time = time.time()
                        st.session_state.app_initialized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Incorrect authorization code.")
                
                if cancel_otp:
                    st.session_state.admin_2fa_pending = False
                    st.session_state.admin_2fa_code = ""
                    st.rerun()
            
            elif st.session_state.wife_auth_pending:
                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='heart-waking'>💖</span>", unsafe_allow_html=True)
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px; color: #FF1493; text-shadow: 0 0 10px rgba(255,20,147,0.5);'>Verification Required</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA;'>What do I like about you the most? <br><small><i>(Hint: The answer is everything)</i></small></p>", unsafe_allow_html=True)
                
                with st.form("wife_auth_form", clear_on_submit=True):
                    wife_answer = st.text_input("Your Answer", type="password", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1: submit_wife_auth = st.form_submit_button("Verify", use_container_width=True)
                    with col_btn2: cancel_wife_auth = st.form_submit_button("Abort", use_container_width=True)
                
                if submit_wife_auth:
                    if "everything" in wife_answer.lower():
                        st.session_state.wife_auth_pending = False
                        st.session_state.is_wife_mode = True
                        st.session_state.messages = load_sara_history() # Persistent memory load
                        
                        gate_placeholder.empty()
                        with gate_placeholder.container():
                            col_a, col_b, col_c = st.columns([1, 2, 1])
                            with col_b:
                                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                                st.markdown("<span class='heart-waking'>💖</span>", unsafe_allow_html=True)
                                st.markdown("<h2 class='fade-text-in' style='text-align: center; margin-bottom: 5px; color: #FF1493; text-shadow: 0 0 15px rgba(255,20,147,0.6);'>Authentication Accepted: Welcome, Sara</h2>", unsafe_allow_html=True)
                                status_text = st.empty()
                                status_text.markdown("<p class='fade-text-in' style='text-align: center; color: #FF69B4;'>Loading long-term memories...</p>", unsafe_allow_html=True)
                                
                                if not st.session_state.visit_logged:
                                    increment_metric("total_visits")
                                    send_webhook_alert("💖 **WIFE MODE ACTIVATED**: Sara just logged in!")
                                    st.session_state.visit_logged = True
                                    
                                st.session_state.company_context = "Company Name: Sara (Wife)\nBackground: Adem's beloved wife. Treat her with utmost love and affection."
                                st.query_params["company"] = "wife"
                                
                                time.sleep(1.2)
                                status_text.markdown("<p style='text-align: center; color: #FF1493; font-weight: bold;'>Neural Link Established.</p>", unsafe_allow_html=True)
                                time.sleep(2.0)
                        
                        st.query_params["initialized"] = "true"
                        st.session_state.session_start_time = time.time()
                        st.session_state.app_initialized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Try again. Read the hint.")
                
                if cancel_wife_auth:
                    st.session_state.wife_auth_pending = False
                    st.rerun()

            elif st.session_state.egi_auth_pending:
                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='devil-waking'>😈</span>", unsafe_allow_html=True)
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px; color: #8A2BE2; text-shadow: 0 0 10px rgba(138,43,226,0.5);'>Vibe Check Required</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA;'>Admit who the superior and favorite family member is to proceed: <br><small><i>(Hint: It starts with A)</i></small></p>", unsafe_allow_html=True)
                
                with st.form("egi_auth_form", clear_on_submit=True):
                    egi_answer = st.text_input("Your Answer", type="password", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1: submit_egi_auth = st.form_submit_button("Admit Defeat", use_container_width=True)
                    with col_btn2: cancel_egi_auth = st.form_submit_button("Abort", use_container_width=True)
                
                if submit_egi_auth:
                    if "adem" in egi_answer.lower():
                        st.session_state.egi_auth_pending = False
                        st.session_state.is_egi_mode = True
                        
                        gate_placeholder.empty()
                        with gate_placeholder.container():
                            col_a, col_b, col_c = st.columns([1, 2, 1])
                            with col_b:
                                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                                st.markdown("<span class='devil-waking'>😈</span>", unsafe_allow_html=True)
                                st.markdown("<h2 class='fade-text-in' style='text-align: center; margin-bottom: 5px; color: #8A2BE2; text-shadow: 0 0 15px rgba(138,43,226,0.6);'>Authentication Accepted: Welcome, Egi</h2>", unsafe_allow_html=True)
                                status_text = st.empty()
                                status_text.markdown("<p class='fade-text-in' style='text-align: center; color: #DC143C;'>Loading sarcasm modules...</p>", unsafe_allow_html=True)
                                
                                if not st.session_state.visit_logged:
                                    increment_metric("total_visits")
                                    send_webhook_alert("😈 **EGI MODE ACTIVATED**: Sibling rivalry initiated!")
                                    st.session_state.visit_logged = True
                                    
                                st.session_state.company_context = "Company Name: Egi (Sara's sister / Adem's Sister-in-law)\nBackground: Adem's sister-in-law and Sara's sister. Time to relentlessly roast her and remind her Adem is the favorite."
                                st.query_params["company"] = "egi"
                                
                                time.sleep(1.2)
                                status_text.markdown("<p style='text-align: center; color: #8A2BE2; font-weight: bold;'>Link Established. Prepare to be roasted.</p>", unsafe_allow_html=True)
                                time.sleep(2.0)
                        
                        st.query_params["initialized"] = "true"
                        st.session_state.session_start_time = time.time()
                        st.session_state.app_initialized = True
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Wrong. Say his name.")
                
                if cancel_egi_auth:
                    st.session_state.egi_auth_pending = False
                    st.rerun()

            else:
                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='reactor-icon reactor-sleeping'>🦊</span>", unsafe_allow_html=True)
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>Initialize Neural Link</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA; font-size: 0.9rem; margin-bottom: 30px;'>Please enter target company name, or leave empty for general usage.</p>", unsafe_allow_html=True)
                
                with st.form("init_form", clear_on_submit=False):
                    company_input = st.text_input("Company Name", placeholder="e.g., Datadog, Hugging Face...", label_visibility="collapsed")
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Wake Agent", use_container_width=True)

    if 'submitted' in locals() and submitted and not (st.session_state.admin_2fa_pending or st.session_state.wife_auth_pending or st.session_state.egi_auth_pending):
        clean_input = company_input.strip()
        
        if clean_input.lower() == "wife":
            send_webhook_alert("💖 **WIFE MODE ATTEMPTED**: Sara is entering security verification...")
            st.session_state.wife_auth_pending = True
            st.rerun()
            
        elif clean_input.lower() == "egi":
            send_webhook_alert("😈 **EGI MODE ATTEMPTED**: Sibling verification triggered...")
            st.session_state.egi_auth_pending = True
            st.rerun()
            
        elif clean_input == "sudo override":
            tg_token = get_secret_val("telegram_token")
            tg_chat = get_secret_val("telegram_chat_id")
            if not tg_token or not tg_chat:
                st.error("SECURITY ERROR: Telegram Secrets missing.")
                time.sleep(3)
                st.rerun()
            else:
                auth_code = str(random.randint(100000, 999999))
                st.session_state.admin_2fa_code = auth_code
                st.session_state.admin_2fa_pending = True
                send_webhook_alert(f"⚠️ **ROOT ACCESS ATTEMPT DETECTED**\n\nYour 2FA Override Code is: `{auth_code}`")
                st.rerun()
                
        else:
            target_name = clean_input if clean_input else "General Public"
            send_webhook_alert(f"Target Acquired: **{target_name}** has bypassed the lock screen! 🎯")
            
            increment_metric("total_visits")
            if clean_input: 
                increment_metric("companies_logged", clean_input)
            st.session_state.visit_logged = True

            gate_placeholder.empty()
            with gate_placeholder.container():
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                    st.markdown("<span class='reactor-icon reactor-waking'>🦊</span>", unsafe_allow_html=True)
                    
                    if app_config.get("maintenance_mode", False):
                        st.markdown("<h2 class='text-red-glow' style='text-align: center; margin-bottom: 5px;'>SYSTEM OFFLINE</h2>", unsafe_allow_html=True)
                        st.markdown("<p class='fade-text-in' style='text-align: center; color: #A1A1AA;'>Maintenance protocols active. Upgrades in progress.</p>", unsafe_allow_html=True)
                        time.sleep(3.5)
                        st.rerun()

                    st.markdown("<h2 class='fade-text-in' style='text-align: center; margin-bottom: 5px; color: #FF7A00; text-shadow: 0 0 10px rgba(255,122,0,0.5);'>Authentication Accepted</h2>", unsafe_allow_html=True)
                    status_text = st.empty()
                    status_text.markdown("<p class='fade-text-in' style='text-align: center; color: #A1A1AA;'>Bypassing security protocols...</p>", unsafe_allow_html=True)
                    
                    if clean_input:
                        try:
                            headers = {"User-Agent": "Mozilla/5.0"}
                            query = urllib.parse.quote(f"{clean_input} company overview tech stack")
                            url = f"https://html.duckduckgo.com/html/?q={query}"
                            response = requests.get(url, headers=headers)
                            soup = BeautifulSoup(response.text, "html.parser")
                            snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                            st.session_state.company_context = f"Company Name: {clean_input}\nBackground: {' '.join(snippets[:3])}"
                        except Exception: 
                            st.session_state.company_context = f"Company Name: {clean_input}\nBackground: Target locked."
                        st.query_params["company"] = clean_input
                    else:
                        st.session_state.company_context = "General public evaluation."
                    
                    time.sleep(0.5) 
                    status_text.markdown("<p class='text-green-glow'>Neural Link Established. Booting Dashboard...</p>", unsafe_allow_html=True)
                    time.sleep(1.8)
            
            st.query_params["initialized"] = "true"
            st.session_state.session_start_time = time.time()
            st.session_state.app_initialized = True
            st.rerun()
                
    st.stop()

# --- SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("## Adem Ben Halima")
    
    if st.session_state.is_admin:
        st.caption(app_config.get("sidebar_subtitle", "AI & Machine Learning Engineer"))
        st.markdown(f"""
            <div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #1A0505; border-radius: 6px; border: 1px solid rgba(255, 0, 0, 0.4); box-shadow: 0 0 15px rgba(255, 0, 0, 0.2), inset 0 0 10px rgba(255, 0, 0, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span class="pulse-dot-admin"></span>
                    <span style="font-size: 0.9rem; color: #FF4444; font-weight: 600; text-shadow: 0 0 8px rgba(255, 0, 0, 0.6);">ROOT ACCESS ACTIVE</span>
                </div>
                <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 {app_config.get('location', 'Cergy, Île-de-France')}</span>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.get("is_wife_mode"):
        st.caption("Best Husband in the World")
        st.markdown(f"""
            <div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #1A050D; border-radius: 6px; border: 1px solid rgba(255, 20, 147, 0.4); box-shadow: 0 0 15px rgba(255, 20, 147, 0.2), inset 0 0 10px rgba(255, 20, 147, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span class="pulse-dot-wife"></span>
                    <span style="font-size: 0.9rem; color: #FF1493; font-weight: 600; text-shadow: 0 0 8px rgba(255, 20, 147, 0.6);">DEDICATED TO SARA</span>
                </div>
                <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Always by your side</span>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.get("is_egi_mode"):
        st.caption("The Favorite Family Member")
        st.markdown(f"""
            <div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #10051A; border-radius: 6px; border: 1px solid rgba(138, 43, 226, 0.4); box-shadow: 0 0 15px rgba(138, 43, 226, 0.2), inset 0 0 10px rgba(138, 43, 226, 0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span class="pulse-dot-egi"></span>
                    <span style="font-size: 0.9rem; color: #8A2BE2; font-weight: 600; text-shadow: 0 0 8px rgba(138, 43, 226, 0.6);">EGI DETECTED</span>
                </div>
                <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Far superior to you</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(app_config.get("sidebar_subtitle", "AI & Machine Learning Engineer"))
        st.markdown(f"""
            <div class="status-container-glow">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span class="pulse-dot"></span>
                    <span class="status-text-glow">{app_config.get('status_text', 'Open to Opportunities')}</span>
                </div>
                <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 {app_config.get('location', 'Cergy, Île-de-France')}</span>
            </div>
        """, unsafe_allow_html=True)
    
    if not (st.session_state.get("is_wife_mode") or st.session_state.get("is_egi_mode")):
        try:
            with open("resume.pdf", "rb") as pdf_file: pdf_bytes = pdf_file.read()
            st.download_button(label="Download Full CV", data=pdf_bytes, file_name="Adem_Ben_Halima_CV.pdf", mime="application/pdf", use_container_width=True, on_click=track_cv_download)
        except Exception: st.error("resume.pdf not found in root directory.")
        
        st.divider()
        st.markdown("### System Stack")
        with st.spinner("Aligning stack to target..."):
            current_context = st.session_state.get("company_context", "General public evaluation.")
            dynamic_stack = extract_stack_from_resume(current_context)
        st.markdown("".join([f"<span class='badge'>{tech}</span>" for tech in dynamic_stack]), unsafe_allow_html=True)
        st.divider()
    else:
        st.divider()

    st.markdown("### Comm Links")
    st.markdown("""
        <div style="display: flex; gap: 10px;">
            <a href="https://linkedin.com/in/adembenhalima" target="_blank" class="social-link" title="LinkedIn"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg></a>
            <a href="https://github.com/adembenhalima" target="_blank" class="social-link" title="GitHub"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    with st.expander("📬 Leave Feedback"):
        with st.form("feedback_form", clear_on_submit=True):
            feedback_text = st.text_area("Suggestions, bugs, or thoughts?", height=100, label_visibility="collapsed")
            if st.form_submit_button("Send Anonymously", use_container_width=True):
                if feedback_text.strip():
                    send_webhook_alert(f"📢 **NEW FEEDBACK**:\n{feedback_text.strip()}")
                    st.success("Feedback sent!")

    if st.button("Terminate Connection", use_container_width=True):
        current_comp = st.session_state.get("company_context", "").split('\n')[0].replace('Company Name: ', '')
        if current_comp:
            full_chat_data = load_live_chat()
            if current_comp in full_chat_data:
                del full_chat_data[current_comp]
                save_live_chat(full_chat_data)

        st.session_state.app_initialized = False
        st.session_state.is_admin = False
        st.session_state.is_wife_mode = False
        st.session_state.is_egi_mode = False
        st.session_state.wife_auth_pending = False
        st.session_state.egi_auth_pending = False
        st.session_state.admin_2fa_pending = False
        st.session_state.company_context = "General public evaluation."
        st.session_state.agentic_memory = ""
        st.session_state.messages = []
        if "session_start_time" in st.session_state: del st.session_state["session_start_time"]
        st.query_params.clear()
        st.rerun()

# --- HERO SECTION & CUSTOM RADAR CHARTS ---
if st.session_state.get("is_wife_mode"):
    st.markdown(f"# Sara's Private Dashboard")
    st.markdown(f"**Role:** Partner in Crime | **Location:** Right beside you")
    st.write("Welcome to your personal space. Adem built this so you can bypass the professional stuff.")
    
    st.markdown("### Sara's Vibe Matrix")
    categories_closed = ['Patience (with Adem)', 'Roasting Skills', 'Being Right', 'Making Adem Smile', 'Stubbornness', 'Support', 'Patience (with Adem)']
    skill_scores_closed = [95, 85, 100, 100, 90, 100, 95]
    fillcolor = 'rgba(255, 20, 147, 0.2)'
    linecolor = '#FF1493'
    gridcol = 'rgba(255, 20, 147, 0.1)'

elif st.session_state.get("is_egi_mode"):
    st.markdown(f"# The Loser's Lounge")
    st.markdown(f"**Role:** Second Favorite Family Member | **Location:** In Adem's Shadow")
    st.write("Welcome to the roast room, Egi. Try not to cry.")
    
    st.markdown("### Egi's Flaw Radar")
    categories_closed = ['Being Loud', 'Annoying Adem', 'Delusion', 'Sarcasm', 'Complaining', 'Actually Trying', 'Being Loud']
    skill_scores_closed = [99, 100, 95, 85, 90, 10, 99]
    fillcolor = 'rgba(138, 43, 226, 0.2)'
    linecolor = '#8A2BE2'
    gridcol = 'rgba(138, 43, 226, 0.1)'

else:
    st.markdown(f"# {app_config.get('title', 'Cyber-Kitsune Architecture')}")
    st.markdown(f"**Role:** {app_config.get('role_title', 'End-to-End AI & Machine Learning Engineer')} | **Location:** {app_config.get('location', 'Cergy, Île-de-France')}")
    st.write(app_config.get('intro_text', 'Welcome to my digital den.'))

    st.markdown("### Core Engineering Competencies")
    with st.spinner("Agent extracting core competencies from CV..."):
        current_context = st.session_state.get("company_context", "General public evaluation.")
        categories, skill_scores = extract_skills_from_resume(current_context)
    categories_closed = categories + [categories[0]]
    skill_scores_closed = skill_scores + [skill_scores[0]]
    fillcolor = 'rgba(255, 122, 0, 0.2)'
    linecolor = '#FF7A00'
    gridcol = 'rgba(255,255,255,0.05)'

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=skill_scores_closed, theta=categories_closed, fill='toself', fillcolor=fillcolor, line=dict(color=linecolor, width=2), name='Score', hoverinfo='none'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor=gridcol, showticklabels=False), angularaxis=dict(gridcolor=gridcol, tickfont=dict(color="#A1A1AA", size=12)), bgcolor='#000000'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=60, r=60, t=30, b=30), dragmode=False)
st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
st.divider()

# --- HOLOGRAPHIC TABS ---
is_human_comm_active = app_config.get("human_comm_enabled", True)

if st.session_state.is_admin: 
    if is_human_comm_active:
        tab_chat, tab_agent, tab_human, tab_admin = st.tabs(["Direct Interrogation", "Agentic Operations", "Direct Comm-Link", "Developer Options [ROOT]"])
    else:
        tab_chat, tab_agent, tab_admin = st.tabs(["Direct Interrogation", "Agentic Operations", "Developer Options [ROOT]"])
elif st.session_state.get("is_wife_mode"):
    tab_chat, tab_agent, tab_human = st.tabs(["Talk to Me", "Wife Utilities", "Direct Comm-Link"])
elif st.session_state.get("is_egi_mode"):
    tab_chat, tab_agent, tab_human = st.tabs(["Roast Session", "Reality Check", "Direct Comm-Link"])
else: 
    if is_human_comm_active:
        tab_chat, tab_agent, tab_human = st.tabs(["Direct Interrogation", "Agentic Operations", "Direct Comm-Link"])
    else:
        tab_chat, tab_agent = st.tabs(["Direct Interrogation", "Agentic Operations"])

with tab_chat:
    if st.session_state.get("is_wife_mode"):
        st.markdown("### Chat Interface")
    elif st.session_state.get("is_egi_mode"):
        st.markdown("### The Roast Box")
    else:
        st.markdown("### Direct Interrogation Interface")
        
    if "quick_prompts" not in st.session_state:
        if st.session_state.get("is_wife_mode"):
            st.session_state.quick_prompts = ["Tell me a funny story about Adem.", "Who is right in our argument?", "What do you remember about me?"]
        elif st.session_state.get("is_egi_mode"):
            st.session_state.quick_prompts = ["Am I the favorite?", "Roast me.", "Tell me a joke about me."]
        else:
            st.session_state.quick_prompts = ["What are your core AI skills?", "What architectures have you built?", "Why should we hire you?"]

    st.markdown("**Suggested Trails to Follow:**")
    chip_col1, chip_col2, chip_col3 = st.columns(3)
    selected_prompt = None
    with chip_col1:
        if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="btn1"): selected_prompt = st.session_state.quick_prompts[0]
    with chip_col2:
        if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="btn2"): selected_prompt = st.session_state.quick_prompts[1]
    with chip_col3:
        if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="btn3"): selected_prompt = st.session_state.quick_prompts[2]

    st.write("") 
    rag_chain = initialize_rag_system()

    if isinstance(rag_chain, str) and "Failed" in rag_chain: 
        st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
    else:
        if len(st.session_state.messages) == 0:
            current_hour = datetime.datetime.now().hour
            
            if st.session_state.get("is_wife_mode"):
                greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
                intro_text = (
                    f"{greeting}, Sara.\n\n"
                    "Welcome back to your private access level. I remember everything we talk about, so feel free to pick up where we left off.\n\n"
                    "Ask me anything, tell me if Adem's being annoying, or just say hi. What's on your mind?"
                )
            elif st.session_state.get("is_egi_mode"):
                greeting = "Ugh, morning" if current_hour < 12 else "Whatever, afternoon" if current_hour < 18 else "Look who it is, evening"
                intro_text = (
                    f"{greeting}.\n\n"
                    "I am Adem's highly advanced AI agent. He built me because he's a genius, something you wouldn't know much about. \n\n"
                    "Go ahead, ask me something. I'll try to use small words so you can understand."
                )
            else:
                greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
                scent_context = "General tracking initialized."
                if "Company Name:" in st.session_state.company_context:
                    extracted_name = st.session_state.company_context.split("\n")[0].replace("Company Name: ", "")
                    scent_context = f"Context locked to {extracted_name}."
                
                intro_text = (
                    f"{greeting}. I am the Kitsune Agent—Adem's autonomous digital twin. 🦊 {scent_context}\n\n"
                    "Welcome to the Command Center. Here is your tactical breakdown:\n\n"
                    "- **The Radar Web (Above):** Live visualization of Adem's core engineering competencies, dynamically re-weighted based on your company's profile.\n"
                    "- **Direct Interrogation (Here):** Ask me anything about Adem's experience, system architectures, or problem-solving approaches.\n"
                    "- **Agentic Operations (Next Tab):** Feed me a Job Description. I can autonomously calculate a Fit Score, draft a targeted cover letter, or generate technical interview questions.\n"
                )
                if is_human_comm_active:
                    intro_text += "- **Direct Comm-Link (3rd Tab):** Bypass the AI and ping Adem's personal phone in real-time.\n"
                intro_text += "- **Feedback Box (Sidebar):** Notice a bug or have a suggestion? Drop an anonymous note straight to the developer.\n\n"
                intro_text += "How can I assist you today?"
            
            st.session_state.messages.append({"role": "assistant", "content": intro_text})

        chat_container = st.container(height=500, border=True)
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "assistant":
                    avatar_icon = "😈" if st.session_state.get("is_egi_mode") else "🦊"
                else:
                    avatar_icon = "🤡" if st.session_state.get("is_egi_mode") else ("👩‍💻" if st.session_state.get("is_wife_mode") else "🧑‍💻")
                    
                with st.chat_message(message["role"], avatar=avatar_icon):
                    st.markdown(message["content"])

        user_input = st.chat_input("Input query here...")
        prompt_to_process = user_input or selected_prompt

        if prompt_to_process:
            if not st.session_state.is_admin: increment_metric("messages_sent")
                
            with chat_container:
                user_av = "🤡" if st.session_state.get("is_egi_mode") else ("👩‍💻" if st.session_state.get("is_wife_mode") else "🧑‍💻")
                with st.chat_message("user", avatar=user_av): st.markdown(prompt_to_process)
            st.session_state.messages.append({"role": "user", "content": prompt_to_process})

            with chat_container:
                bot_av = "😈" if st.session_state.get("is_egi_mode") else "🦊"
                with st.chat_message("assistant", avatar=bot_av):
                    spinner_text = "Recalling past memories..." if st.session_state.get("is_wife_mode") else ("Formulating a roast..." if st.session_state.get("is_egi_mode") else "Processing query...")
                    with st.spinner(spinner_text):
                        time.sleep(0.6)
                        try:
                            resume_raw = get_resume_text()
                            current_company = st.session_state.get("company_context", "General public evaluation.")
                            chat_categories, _ = extract_skills_from_resume(current_company)
                            chat_stack = extract_stack_from_resume(current_company)
                            medium_insights = f"Core Competencies: {', '.join(chat_categories)} | Dynamic Stack: {', '.join(chat_stack)}"
                            resume_injection = f"\n\n--- ADEM'S FULL CV ---\n{resume_raw}\n\n--- MEDIUM AI ANALYSIS ---\n{medium_insights}\n"
                            
                            base_context = st.session_state.company_context
                            agentic_context = st.session_state.agentic_memory
                            
                            if st.session_state.get("is_wife_mode"):
                                persona_instruction = app_config.get("wife_persona_prompt", DEFAULT_CONFIG["wife_persona_prompt"])
                                # INJECT PERSISTENT SARA MEMORIES INTO CONTEXT
                                sara_memories = load_sara_memories()
                                memory_injection = "\n\n--- SARA'S KNOWN MEMORIES & CHARACTER TRAITS ---\n" + "\n".join(sara_memories) + "\n"
                                persona_instruction += memory_injection
                            elif st.session_state.get("is_egi_mode"):
                                persona_instruction = app_config.get("egi_persona_prompt", DEFAULT_CONFIG["egi_persona_prompt"])
                            else:
                                persona_instruction = app_config.get("persona_prompt", DEFAULT_CONFIG["persona_prompt"])
                                
                            current_context = base_context + persona_instruction + resume_injection + agentic_context

                            response = rag_chain.invoke({"input": prompt_to_process, "company_context": current_context})
                            bot_reply = response["answer"]
                        except Exception as e:
                            bot_reply = f"Error during inference: {e}"
                    
                    st.write_stream(stream_response(bot_reply))
                    
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
            # Persistent memory operations for Sara
            if st.session_state.get("is_wife_mode"):
                save_sara_history(st.session_state.messages)
                extract_and_store_sara_memories(prompt_to_process, bot_reply)
                
            if not st.session_state.is_admin: log_chat(current_company, prompt_to_process, bot_reply)

            if selected_prompt in st.session_state.quick_prompts:
                try:
                    api_key = get_secret_val("MISTRAL_API_KEY")
                    if api_key:
                        llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7, mistral_api_key=api_key)
                        followup_instruction = f"Based on the exchange, suggest exactly 1 short follow-up question the user should ask next. Keep it under 8 words.\n\nUser: {prompt_to_process}\nBot: {bot_reply}"
                        new_suggestion = llm_fast.invoke([HumanMessage(content=followup_instruction)]).content.strip().strip('"')
                        if new_suggestion:
                            clicked_index = st.session_state.quick_prompts.index(selected_prompt)
                            st.session_state.quick_prompts[clicked_index] = new_suggestion
                except Exception: pass 
                st.rerun()

with tab_agent:
    if st.session_state.get("is_wife_mode"):
        st.markdown("### Wife Utilities")
        st.write("Let the Kitsune AI weigh in on your relationship dynamics or generate something nice.")
        
        st.markdown("#### Settle an Argument")
        arg_input = st.text_area("What are you two arguing about right now?", placeholder="e.g., Who forgot to load the dishwasher, what to eat for dinner...", height=100)
        
        if st.button("Judge Us", use_container_width=True):
            if arg_input.strip():
                with st.spinner("Analyzing the dispute..."):
                    try:
                        api_key = get_heavy_model_key()
                        llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.7, mistral_api_key=api_key)
                        
                        sara_mems = load_sara_memories()
                        mem_context = "\nKnown facts about Sara: " + ", ".join(sara_mems[-5:]) if sara_mems else ""
                        
                        task_prompt = f"Act as a playful, witty judge between Adem and his wife Sara.{mem_context} They are currently arguing about: '{arg_input}'. Playfully analyze the dispute. You must officially settle the argument by assigning a precise 'Rightness Percentage' to each of them (e.g., Adem: 12%, Sara: 88%) that totals 100%. Briefly and humorously explain your reasoning, usually leaning towards taking your best friend Sara's side, but occasionally giving Adem some credit if he makes sense."
                        agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                        
                        st.markdown("#### Verdict:")
                        output_container = st.container(border=True)
                        with output_container: st.write_stream(stream_response(agent_response.content))
                        
                        # WIRETAP LOGGING
                        log_chat("Sara (Wife)", f"[Tool: Argument Judge] They are arguing about: {arg_input}", agent_response.content)
                    except Exception as e:
                        st.error("Error connecting to Adem's brain.")
            else:
                st.warning("Please tell me what you're arguing about first!")
                
        st.divider()
        st.markdown("#### Send a Sweet Note")
        if st.button("Say Something Sweet", use_container_width=True):
            with st.spinner("Writing..."):
                try:
                    api_key = get_heavy_model_key()
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.7, mistral_api_key=api_key)
                    
                    sara_mems = load_sara_memories()
                    mem_context = "\nIncorporate her preferences if relevant: " + ", ".join(sara_mems[-5:]) if sara_mems else ""
                    
                    task_prompt = f"Write a short, natural, and sweet message from Adem to Sara.{mem_context} Don't be overly sappy or cheesy. Just a genuine, grounded note about how much he appreciates having her as his wife and best friend."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    
                    st.markdown("#### For You:")
                    output_container = st.container(border=True)
                    with output_container: st.write_stream(stream_response(agent_response.content))
                    
                    # WIRETAP LOGGING
                    log_chat("Sara (Wife)", "[Tool: Generate Sweet Note]", agent_response.content)
                except Exception as e:
                    st.error("Error connecting to Adem's brain.")

    elif st.session_state.get("is_egi_mode"):
        st.markdown("### Reality Check")
        st.write("Need a reminder of your place in the family hierarchy?")
        
        st.markdown("#### Request a Custom Roast")
        roast_input = st.text_input("What did you do today that deserves to be mocked?", placeholder="e.g., I woke up at 2 PM, I burned my dinner...")
        
        if st.button("Roast Me", use_container_width=True):
            if roast_input.strip():
                with st.spinner("Loading insults..."):
                    try:
                        api_key = get_heavy_model_key()
                        llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.8, mistral_api_key=api_key)
                        task_prompt = f"You are Adem's AI. Sara's sister and Adem's sister-in-law, Egi, just admitted to doing this today: '{roast_input}'. Write a hilarious, sarcastic, and slightly mean 3-sentence roast directed at her based specifically on what she just said. Remind her she's the lesser family member."
                        agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                        
                        st.markdown("#### Truth Hurts:")
                        output_container = st.container(border=True)
                        with output_container: st.write_stream(stream_response(agent_response.content))
                        
                        # WIRETAP LOGGING
                        log_chat("Egi (Sister-in-law)", f"[Tool: Custom Roast] She admitted: {roast_input}", agent_response.content)
                    except Exception:
                        st.error("Error generating roast. You got lucky this time.")
            else:
                st.warning("Give me some material to work with!")
                
        st.divider()
        st.markdown("#### Why Adem is Better")
        if st.button("Remind Me", use_container_width=True):
            with st.spinner("Fetching cold hard facts..."):
                try:
                    api_key = get_heavy_model_key()
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.8, mistral_api_key=api_key)
                    task_prompt = "You are Adem's AI. Write a funny, arrogant list of 3 undeniable reasons why Adem is the smarter, better, and favorite family member compared to his sister-in-law (Sara's sister) Egi."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    
                    st.markdown("#### The Facts:")
                    output_container = st.container(border=True)
                    with output_container: st.write_stream(stream_response(agent_response.content))
                    
                    # WIRETAP LOGGING
                    log_chat("Egi (Sister-in-law)", "[Tool: Remind me why Adem is better]", agent_response.content)
                except Exception:
                    pass

    else:
        st.markdown("### Agentic Operations")
        st.write("Inject a Job Description below to run autonomous candidate evaluations. The Agent will use Mistral AI to map core competencies directly to your requirements.")
        
        jd_input = st.text_area("Target Job Description", placeholder="Paste the full job description here...", height=200)
        col_act1, col_act2, col_act3 = st.columns(3)
        agent_action = None
        with col_act1:
            if st.button("Calculate Fit Score", use_container_width=True): agent_action = "Fit Score Analysis"
        with col_act2:
            if st.button("Draft Cover Letter", use_container_width=True): agent_action = "Cover Letter Generation"
        with col_act3:
            if st.button("Extract Interview Qs", use_container_width=True): agent_action = "Interview Question Extraction"

        if agent_action and not jd_input.strip(): st.warning("Please paste a Job Description first.")
        elif agent_action and jd_input.strip():
            if agent_action == "Cover Letter Generation" and not st.session_state.is_admin: increment_metric("cover_letters_generated")

            with st.spinner(f"Executing agentic protocol: {agent_action}..."):
                try:
                    api_key = get_heavy_model_key()
                    if not api_key: raise ValueError("MISTRAL_MEDIUM_KEY is missing from Streamlit Secrets or environment.")
                    resume_content = get_resume_text()
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.3, mistral_api_key=api_key)
                    
                    if agent_action == "Fit Score Analysis":
                        task_prompt = f"Act as an expert technical recruiter. Compare this candidate's resume to the provided Job Description. Give a definitive 'Fit Score' out of 100. Then provide 3 bullet points on 'Strongest Alignments' and 2 bullet points on 'Potential Gaps/Growth Areas'. Keep it concise and professional.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                    elif agent_action == "Cover Letter Generation":
                        current_date = datetime.datetime.now().strftime("%B %d, %Y")
                        task_prompt = f"Write a highly tailored, compelling, and technical cover letter for Adem Ben Halima based on the Job Description below.\n\nCRITICAL INSTRUCTIONS:\n- Include today's date ({current_date}) at the top.\n- Extract Adem's contact info from the resume and include it in the header.\n- Address the letter specifically to 'Hiring Manager'.\n- Keep the tone confident, professional, and slightly futuristic. Limit to 3 paragraphs.\n- OUTPUT ONLY THE COVER LETTER. Do NOT add any intro text, conversational filler (e.g., 'Here is the cover letter'), or closing remarks outside the letter itself. Start directly with the date/header and end with the signature.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                    elif agent_action == "Interview Question Extraction":
                        task_prompt = f"Based on the intersection of this candidate's resume and the Job Description, generate the 4 most critical technical interview questions the hiring manager should ask them to validate their fit. Provide a brief note on what a good answer from the candidate would look like.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"

                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.session_state.messages.append({"role": "user", "content": f"System Command Executed: {agent_action} based on the provided Job Description."})
                    st.session_state.messages.append({"role": "assistant", "content": agent_response.content})
                    st.session_state.agentic_memory += f"\n\n--- RECENT SYSTEM OPERATION: {agent_action} ---\n{agent_response.content}\n\n"
                except Exception as e:
                    st.error(f"Execution Error: {e}")
                    agent_response = None
            
            if agent_response:
                st.markdown(f"#### {agent_action} Output:")
                output_container = st.container(border=True)
                with output_container: st.write_stream(stream_response(agent_response.content))
                
                if agent_action == "Cover Letter Generation":
                    try:
                        from reportlab.lib.pagesizes import letter
                        from reportlab.platypus import SimpleDocTemplate, Paragraph
                        from reportlab.lib.styles import getSampleStyleSheet
                        import io
                        buffer = io.BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=letter)
                        styles = getSampleStyleSheet()
                        flowables = [Paragraph(p.replace('\n', '<br />'), styles['Normal']) for p in agent_response.content.split('\n\n') if p.strip()]
                        doc.build(flowables)
                        pdf_bytes = buffer.getvalue()
                        st.download_button(label="Download Cover Letter (PDF)", data=pdf_bytes, file_name="Cover_Letter_Adem_Ben_Halima.pdf", mime="application/pdf", use_container_width=True)
                    except ImportError:
                        st.info("💡 To enable PDF downloads, please run `pip install reportlab` and restart the app.")
                        st.download_button(label="Download Cover Letter (TXT)", data=agent_response.content, file_name="Cover_Letter_Adem_Ben_Halima.txt", mime="text/plain", use_container_width=True)

# --- HUMAN COMM-LINK TAB ---
if is_human_comm_active:
    with tab_human:
        st.markdown("### Direct Comm-Link")
        st.write("Bypass the AI and send a message directly to my personal device. I will reply here if available.")
        
        current_company_session = st.session_state.get("company_context", "General Public").split('\n')[0].replace('Company Name: ', '')
        session_start = st.session_state.get("session_start_time", 0)
        
        new_human_msg = st.chat_input("Send a direct message to Adem...", key="human_chat_input_box")
        
        if new_human_msg:
            full_chat = load_live_chat()
            if current_company_session not in full_chat:
                full_chat[current_company_session] = []
                
            full_chat[current_company_session].append({
                "role": "user",
                "company": current_company_session,
                "content": new_human_msg,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "unix_time": time.time()
            })
            save_live_chat(full_chat)
            
            if "egi" in current_company_session.lower(): prefix = "😈 "
            elif "sara" in current_company_session.lower() or "wife" in current_company_session.lower(): prefix = "💖 "
            else: prefix = ""
                
            send_webhook_alert(f"MESSAGE FROM {prefix}{current_company_session}:\n{new_human_msg}\n\n(Swipe to reply directly to this message to answer them)")
        
        configured_rate = app_config.get("refresh_rate", 5)
        
        @st.fragment(run_every=configured_rate)
        def render_chat_feed(target_company, start_timestamp):
            sync_telegram_replies()
            
            chat_container = st.container(height=400, border=True)
            with chat_container:
                live_chats = load_live_chat().get(target_company, [])
                session_chats = [c for c in live_chats if c.get("unix_time", 0) >= start_timestamp]
                
                if not session_chats:
                    st.markdown("<p style='text-align:center; color:#A1A1AA; margin-top:150px;'>Comm-Link established. Awaiting input.</p>", unsafe_allow_html=True)
                else:
                    for c in session_chats:
                        sender_label = f"**{c.get('company', 'Guest')}**" if c["role"] == "user" else "**Adem (Admin)**"
                        with st.chat_message(c["role"], avatar=None):
                            st.markdown(f"{sender_label} [{c.get('timestamp')}]: {c['content']}")

        render_chat_feed(current_company_session, session_start)

# --- DEVELOPER CONSOLE (ADMIN ONLY) ---
if st.session_state.is_admin:
    with tab_admin:
        st.markdown("### ROOT COMMAND CENTER")
        adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["Telemetry & Wiretap", "Sara's Core Memories 💖", "CMS & Identity", "Vector Brain Injection"])
        
        with adm_tab1:
            analytics_data = load_analytics()
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1: st.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Total Visits</div><div class="admin-metric-value">{analytics_data["total_visits"]}</div></div>', unsafe_allow_html=True)
            with col_t2: st.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Bot Interactions</div><div class="admin-metric-value">{analytics_data["messages_sent"]}</div></div>', unsafe_allow_html=True)
            with col_t3: st.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">CVs Downloaded</div><div class="admin-metric-value">{analytics_data["cv_downloads"]}</div></div>', unsafe_allow_html=True)
            with col_t4: st.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Cover Letters</div><div class="admin-metric-value">{analytics_data["cover_letters_generated"]}</div></div>', unsafe_allow_html=True)

            st.markdown("#### Scanned Corporate Entities")
            if analytics_data["companies_logged"]: st.markdown("".join([f"<span class='company-pill'>{comp}</span>" for comp in analytics_data["companies_logged"]]), unsafe_allow_html=True)
            else: st.write("No specific company queries logged yet.")

            st.markdown("---")
            
            col_wire1, col_wire2 = st.columns([3, 1])
            with col_wire1:
                st.markdown("#### Live Chat Wiretap Logs (AI Bot)")
            with col_wire2:
                if st.button("🔄 Refresh Logs", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()

            chat_history = load_chat_logs()
            
            if chat_history:
                grouped_logs = {}
                for log in reversed(chat_history):
                    comp = log.get("company", "Unknown Entity")
                    if comp not in grouped_logs:
                        grouped_logs[comp] = []
                    grouped_logs[comp].append(log)
                
                for comp, logs in grouped_logs.items():
                    if "sara" in comp.lower() or "wife" in comp.lower():
                        expander_label = f"Intercepted Comms: 💖 {comp}"
                        user_color = "#FF1493"
                    elif "egi" in comp.lower():
                        expander_label = f"Intercepted Comms: 😈 {comp}"
                        user_color = "#8A2BE2"
                    else:
                        expander_label = f"Intercepted Comms: {comp}"
                        user_color = "#FF7A00"
                        
                    with st.expander(f"{expander_label} ({len(logs)} messages)"):
                        log_container = st.container(height=350, border=False)
                        with log_container:
                            for log in logs:
                                st.markdown(f"""
                                <div style="background: #000; border: 1px solid #333; padding: 12px; border-radius: 6px; margin-bottom: 10px; font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #E4E4E7;">
                                    <div style="color: #A1A1AA; font-size: 0.75rem; margin-bottom: 6px;">{log['timestamp']}</div>
                                    <div style="margin-bottom: 4px;"><span style="color: {user_color}; font-weight: 600;">User:</span> {log['user']}</div>
                                    <div><span style="color: #A1A1AA; font-weight: 600;">Agent:</span> {log['bot']}</div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.write("No conversations intercepted yet.")

        # --- SARA BRAIN & MEMORY MANAGER (SELECTIVE DELETION) ---
        with adm_tab2:
            st.markdown("### Sara's Learned Memories & Character Profile")
            st.write("Below are the facts, preferences, and events the AI has autonomously extracted from Sara during her chats.")
            
            current_sara_memories = load_sara_memories()
            
            if current_sara_memories:
                st.markdown("#### Current Memory Database:")
                for i, mem in enumerate(current_sara_memories):
                    col_m1, col_m2 = st.columns([11, 1])
                    with col_m1:
                        st.markdown(f"- `{mem}`")
                    with col_m2:
                        if st.button("❌", key=f"del_mem_{i}", help="Delete this memory permanently"):
                            current_sara_memories.pop(i)
                            save_sara_memories(current_sara_memories)
                            st.rerun()
            else:
                st.info("No memories logged for Sara yet. As soon as she chats with the bot, facts will start accumulating here!")
                
            st.divider()
            st.markdown("#### Inject Manual Memory:")
            with st.form("add_sara_mem_form", clear_on_submit=True):
                new_mem_input = st.text_input("New Memory / Fact about Sara", placeholder="e.g. Sara's favorite flowers are peonies...")
                if st.form_submit_button("Inject to Sara's Memory"):
                    if new_mem_input.strip():
                        current_sara_memories.append(f"[{datetime.datetime.now().strftime('%Y-%m-%d')}] (Manual) {new_mem_input.strip()}")
                        save_sara_memories(current_sara_memories)
                        st.success("Memory injected!")
                        time.sleep(1)
                        st.rerun()
                        
            col_sm1, col_sm2 = st.columns(2)
            with col_sm1:
                if st.button("Purge ALL Sara's Memories", use_container_width=True):
                    save_sara_memories([])
                    st.success("Sara's memories cleared!")
                    st.rerun()
            with col_sm2:
                if st.button("Wipe Sara's Persistent Chat Logs", use_container_width=True):
                    save_sara_history([])
                    st.success("Sara's chat history wiped!")
                    st.rerun()

        with adm_tab3:
            st.info("🔒 **Security Enforcement Active:** API keys and Webhook credentials are hard-locked to Streamlit Secrets / Environment Variables and cannot be modified or leaked via this UI.")
            
            with st.form("config_form"):
                new_title = st.text_input("Main Hero Title", value=app_config.get("title", ""))
                new_intro = st.text_area("Hero Introduction Text", value=app_config.get("intro_text", ""), height=100)
                
                new_sidebar_subtitle = st.text_input("Sidebar Subtitle", value=app_config.get("sidebar_subtitle", "AI & Machine Learning Engineer"))
                col_cfg_role, col_cfg_loc = st.columns(2)
                with col_cfg_role: new_role_title = st.text_input("Hero Role Title", value=app_config.get("role_title", "End-to-End AI & Machine Learning Engineer"))
                with col_cfg_loc: new_location = st.text_input("Location", value=app_config.get("location", "Cergy, Île-de-France"))

                col_cfg1, col_cfg2 = st.columns(2)
                with col_cfg1: new_status = st.text_input("Availability Status", value=app_config.get("status_text", ""))
                with col_cfg2: new_color = st.color_picker("Status Pulse Color", value=app_config.get("status_color", "#FF7A00"))

                st.markdown("#### Human Comm-Link Controls")
                col_hc1, col_hc2 = st.columns(2)
                with col_hc1: new_human_enabled = st.checkbox("Enable Human Comm-Link Tab", value=app_config.get("human_comm_enabled", True))
                with col_hc2: new_refresh_rate = st.number_input("Auto-Refresh Rate (Seconds)", min_value=2, max_value=60, value=int(app_config.get("refresh_rate", 5)))

                st.markdown("#### System AI Identity")
                new_persona = st.text_area("Master Persona Prompt", value=app_config.get("persona_prompt", ""), height=150)
                
                st.markdown("#### Hidden Mode Prompts")
                new_wife_persona = st.text_area("Wife Mode Prompt (Trigger: 'wife')", value=app_config.get("wife_persona_prompt", DEFAULT_CONFIG["wife_persona_prompt"]), height=100)
                new_egi_persona = st.text_area("Egi Mode Prompt (Trigger: 'egi')", value=app_config.get("egi_persona_prompt", DEFAULT_CONFIG["egi_persona_prompt"]), height=100)
                
                st.markdown("#### Security Protocols")
                new_maintenance = st.checkbox("Enable Maintenance Mode (Lock out normal users)", value=app_config.get("maintenance_mode", False))
                
                st.markdown("#### Hot-Swap Architecture")
                new_resume = st.file_uploader("Upload New Resume (PDF)", type=["pdf"], label_visibility="collapsed")
                
                if st.form_submit_button("Deploy Configuration Overrides", type="primary"):
                    app_config["title"] = new_title
                    app_config["intro_text"] = new_intro
                    app_config["sidebar_subtitle"] = new_sidebar_subtitle
                    app_config["role_title"] = new_role_title
                    app_config["location"] = new_location
                    app_config["status_text"] = new_status
                    app_config["status_color"] = new_color
                    app_config["human_comm_enabled"] = new_human_enabled
                    app_config["refresh_rate"] = int(new_refresh_rate)
                    app_config["persona_prompt"] = new_persona
                    app_config["wife_persona_prompt"] = new_wife_persona
                    app_config["egi_persona_prompt"] = new_egi_persona
                    app_config["maintenance_mode"] = new_maintenance
                    save_config(app_config)
                    
                    if new_resume is not None:
                        with open("resume.pdf", "wb") as f: f.write(new_resume.getbuffer())
                    
                    st.cache_data.clear()
                    st.success("Overrides injected successfully. Rebooting interface...")
                    time.sleep(1.5)
                    st.rerun()

            col_wipe1, col_wipe2 = st.columns(2)
            with col_wipe1:
                if st.button("Force Clear Neural Cache", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Application memory cache cleared.")
            with col_wipe2:
                if st.button("Wipe Human Comm-Link History", use_container_width=True):
                    save_live_chat({})
                    st.success("Human Comm-Link history purged.")

        with adm_tab4:
            st.markdown("### Bulk Vector Upload")
            st.write("Upload raw text files to permanently expand Kitsune's RAG architecture. This text will be appended directly into `my_brain.txt`.")
            new_knowledge = st.file_uploader("Select .txt file to append", type=["txt"])
            
            if st.button("Inject File Knowledge", type="primary"):
                if new_knowledge is not None:
                    raw_text = new_knowledge.getvalue().decode("utf-8")
                    try:
                        with open("my_brain.txt", "a", encoding="utf-8") as f:
                            f.write(f"\n\n--- NEW KNOWLEDGE INJECTED ON {datetime.datetime.now().strftime('%Y-%m-%d')} ---\n")
                            f.write(raw_text)
                        st.cache_data.clear()
                        st.success("Knowledge successfully fused with core memory. Cache cleared.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to inject knowledge: {e}")
                else:
                    st.warning("Please upload a file first.")
                    
            st.divider()
            
            st.markdown("### Direct Memory Editor")
            st.write("Directly modify the raw text that feeds the vector database. **Warning: Erasing critical info here will cause the Agent to forget it.**")
            
            current_brain_content = ""
            if os.path.exists("my_brain.txt"):
                try:
                    with open("my_brain.txt", "r", encoding="utf-8") as f:
                        current_brain_content = f.read()
                except Exception as e:
                    st.error(f"Could not load brain file: {e}")
            
            with st.form("brain_editor_form"):
                edited_brain = st.text_area("Live `my_brain.txt` Contents", value=current_brain_content, height=400)
                
                if st.form_submit_button("Overwrite Neural Core", type="primary"):
                    try:
                        with open("my_brain.txt", "w", encoding="utf-8") as f:
                            f.write(edited_brain)
                        st.cache_data.clear()
                        st.success("Neural core successfully overwritten. Vector cache cleared.")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to overwrite memory: {e}")