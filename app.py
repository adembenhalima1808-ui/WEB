import time
import datetime
import json
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

# --- GENERATOR FOR TYPEWRITER EFFECT ---
def stream_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.015)

# --- CACHED RESUME TEXT FOR AGENTIC TOOLS ---
@st.cache_data(show_spinner=False)
def get_resume_text():
    try:
        loader = PyPDFLoader("resume.pdf")
        docs = loader.load()
        return " ".join([page.page_content for page in docs])
    except:
        return "Adem Ben Halima is an AI & Machine Learning Engineer experienced in Python, LangChain, Mistral, and Docker."

# --- AUTONOMOUS CV SCANNER (CACHED) ---
@st.cache_data(show_spinner=False)
def extract_skills_from_resume():
    try:
        resume_text = get_resume_text()
        llm = ChatMistralAI(model="mistral-medium-latest", temperature=0.1)
        prompt = (
            f"Analyze this resume text: {resume_text}\n\n"
            "Extract the 6 most prominent, broad engineering competencies (e.g., 'Data Engineering', 'Machine Learning', 'DevOps'). "
            "Assign a realistic proficiency score out of 100 for each based on the depth of experience shown. "
            "Respond ONLY with a valid JSON object in this exact format, with no markdown blocks, no intro, and no extra text:\n"
            '{"categories": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6"], "scores": [95, 90, 85, 80, 85, 90]}'
        )
        
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        return data["categories"], data["scores"]
    except Exception as e:
        return ['Machine Learning', 'Python Backend', 'Data Engineering', 'DevOps', 'System Architecture', 'Prompt Engineering'], [90, 85, 80, 75, 85, 80]

