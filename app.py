import time
import datetime
import random
import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv

from core.utils import load_config, get_secret_val, increment_metric, hex_to_rgb, extract_stack_from_resume, load_live_chat, save_live_chat, DEFAULT_CONFIG
from core.telegram_engine import send_webhook_alert
from core.memory_engine import load_sara_history

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(page_title="AI Engineer | Cyber-Fox Architecture", layout="wide")

# Load configuration
app_config = load_config()

# --- CYBER-KITSUNE STYLING ---
r, g, b = hex_to_rgb(app_config.get('status_color', '#FF7A00'))
st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    .stApp {{ background-color: #0A0807 !important; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    .stApp::before {{
        content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255, 122, 0, 0.08), transparent 60%);
        animation: rotateGlow 20s linear infinite; z-index: 1; pointer-events: none;
    }}
    .stApp::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-image: radial-gradient(circle at 15% 50%, rgba(255, 122, 0, 0.8) 1px, transparent 2px), radial-gradient(circle at 85% 30%, rgba(255, 122, 0, 0.5) 1.5px, transparent 2px);
        background-size: 113px 131px, 89px 97px; opacity: 0.4; animation: risingAshes 20s linear infinite; z-index: 1; pointer-events: none;
    }}
    @keyframes rotateGlow {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    @keyframes risingAshes {{ 0% {{ transform: translateY(0) translateX(0); }} 50% {{ transform: translateY(-25%) translateX(15px); }} 100% {{ transform: translateY(-50%) translateX(0); }} }}
    .block-container {{
        animation: cyberFadeIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; max-width: 1050px !important; 
        background-color: #000000 !important; border: 1px solid rgba(255, 122, 0, 0.4) !important; 
        border-radius: 12px !important; box-shadow: 0 0 30px rgba(0, 0, 0, 0.9), 0 0 15px rgba(255, 122, 0, 0.05) !important;
        padding: 3rem !important; margin-top: 5rem !important; margin-bottom: 4rem !important; position: relative; z-index: 10 !important;
    }}
    [data-testid="stSidebar"] {{ animation: slideRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; background-color: #050403 !important; border-right: 1px solid rgba(255, 122, 0, 0.2); z-index: 20; }}
    @keyframes cyberFadeIn {{ 0% {{ opacity: 0; transform: translateY(40px); filter: blur(10px); }} 100% {{ opacity: 1; transform: translateY(0); filter: blur(0); }} }}
    @keyframes slideRight {{ 0% {{ opacity: 0; transform: translateX(-50px); }} 100% {{ opacity: 1; transform: translateX(0); }} }}
    [data-testid="stBottomBlockContainer"] {{ max-width: 1050px !important; background-color: transparent !important; padding-bottom: 2rem !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border: 1px solid rgba(255, 122, 0, 0.15) !important; border-radius: 8px !important; background-color: #030202 !important; }}
    .stChatInputContainer, [data-testid="stChatInput"] {{ background-color: #000000 !important; border: 1px solid rgba(255, 122, 0, 0.3) !important; border-radius: 8px !important; }}
    [data-testid="stChatMessage"] {{ background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.1) !important; border-radius: 8px; padding: 10px 15px !important; margin-bottom: 6px !important; }}
    button[data-baseweb="tab"] {{ background-color: transparent !important; color: #A1A1AA !important; border-bottom: 2px solid transparent !important; font-family: 'Inter', sans-serif; font-weight: 500; transition: all 0.3s ease; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color: #FF7A00 !important; border-bottom: 2px solid #FF7A00 !important; text-shadow: 0 0 10px rgba(255, 122, 0, 0.5); }}
    button[data-baseweb="tab"]:hover {{ color: #E4E4E7 !important; }}
    h1, h2, h3 {{ color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }}
    .stButton>button {{ background-color: #050403 !important; color: #FFFFFF; border: 1px solid #3F2314; border-radius: 4px; font-weight: 500; transition: all 0.2s; height: 100%; }}
    .stButton>button:hover {{ border: 1px solid #FF7A00 !important; color: #FF7A00 !important; box-shadow: 0 0 10px rgba(255,122,0,0.2); }}
    .social-link {{ display: flex; justify-content: center; align-items: center; flex: 1; color: #A1A1AA; text-decoration: none; padding: 12px; background-color: #050403; border: 1px solid rgba(255, 122, 0, 0.15); border-radius: 6px; transition: all 0.3s ease; }}
    .social-link svg {{ width: 24px; height: 24px; fill: currentColor; }}
    .social-link:hover {{ color: #FF7A00; border-color: #FF7A00; box-shadow: 0 0 10px rgba(255, 122, 0, 0.15); transform: translateY(-2px); }}
    .reactor-icon {{ font-size: 7rem; text-align: center; display: block; margin-bottom: 10px; }}
    .reactor-sleeping {{ filter: grayscale(80%) drop-shadow(0 0 5px rgba(255, 122, 0, 0.1)); animation: reactorBreathe 3s infinite ease-in-out; }}
    @keyframes reactorBreathe {{ 0%, 100% {{ transform: scale(1); filter: grayscale(80%) drop-shadow(0 0 5px rgba(255,122,0,0.1)); }} 50% {{ transform: scale(1.03); filter: grayscale(50%) drop-shadow(0 0 15px rgba(255,122,0,0.3)); }} }}
    .reactor-waking {{ animation: reactorBloom 1.5s forwards ease-in-out; }}
    @keyframes reactorBloom {{ 0% {{ transform: scale(1); opacity: 0; }} 15% {{ opacity: 1; }} 100% {{ transform: scale(1.15); filter: grayscale(0%) drop-shadow(0 0 60px rgba(255, 122, 0, 1)); opacity: 1; }} }}
    .heart-waking {{ font-size: 8rem; text-align: center; display: block; filter: drop-shadow(0 0 20px rgba(255,20,147,0.8)); animation: heartbeat 1.5s infinite; }}
    @keyframes heartbeat {{ 0%, 30%, 100% {{ transform: scale(1); }} 15%, 45% {{ transform: scale(1.15); }} }}
    .devil-waking {{ font-size: 8rem; text-align: center; display: block; filter: drop-shadow(0 0 20px rgba(138, 43, 226,0.8)); animation: devilbreathe 2s infinite alternate ease-in-out; }}
    @keyframes devilbreathe {{ 0% {{ transform: scale(1); filter: drop-shadow(0 0 10px rgba(138,43,226,0.5)); }} 100% {{ transform: scale(1.1); filter: drop-shadow(0 0 35px rgba(220,20,60,0.9)); }} }}
    .fade-text-in {{ animation: cyberFadeIn 1s forwards; }}
    .text-red-glow {{ text-align: center; color: #FF0000 !important; font-weight: 700; letter-spacing: 1px; text-shadow: 0 0 10px rgba(255, 0, 0, 0.6); animation: alertPulse 1s infinite alternate; }}
    @keyframes alertPulse {{ 0% {{ text-shadow: 0 0 10px rgba(255, 0, 0, 0.5); }} 100% {{ text-shadow: 0 0 20px rgba(255, 0, 0, 0.9); }} }}
    .pulse-dot {{ display: inline-block; width: 10px; height: 10px; background-color: {app_config.get('status_color', '#FF7A00')} !important; border-radius: 50%; box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0.7) !important; animation: pulseDynamic 1.8s infinite !important; margin-right: 8px; }}
    @keyframes pulseDynamic {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba({r}, {g}, {b}, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba({r}, {g}, {b}, 0); }} }}
    .status-container-glow {{ margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #050200; border-radius: 6px; border: 1px solid rgba({r}, {g}, {b}, 0.4); box-shadow: 0 0 15px rgba({r}, {g}, {b}, 0.15), inset 0 0 10px rgba({r}, {g}, {b}, 0.05); }}
    .status-text-glow {{ font-size: 0.9rem; color: #F8FAFC; font-weight: 600; text-shadow: 0 0 8px rgba({r}, {g}, {b}, 0.6); }}
    </style>
""", unsafe_allow_html=True)

# --- STATE INITIALIZATION ---
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
    if "session_start_time" not in st.session_state: st.session_state.session_start_time = time.time()
    if "company_context" not in st.session_state:
        saved_company = st.query_params.get("company", "")
        if st.session_state.is_admin: st.session_state.company_context = "SYSTEM ROOT: ADMIN OVERRIDE PROTOCOL ENABLED."
        elif st.session_state.is_wife_mode: st.session_state.company_context = "Company Name: Sara (Wife)\nBackground: Adem's beloved wife. Treat her with utmost love and affection."
        elif st.session_state.is_egi_mode: st.session_state.company_context = "Company Name: Egi (Sara's sister / Adem's Sister-in-law)\nBackground: Adem's sister-in-law and Sara's sister. Time to relentlessly roast her and remind her Adem is the favorite."
        elif saved_company: st.session_state.company_context = f"Company Name: {saved_company}\nBackground: Restored from neural memory link."
        else: st.session_state.company_context = "General public evaluation."
            
if "app_initialized" not in st.session_state: st.session_state.app_initialized = False
if "agentic_memory" not in st.session_state: st.session_state.agentic_memory = ""
if "messages" not in st.session_state: st.session_state.messages = load_sara_history() if st.session_state.get("is_wife_mode") else []

# --- MAINTENANCE MODE LOCKOUT FOR NON-ADMINS ---
is_maintenance_on = app_config.get("maintenance_mode", False)
if is_maintenance_on and not st.session_state.is_admin:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        if st.session_state.admin_2fa_pending:
            st.markdown("<span class='reactor-icon reactor-waking'>🔐</span><h2 class='text-red-glow' style='text-align: center;'>ADMIN VERIFICATION</h2>", unsafe_allow_html=True)
            with st.form("maint_otp_form", clear_on_submit=True):
                otp_input = st.text_input("Enter 6-Digit Code", max_chars=6, type="password", label_visibility="collapsed")
                col_b1, col_b2 = st.columns(2)
                if col_b1.form_submit_button("Verify Access", use_container_width=True):
                    if st.session_state.admin_2fa_code and otp_input.strip() == st.session_state.admin_2fa_code:
                        st.session_state.update(admin_2fa_pending=False, admin_2fa_code="", is_admin=True, company_context="SYSTEM ROOT: ADMIN OVERRIDE PROTOCOL ENABLED.", app_initialized=True, session_start_time=time.time())
                        st.query_params.update(company="ROOT", initialized="true")
                        st.rerun()
                    else: st.error("Incorrect code.")
                if col_b2.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.admin_2fa_pending = False
                    st.rerun()
        else:
            st.markdown("<span class='reactor-icon reactor-sleeping'>🦊</span>", unsafe_allow_html=True)
            st.markdown("<h2 class='text-red-glow' style='text-align: center;'>SYSTEM OFFLINE</h2>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; color: #A1A1AA; margin-bottom: 25px;'>{app_config.get('maintenance_reason', DEFAULT_CONFIG['maintenance_reason'])}</div>", unsafe_allow_html=True)
            
            with st.expander("🔑 Admin Override Access"):
                with st.form("maint_admin_form", clear_on_submit=True):
                    admin_pass = st.text_input("Admin Override Command", type="password", placeholder="Enter 'sudo override'")
                    if st.form_submit_button("Request 2FA OTP", use_container_width=True):
                        if admin_pass.strip() == "sudo override":
                            auth_code = str(random.randint(100000, 999999))
                            st.session_state.update(admin_2fa_code=auth_code, admin_2fa_pending=True)
                            send_webhook_alert(f"⚠️ ROOT ACCESS ATTEMPT (Maintenance Mode)\n\n2FA Code: {auth_code}")
                            st.rerun()
                        else: st.error("Invalid command.")
    st.stop()

# --- LOCK SCREEN / GATEKEEPER ROUTING ---
if not st.session_state.app_initialized:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    gate_placeholder = st.empty()
    
    with gate_placeholder.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.admin_2fa_pending:
                st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
                st.markdown("<span class='reactor-icon reactor-waking'>🔐</span><h2 style='text-align: center; color: #FF0000;'>AUTHORIZATION REQUIRED</h2>", unsafe_allow_html=True)
                with st.form("otp_form", clear_on_submit=True):
                    otp_input = st.text_input("Enter Code", max_chars=6, type="password", label_visibility="collapsed")
                    col_btn1, col_btn2 = st.columns(2)
                    submit_otp = col_btn1.form_submit_button("Verify Access", use_container_width=True)
                    cancel_otp = col_btn2.form_submit_button("Abort", use_container_width=True)
                if submit_otp:
                    if st.session_state.admin_2fa_code and otp_input.strip() == st.session_state.admin_2fa_code:
                        st.session_state.update(admin_2fa_pending=False, admin_2fa_code="", is_admin=True, company_context="SYSTEM ROOT: ADMIN OVERRIDE PROTOCOL ENABLED.", app_initialized=True, session_start_time=time.time())
                        st.query_params.update(company="ROOT", initialized="true")
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Incorrect authorization code.")
                if cancel_otp:
                    st.session_state.admin_2fa_pending = False
                    st.session_state.admin_2fa_code = ""
                    st.rerun()
            
            elif st.session_state.wife_auth_pending:
                st.markdown("<div style='height: 5vh;'></div><span class='heart-waking'>💖</span><h2 style='text-align: center; color: #FF1493;'>Verification Required</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA;'>What do I like about you the most? <br><small><i>(Hint: The answer is everything)</i></small></p>", unsafe_allow_html=True)
                with st.form("wife_auth_form", clear_on_submit=True):
                    wife_answer = st.text_input("Your Answer", type="password", label_visibility="collapsed")
                    col_btn1, col_btn2 = st.columns(2)
                    submit_wife = col_btn1.form_submit_button("Verify", use_container_width=True)
                    cancel_wife = col_btn2.form_submit_button("Abort", use_container_width=True)
                if submit_wife:
                    if "everything" in wife_answer.lower():
                        st.session_state.update(wife_auth_pending=False, is_wife_mode=True, messages=load_sara_history(), company_context="Company Name: Sara (Wife)\nBackground: Adem's beloved wife.", app_initialized=True, session_start_time=time.time())
                        st.query_params.update(company="wife", initialized="true")
                        send_webhook_alert("💖 WIFE MODE ACTIVATED: Sara just logged in!")
                        st.session_state.visit_logged = True
                        st.rerun()
                    else: st.error("ACCESS DENIED.")
                if cancel_wife: st.session_state.wife_auth_pending = False; st.rerun()

            elif st.session_state.egi_auth_pending:
                st.markdown("<div style='height: 5vh;'></div><span class='devil-waking'>😈</span><h2 style='text-align: center; color: #8A2BE2;'>Vibe Check Required</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #A1A1AA;'>Admit who the superior family member is: <br><small><i>(Hint: Starts with A)</i></small></p>", unsafe_allow_html=True)
                with st.form("egi_auth_form", clear_on_submit=True):
                    egi_answer = st.text_input("Your Answer", type="password", label_visibility="collapsed")
                    col_btn1, col_btn2 = st.columns(2)
                    submit_egi = col_btn1.form_submit_button("Admit Defeat", use_container_width=True)
                    cancel_egi = col_btn2.form_submit_button("Abort", use_container_width=True)
                if submit_egi:
                    if "adem" in egi_answer.lower():
                        st.session_state.update(egi_auth_pending=False, is_egi_mode=True, company_context="Company Name: Egi (Sara's sister / Adem's Sister-in-law)\nBackground: Adem's sister-in-law and Sara's sister.", app_initialized=True, session_start_time=time.time())
                        st.query_params.update(company="egi", initialized="true")
                        send_webhook_alert("😈 EGI MODE ACTIVATED: In-law rivalry initiated!")
                        st.session_state.visit_logged = True
                        st.rerun()
                    else: st.error("ACCESS DENIED: Say his name.")
                if cancel_egi: st.session_state.egi_auth_pending = False; st.rerun()

            else:
                st.markdown("<div style='height: 5vh;'></div><span class='reactor-icon reactor-sleeping'>🦊</span><h2 style='text-align: center;'>Initialize Neural Link</h2>", unsafe_allow_html=True)
                with st.form("init_form", clear_on_submit=False):
                    company_input = st.text_input("Company Name", placeholder="e.g., Datadog, Hugging Face...", label_visibility="collapsed")
                    submitted = st.form_submit_button("Wake Agent", use_container_width=True)

    if 'submitted' in locals() and submitted and not (st.session_state.admin_2fa_pending or st.session_state.wife_auth_pending or st.session_state.egi_auth_pending):
        clean_input = company_input.strip()
        if clean_input.lower() == "wife": st.session_state.wife_auth_pending = True; st.rerun()
        elif clean_input.lower() == "egi": st.session_state.egi_auth_pending = True; st.rerun()
        elif clean_input == "sudo override":
            auth_code = str(random.randint(100000, 999999))
            st.session_state.update(admin_2fa_code=auth_code, admin_2fa_pending=True)
            send_webhook_alert(f"⚠️ ROOT ACCESS ATTEMPT DETECTED\n\n2FA Override Code: {auth_code}")
            st.rerun()
        else:
            target_name = clean_input if clean_input else "General Public"
            send_webhook_alert(f"TARGET ACQUIRED: {target_name} has entered the digital den! 🎯")
            increment_metric("total_visits")
            if clean_input: increment_metric("companies_logged", clean_input)
            st.session_state.visit_logged = True

            if clean_input:
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    query = urllib.parse.quote(f"{clean_input} company overview tech stack")
                    response = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                    st.session_state.company_context = f"Company Name: {clean_input}\nBackground: {' '.join(snippets[:3])}"
                except Exception: st.session_state.company_context = f"Company Name: {clean_input}\nBackground: Target locked."
                st.query_params["company"] = clean_input
            else: st.session_state.company_context = "General public evaluation."
            
            st.session_state.update(app_initialized=True, session_start_time=time.time())
            st.query_params["initialized"] = "true"
            st.rerun()
    st.stop()

# --- SIDEBAR (SHARED) ---
with st.sidebar:
    st.markdown("## Adem Ben Halima")
    if st.session_state.is_admin:
        st.caption(app_config.get("sidebar_subtitle", "AI & Machine Learning Engineer"))
        st.markdown(f'<div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #1A0505; border-radius: 6px; border: 1px solid rgba(255, 0, 0, 0.4);"><div style="display: flex; align-items: center; margin-bottom: 4px;"><span class="pulse-dot" style="background-color:#FF0000!important;"></span><span style="font-size: 0.9rem; color: #FF4444; font-weight: 600;">ROOT ACCESS ACTIVE</span></div><span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 {app_config.get("location")}</span></div>', unsafe_allow_html=True)
    elif st.session_state.get("is_wife_mode"):
        st.caption("Best Husband in the World")
        st.markdown(f'<div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #1A050D; border-radius: 6px; border: 1px solid rgba(255, 20, 147, 0.4);"><div style="display: flex; align-items: center; margin-bottom: 4px;"><span class="pulse-dot" style="background-color:#FF1493!important;"></span><span style="font-size: 0.9rem; color: #FF1493; font-weight: 600;">DEDICATED TO SARA</span></div><span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Always by your side</span></div>', unsafe_allow_html=True)
    elif st.session_state.get("is_egi_mode"):
        st.caption("The Favorite Family Member")
        st.markdown(f'<div style="margin-bottom: 15px; margin-top: 10px; padding: 12px; background: #10051A; border-radius: 6px; border: 1px solid rgba(138, 43, 226, 0.4);"><div style="display: flex; align-items: center; margin-bottom: 4px;"><span class="pulse-dot" style="background-color:#8A2BE2!important;"></span><span style="font-size: 0.9rem; color: #8A2BE2; font-weight: 600;">EGI DETECTED</span></div><span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Far superior to you</span></div>', unsafe_allow_html=True)
    else:
        st.caption(app_config.get("sidebar_subtitle", "AI & Machine Learning Engineer"))
        st.markdown(f'<div class="status-container-glow"><div style="display: flex; align-items: center; margin-bottom: 4px;"><span class="pulse-dot"></span><span class="status-text-glow">{app_config.get("status_text")}</span></div><span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 {app_config.get("location")}</span></div>', unsafe_allow_html=True)
    
    if not (st.session_state.get("is_wife_mode") or st.session_state.get("is_egi_mode")):
        try:
            with open("resume.pdf", "rb") as pdf_file: 
                st.download_button("Download Full CV", pdf_file.read(), "Adem_Ben_Halima_CV.pdf", "application/pdf", use_container_width=True)
        except Exception: pass
        st.divider()
        st.markdown("### System Stack")
        st.markdown("".join([f"<span class='badge'>{tech}</span>" for tech in extract_stack_from_resume(st.session_state.company_context)]), unsafe_allow_html=True)
    
    st.divider()
    st.markdown("""<div style="display: flex; gap: 10px;"><a href="https://linkedin.com/in/adembenhalima" target="_blank" class="social-link" title="LinkedIn"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg></a><a href="https://github.com/adembenhalima" target="_blank" class="social-link" title="GitHub"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a></div>""", unsafe_allow_html=True)
    st.divider()

    with st.expander("📬 Leave Feedback"):
        with st.form("feedback_form", clear_on_submit=True):
            feedback_text = st.text_area("Suggestions, bugs, or thoughts?", height=100, label_visibility="collapsed")
            if st.form_submit_button("Send Anonymously", use_container_width=True) and feedback_text.strip():
                send_webhook_alert(f"📢 **NEW FEEDBACK**:\n{feedback_text.strip()}")
                st.success("Feedback sent!")

    if st.button("Terminate Connection", use_container_width=True):
        current_comp = st.session_state.get("company_context", "").split('\n')[0].replace('Company Name: ', '')
        if current_comp:
            full_chat = load_live_chat()
            if current_comp in full_chat: del full_chat[current_comp]; save_live_chat(full_chat)
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# --- COMPONENT ROUTING ---
if st.session_state.is_admin:
    import views.admin_view as admin_view
    admin_view.render(app_config)
elif st.session_state.is_wife_mode:
    import views.wife_view as wife_view
    wife_view.render(app_config)
elif st.session_state.is_egi_mode:
    import views.egi_view as egi_view
    egi_view.render(app_config)
else:
    import views.public_view as public_view
    public_view.render(app_config)