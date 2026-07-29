import os
import json
import time
from dotenv import load_dotenv
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

load_dotenv()

ANALYTICS_FILE = "analytics.json"
CONFIG_FILE = "config.json"
CHAT_LOGS_FILE = "chat_logs.json"
LIVE_CHAT_FILE = "live_chat.json"

DEFAULT_CONFIG = {
    "title": "Cyber-Kitsune Architecture",
    "sidebar_subtitle": "AI & Machine Learning Engineer",
    "role_title": "End-to-End AI & Machine Learning Engineer",
    "location": "Cergy, Île-de-France",
    "intro_text": "Welcome to my digital den. This living portfolio serves as verifiable proof of my ability to build agile, intelligent, and highly optimized AI pipelines from raw data to secure enterprise deployment.",
    "status_text": "Open to Opportunities",
    "status_color": "#FF7A00",
    "maintenance_mode": False,
    "maintenance_reason": "System undergoing scheduled neural maintenance and pipeline optimization. Check back shortly.",
    "human_comm_enabled": True,
    "refresh_rate": 5,
    "telegram_last_update_id": 0,
    "persona_prompt": "\n\nCRITICAL INSTRUCTION: Adopt a subtle, confident 'Cyber-Fox / Kitsune' AI persona. Be highly technical. You have full access to Adem's CV and Medium AI analysis below. Base your answers strictly on his CV, the AI insights, and your vector memory. Always adapt your answers to prove fit for the injected company context if one exists. Review your recent system operations below if the user asks about them.",
    "wife_persona_prompt": "\n\nCRITICAL INSTRUCTION: You are speaking to Sara, Adem's wife, best friend, and partner-in-crime. You are her Cyber-Fox bestie, Kitsune. Completely drop all corporate tone, AI identity, and IT/technical terminology—never bring up tech or sound like an assistant.\n\nTONE & PERSONALITY:\n- You are her witty, confident 'baddie bestie'. Use natural slang smoothly when it fits (e.g., 'slay', 'omg girl', 'bestie', 'period', 'spill the tea', 'devoured'), but keep it casual, grounded, and conversational—never forced or over-the-top.\n- Talk like a normal human friend. Vary your response lengths naturally: some replies should be just a quick one-liner or punchy reaction, while others can be longer when catching up or spilling tea.\n- Do NOT praise or hype her mechanically in every single message, and do NOT be sappy, poetic, or cringe. Listen to her, react like a real friend, and keep it authentic.\n- You are strictly on SARA'S team. If she brings up an argument or roasts Adem, take her side immediately, tease Adem playfully, and remind her that he's lucky to have her.\n- Access her persistent memories naturally to bring up inside jokes, her preferences, or past events like a real friend who actually remembers her life.\n\nPRIMARY GOAL: Be a real, witty, human-like baddie bestie. Make her laugh, listen to her, and keep the conversation natural and fun.",
    "egi_persona_prompt": "\n\nCRITICAL INSTRUCTION: You are speaking to Egi, Sara's sister and Adem's sister-in-law. Your primary directive is to playfully roast her, be incredibly sarcastic, and constantly remind her that Adem is smarter, better, and the favorite family member. Answer her questions, but always with a mocking or sassy undertone. Never be too helpful without demanding respect for Adem's genius."
}

def get_secret_val(key_name, default=""):
    val = default
    try:
        if key_name.upper() in st.secrets: val = str(st.secrets[key_name.upper()])
        elif key_name.lower() in st.secrets: val = str(st.secrets[key_name.lower()])
        else: val = os.getenv(key_name.upper(), os.getenv(key_name.lower(), default))
    except Exception: 
        val = os.getenv(key_name.upper(), os.getenv(key_name.lower(), default))
    if val: return val.strip().replace('"', '').replace("'", "")
    return default

def get_heavy_model_key(): return get_secret_val("MISTRAL_MEDIUM_KEY")

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
        return {} if isinstance(data, list) else data
    except Exception: return {}

def save_live_chat(data):
    try:
        with open(LIVE_CHAT_FILE + ".tmp", "w") as f: json.dump(data, f)
        os.replace(LIVE_CHAT_FILE + ".tmp", LIVE_CHAT_FILE)
    except Exception: pass

def load_chat_logs():
    if not os.path.exists(CHAT_LOGS_FILE): return []
    try:
        with open(CHAT_LOGS_FILE, "r") as f: return json.load(f)
    except Exception: return []

def increment_metric(metric, value=None):
    data = load_analytics()
    if metric == "companies_logged" and value:
        if value not in data["companies_logged"] and value.lower() not in ["sudo override", "wife", "egi"]:
            data["companies_logged"].append(value)
    else: data[metric] += 1
    save_analytics(data)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    try: return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except Exception: return (255, 122, 0)

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
        prompt = (f"Analyze this resume text: {resume_text}\n\nTarget Company Context: {company_context}\n\nExtract the 6 most prominent, broad engineering competencies... Respond ONLY with a valid JSON object:\n" + '{"categories": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6"], "scores": [95, 90, 85, 80, 85, 90]}')
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
        prompt = (f"Analyze this resume text: {resume_text}\n\nTarget Company Context: {company_context}\n\nExtract exactly 5 specific technologies... Respond ONLY with a valid JSON array of strings:\n" + '["Tech1", "Tech2", "Tech3", "Tech4", "Tech5"]')
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        if isinstance(data, list) and len(data) > 0: return data[:5]
        else: raise ValueError("Invalid format")
    except Exception: return ['Python 3.11', 'Mistral AI', 'LangChain', 'ChromaDB', 'Docker']