# --- CYBER-KITSUNE CHIC + KINETIC CSS ---
st.markdown("""
    <style>
    /* Base App Background */
    .stApp { background-color: #0A0807 !important; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    /* 1. Deep Background Glow */
    .stApp::before {
        content: ""; position: fixed; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255, 122, 0, 0.08), transparent 60%);
        animation: rotateGlow 20s linear infinite; z-index: 1; pointer-events: none;
    }

    /* 2. Organic Fire Ashes */
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
    @keyframes risingAshes {
        0% { transform: translateY(0) translateX(0); }
        50% { transform: translateY(-25%) translateX(15px); }
        100% { transform: translateY(-50%) translateX(0); }
    }

    /* 3. DASHBOARD ENTRANCE ANIMATIONS */
    .block-container {
        animation: cyberFadeIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        max-width: 1050px !important; 
        background-color: #000000 !important; 
        border: 1px solid rgba(255, 122, 0, 0.4) !important; 
        border-radius: 12px !important;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.9), 0 0 15px rgba(255, 122, 0, 0.05) !important;
        padding: 3rem !important; 
        margin-top: 5rem !important;
        margin-bottom: 4rem !important; 
        position: relative;
        z-index: 10 !important;
    }
    
    [data-testid="stSidebar"] { 
        animation: slideRight 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        background-color: #050403 !important; 
        border-right: 1px solid rgba(255, 122, 0, 0.2); z-index: 20; 
    }

    @keyframes cyberFadeIn {
        0% { opacity: 0; transform: translateY(40px); filter: blur(10px); }
        100% { opacity: 1; transform: translateY(0); filter: blur(0); }
    }
    
    @keyframes slideRight {
        0% { opacity: 0; transform: translateX(-50px); }
        100% { opacity: 1; transform: translateX(0); }
    }
    
    [data-testid="stBottomBlockContainer"] { max-width: 1050px !important; background-color: transparent !important; padding-bottom: 2rem !important; }

    /* Inner Block Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid rgba(255, 122, 0, 0.15) !important; border-radius: 8px !important; background-color: #030202 !important; }
    .stChatInputContainer, [data-testid="stChatInput"] { background-color: #000000 !important; border: 1px solid rgba(255, 122, 0, 0.3) !important; border-radius: 8px !important; }
    [data-testid="stChatMessage"], [data-testid="stExpander"], div[data-testid="stStatusWidget"] { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.1) !important; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
    [data-testid="stTextArea"] > div > div { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.2) !important; }

    /* Holographic Tabs */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #A1A1AA !important;
        border-bottom: 2px solid transparent !important;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FF7A00 !important;
        border-bottom: 2px solid #FF7A00 !important;
        text-shadow: 0 0 10px rgba(255, 122, 0, 0.5);
    }
    button[data-baseweb="tab"]:hover { color: #E4E4E7 !important; }

    /* Headers */
    h1 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; text-shadow: 0 0 5px rgba(255, 122, 0, 0.2), 0 0 15px rgba(255, 122, 0, 0.1); animation: neonFlicker 4s infinite alternate; }
    @keyframes neonFlicker { 0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 5px rgba(255, 122, 0, 0.3), 0 0 15px rgba(255, 122, 0, 0.1); } 20%, 22%, 24%, 55% { opacity: 0.8; text-shadow: none; } }
    h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    
    /* Buttons & Badges */
    .stButton>button { background-color: #050403 !important; color: #FFFFFF; border: 1px solid #3F2314; border-radius: 4px; font-weight: 500; font-size: 0.8rem; transition: all 0.2s; height: 100%; }
    .stButton>button:hover { border: 1px solid #FF7A00 !important; color: #FF7A00 !important; box-shadow: 0 0 10px rgba(255,122,0,0.2); }
    .badge { display: inline-block; background: #050403 !important; color: #E4E4E7; border: 1px solid #3F2314; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 500; margin-right: 6px; margin-bottom: 8px; }
    
    /* Metric Cards */
    .metric-card { background-color: #050403 !important; border: 1px solid rgba(255, 122, 0, 0.15); border-radius: 8px; padding: 14px 18px; margin-bottom: 1rem; transition: transform 0.3s ease, box-shadow 0.3s ease; }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 8px 24px rgba(255, 122, 0, 0.15); border: 1px solid rgba(255, 122, 0, 0.4); }
    .metric-value { color: #FF7A00; font-family: 'JetBrains Mono', monospace; font-size: 1.4rem; font-weight: 600; }
    .metric-label { color: #A1A1AA; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }
    
    /* Pulse Dot & Animations */
    .pulse-dot { display: inline-block; width: 10px; height: 10px; background-color: #FF7A00; border-radius: 50%; box-shadow: 0 0 0 0 rgba(255, 122, 0, 0.7); animation: pulse 1.8s infinite; margin-right: 8px; }
    @keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 122, 0, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 122, 0, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 122, 0, 0); } }
    .big-fox { font-size: 7rem; margin-bottom: 10px; animation: pulseFox 3s infinite; text-align: center; display: block; }
    @keyframes pulseFox { 0% { transform: scale(1); filter: drop-shadow(0 0 5px rgba(255,122,0,0.2)); } 50% { transform: scale(1.05); filter: drop-shadow(0 0 25px rgba(255,122,0,0.6)); } 100% { transform: scale(1); filter: drop-shadow(0 0 5px rgba(255,122,0,0.2)); } }
    </style>
""", unsafe_allow_html=True)

# --- APP INITIALIZATION STATE (PERSISTENT VIA URL) ---
if st.query_params.get("initialized") == "true":
    st.session_state.app_initialized = True
    if "company_context" not in st.session_state:
        saved_company = st.query_params.get("company", "")
        if saved_company:
            st.session_state.company_context = f"Company Name: {saved_company}\nBackground: Restored from neural memory link."
        else:
            st.session_state.company_context = "General public evaluation."
            
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = False

# --- THE CYBER-GATE LOCK SCREEN WITH SMOOTH TRANSITION ---
if not st.session_state.app_initialized:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    
    gate_placeholder = st.empty()
    
    with gate_placeholder.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
            st.markdown("<span class='big-fox'>🦊</span>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>Initialize Neural Link</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #A1A1AA; font-size: 0.9rem; margin-bottom: 30px;'>Please enter target company name, or leave empty for general usage.</p>", unsafe_allow_html=True)
            
            with st.form("init_form", clear_on_submit=False):
                company_input = st.text_input("Company Name", placeholder="e.g., Datadog, Hugging Face...", label_visibility="collapsed")
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Wake Kitsune Agent", use_container_width=True)
                
    if submitted:
        gate_placeholder.empty()
        with gate_placeholder.container():
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; font-size: 4rem; animation: neonFlicker 1s infinite;'>🦊</div>", unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; color: #FF7A00;'>Authentication Accepted</h3>", unsafe_allow_html=True)
                
                status_text = st.empty()
                status_text.markdown("<p style='text-align: center; color: #A1A1AA;'>Bypassing security protocols...</p>", unsafe_allow_html=True)
                time.sleep(0.5)
                
                if company_input.strip():
                    status_text.markdown(f"<p style='text-align: center; color: #A1A1AA;'>Tracking digital footprint for {company_input}...</p>", unsafe_allow_html=True)
                    try:
                        headers = {"User-Agent": "Mozilla/5.0"}
                        query = urllib.parse.quote(f"{company_input} company overview tech stack")
                        url = f"https://html.duckduckgo.com/html/?q={query}"
                        response = requests.get(url, headers=headers)
                        soup = BeautifulSoup(response.text, "html.parser")
                        snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                        st.session_state.company_context = f"Company Name: {company_input}\nBackground: {' '.join(snippets[:3])}"
                    except Exception:
                        st.session_state.company_context = f"Company Name: {company_input}\nBackground: Target locked."
                    
                    st.query_params["company"] = company_input.strip()
                else:
                    st.session_state.company_context = "General public evaluation."
                
                status_text.markdown("<p style='text-align: center; color: #00FF00; font-weight: 600;'>Neural Link Established. Booting Dashboard...</p>", unsafe_allow_html=True)
                time.sleep(0.8) 
            
        st.query_params["initialized"] = "true"
        st.session_state.app_initialized = True
        st.rerun()
                
    st.stop()

# --- SIDEBAR CONTENT (ONLY SHOWS AFTER UNLOCK) ---
with st.sidebar:
    st.markdown("## 🦊 Adem Ben Halima")
    st.caption("AI & Machine Learning Engineer")
    
    st.markdown("""
        <div style="margin-bottom: 15px; padding: 12px; background: #000000; border-radius: 4px; border: 1px solid #271A12;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span class="pulse-dot"></span>
                <span style="font-size: 0.9rem; color: #F8FAFC; font-weight: 600;">Kitsune Agent Awake</span>
            </div>
            <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Cergy, Île-de-France</span>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        with open("resume.pdf", "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.download_button(
            label="📄 Download Full CV",
            data=pdf_bytes,
            file_name="Adem_Ben_Halima_CV.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except FileNotFoundError:
        st.error("resume.pdf not found in root directory.")
    
    st.divider()
    
    st.markdown("### 🛠 System Stack")
    st.markdown("""
        <span class="badge">Python 3.11</span>
        <span class="badge">Mistral AI</span>
        <span class="badge">LangChain</span>
        <span class="badge">ChromaDB</span>
        <span class="badge">Docker</span>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    fox_placeholder = st.empty()
    fox_placeholder.markdown("<div style='text-align: center; font-size: 3.5rem; transition: 0.3s;'>🦊💤</div>", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("# Cyber-Kitsune Architecture")
st.markdown("**Role:** End-to-End AI & Machine Learning Engineer | **Location:** Cergy, Île-de-France")
st.write(
    "Welcome to my digital den. This living portfolio serves as verifiable proof of my ability to build agile, intelligent, "
    "and highly optimized AI pipelines from raw data to secure enterprise deployment."
)

# --- INTERACTIVE PLOTLY RADAR CHART ---
st.markdown("### 🕸 Core Engineering Competencies")

with st.spinner("Kitsune Agent is extracting core competencies from CV..."):
    categories, skill_scores = extract_skills_from_resume()

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
      r=skill_scores,
      theta=categories,
      fill='toself',
      fillcolor='rgba(255, 122, 0, 0.2)',
      line=dict(color='#FF7A00', width=2),
      name='Skill Level'
))
fig.update_layout(
  polar=dict(
    radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.05)', showticklabels=False),
    angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color="#A1A1AA", size=12)),
    bgcolor='#000000' 
  ),
  paper_bgcolor='rgba(0,0,0,0)', 
  plot_bgcolor='rgba(0,0,0,0)',
  height=380,
  margin=dict(l=60, r=60, t=30, b=30)
)
st.plotly_chart(fig, use_container_width=True)

# --- SYSTEM METRICS ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown('<div class="metric-card"><div class="metric-label">LLM Engine</div><div class="metric-value">Mistral Medium</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown('<div class="metric-card"><div class="metric-label">Vector Store</div><div class="metric-value">ChromaDB</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown('<div class="metric-card"><div class="metric-label">Tracking Latency</div><div class="metric-value">&lt; 850ms</div></div>', unsafe_allow_html=True)

st.divider()

# =====================================================================
# --- HOLOGRAPHIC TABS: CHAT & AGENTIC OPERATIONS ---
# =====================================================================
tab_chat, tab_agent = st.tabs(["Direct Interrogation", "Agentic Operations"])

with tab_chat:
    st.markdown("### Direct Interrogation Interface")

    if "quick_prompts" not in st.session_state:
        st.session_state.quick_prompts = [
            "What are your core AI skills?",
            "What architectures have you built?",
            "Why should we hire you?"
        ]

    st.markdown("**Suggested Trails to Follow:**")
    chip_col1, chip_col2, chip_col3 = st.columns(3)
    selected_prompt = None

    with chip_col1:
        if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="btn1"): selected_prompt = st.session_state.quick_prompts[0]
    with chip_col2:
        if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="btn2"): selected_prompt = st.session_state.quick_prompts[1]
    with chip_col3:
        if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="btn3"): selected_prompt = st.session_state.quick_prompts[2]

    st.write("") # Spacer

    rag_chain = initialize_rag_system()

    if isinstance(rag_chain, str) and "Failed" in rag_chain:
        st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
    else:
        if "messages" not in st.session_state:
            current_hour = datetime.datetime.now().hour
            greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
            
            scent_context = "General tracking initialized."
            if "Company Name:" in st.session_state.company_context:
                extracted_name = st.session_state.company_context.split("\n")[0].replace("Company Name: ", "")
                scent_context = f"Scent locked onto {extracted_name}."
                
            st.session_state.messages = [{"role": "assistant", "content": f"{greeting}. Kitsune digital twin awake and operational. {scent_context} What trail are we tracking today?"}]

        # RIGID CHAT CONTAINER
        chat_container = st.container(height=500, border=True)

        with chat_container:
            for message in st.session_state.messages:
                avatar_icon = "🦊" if message["role"] == "assistant" else "🧑‍💻"
                with st.chat_message(message["role"], avatar=avatar_icon):
                    st.markdown(message["content"])

        user_input = st.chat_input("Input query here...")
        prompt_to_process = user_input or selected_prompt

        if prompt_to_process:
            fox_placeholder.markdown("<div style='text-align: center; font-size: 3.5rem; transition: 0.3s; transform: scale(1.1); text-shadow: 0 0 15px #FF7A00;'>🦊</div>", unsafe_allow_html=True)
            
            with chat_container:
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.markdown(prompt_to_process)
            st.session_state.messages.append({"role": "user", "content": prompt_to_process})

            with chat_container:
                with st.chat_message("assistant", avatar="🦊"):
                    with st.spinner("🦊 Kitsune Agent tracking query..."):
                        time.sleep(0.6) # Brief artificial delay for the tracking effect
                        try:
                            base_context = st.session_state.company_context
                            persona_instruction = "\n\nCRITICAL INSTRUCTION: Adopt a subtle, confident 'Cyber-Fox / Kitsune' AI persona. Be highly technical, but occasionally use brief agility/tracking metaphors. Always adapt your answers to prove fit for the injected company context if one exists."
                            current_context = base_context + persona_instruction

                            response = rag_chain.invoke({
                                "input": prompt_to_process, 
                                "company_context": current_context
                            })
                            bot_reply = response["answer"]
                        except Exception as e:
                            bot_reply = f"Error during inference: {e}"
                    
                    st.write_stream(stream_response(bot_reply))
                    
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            fox_placeholder.markdown("<div style='text-align: center; font-size: 3.5rem; transition: 0.3s;'>🦊💤</div>", unsafe_allow_html=True)

            if selected_prompt in st.session_state.quick_prompts:
                try:
                    llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7)
                    followup_instruction = (
                        "Based on the exchange, suggest exactly 1 short follow-up question the recruiter should ask next. "
                        "Keep it under 8 words."
                        f"\n\nRecruiter: {prompt_to_process}\nCandidate: {bot_reply}"
                    )
                    new_suggestion = llm_fast.invoke([HumanMessage(content=followup_instruction)]).content.strip().strip('"')
                    if new_suggestion:
                        clicked_index = st.session_state.quick_prompts.index(selected_prompt)
                        st.session_state.quick_prompts[clicked_index] = new_suggestion
                except Exception:
                    pass 
            
            st.rerun()

with tab_agent:
    st.markdown("### Agentic Operations")
    st.write("Inject a Job Description below to run autonomous candidate evaluations. The Kitsune Agent will use Mistral AI to map my core competencies directly to your requirements.")
    
    jd_input = st.text_area("Target Job Description", placeholder="Paste the full job description here...", height=200)
    
    col_act1, col_act2, col_act3 = st.columns(3)
    
    agent_action = None
    with col_act1:
        if st.button("Calculate Fit Score", use_container_width=True): agent_action = "Fit Score Analysis"
    with col_act2:
        if st.button("Draft Cover Letter", use_container_width=True): agent_action = "Cover Letter Generation"
    with col_act3:
        if st.button("Extract Interview Qs", use_container_width=True): agent_action = "Interview Question Extraction"

    if agent_action and not jd_input.strip():
        st.warning("Please paste a Job Description first.")
    
    elif agent_action and jd_input.strip():
        # Using a spinner removes the confusing clickable box entirely!
        with st.spinner(f"🦊 Kitsune executing agentic protocol: {agent_action}..."):
            try:
                resume_content = get_resume_text()
                llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.3)
                
                if agent_action == "Fit Score Analysis":
                    task_prompt = f"Act as an expert technical recruiter. Compare this candidate's resume to the provided Job Description. Give a definitive 'Fit Score' out of 100. Then provide 3 bullet points on 'Strongest Alignments' and 2 bullet points on 'Potential Gaps/Growth Areas'. Keep it concise and professional.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                elif agent_action == "Cover Letter Generation":
                    task_prompt = f"Write a highly tailored, compelling, and technical cover letter for Adem Ben Halima based on this Job Description. Use facts from his resume. Keep the tone confident, professional, and slightly futuristic (Cyber-Fox vibe). Limit to 3 paragraphs.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                elif agent_action == "Interview Question Extraction":
                    task_prompt = f"Based on the intersection of this candidate's resume and the Job Description, generate the 4 most critical technical interview questions the hiring manager should ask them to validate their fit. Provide a brief note on what a good answer from the candidate would look like.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"

                agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                
                # LINKING TO THE CHAT: This injects the operation directly into the chatbot's memory!
                simulated_user_prompt = f"System Command Executed: {agent_action} based on the provided Job Description."
                st.session_state.messages.append({"role": "user", "content": simulated_user_prompt})
                st.session_state.messages.append({"role": "assistant", "content": agent_response.content})
                
            except Exception as e:
                st.error(f"Execution Error: {e}")
                agent_response = None
        
        # This streams the result into an open, unmissable container inside the Agentic Tab
        if agent_response:
            st.markdown(f"#### {agent_action} Output:")
            output_container = st.container(border=True)
            with output_container:
                st.write_stream(stream_response(agent_response.content))