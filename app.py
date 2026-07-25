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

# --- AUTONOMOUS CV SCANNER (CACHED) ---
@st.cache_data(show_spinner=False)
def extract_skills_from_resume():
    try:
        loader = PyPDFLoader("resume.pdf")
        docs = loader.load()
        resume_text = " ".join([page.page_content for page in docs])
        
        # Upgraded to Mistral Medium for strict JSON compliance and deep semantic extraction
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
    .stApp { background-color: #100C0A; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    
    /* Ambient Fox-Fire Glow */
    .stApp::before {
        content: "";
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(255, 122, 0, 0.04), transparent 60%);
        animation: rotateGlow 20s linear infinite;
        z-index: -1;
        pointer-events: none;
    }
    @keyframes rotateGlow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Floating Fox-Fire Embers */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 200%;
        background-image: radial-gradient(circle, #FF7A00 1.5px, transparent 1.5px),
                          radial-gradient(circle, #FF7A00 1px, transparent 1px);
        background-size: 80px 80px;
        background-position: 0 0, 40px 40px;
        opacity: 0.15;
        animation: risingEmbers 25s linear infinite;
        z-index: -1;
        pointer-events: none;
    }
    @keyframes risingEmbers {
        0% { transform: translateY(0); }
        100% { transform: translateY(-50%); }
    }

    /* Neon Flicker on Main Headers */
    h1 {
        color: #FFFFFF !important;
        font-weight: 300 !important;
        letter-spacing: -0.8px;
        text-shadow: 0 0 5px rgba(255, 122, 0, 0.2), 0 0 15px rgba(255, 122, 0, 0.1);
        animation: neonFlicker 4s infinite alternate;
    }
    @keyframes neonFlicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            opacity: 1;
            text-shadow: 0 0 5px rgba(255, 122, 0, 0.3), 0 0 15px rgba(255, 122, 0, 0.1);
        }
        20%, 22%, 24%, 55% {
            opacity: 0.8;
            text-shadow: none;
        }
    }
    
    h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    [data-testid="stSidebar"] { background-color: #0A0807; border-right: 1px solid #271A12; }
    
    /* Neon Fox Buttons */
    .stButton>button {
        background-color: transparent; color: #FFFFFF; border: 1px solid #3F2314;
        border-radius: 4px; font-weight: 500; letter-spacing: 0.5px;
        text-transform: uppercase; font-size: 0.8rem; transition: all 0.2s ease-in-out;
        height: 100%;
    }
    .stButton>button:hover { background-color: #3F2314; border: 1px solid #FF7A00; color: #FF7A00; }
    
    /* Tech Stack Badges */
    .badge {
        display: inline-block; background: rgba(255, 122, 0, 0.05); color: #E4E4E7;
        border: 1px solid #3F2314; padding: 4px 10px; border-radius: 4px;
        font-size: 0.75rem; font-weight: 500; margin-right: 6px; margin-bottom: 8px;
    }
    
    /* Glassmorphism Metric Cards with Staggered Entrance */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 122, 0, 0.08);
        border-radius: 8px;
        padding: 14px 18px;
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
        opacity: 0;
        animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(255, 122, 0, 0.15);
        border: 1px solid rgba(255, 122, 0, 0.3);
    }
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    /* Stagger the delays for columns 1, 2, and 3 */
    div[data-testid="column"]:nth-child(1) .metric-card { animation-delay: 0.1s; }
    div[data-testid="column"]:nth-child(2) .metric-card { animation-delay: 0.25s; }
    div[data-testid="column"]:nth-child(3) .metric-card { animation-delay: 0.4s; }

    .metric-value {
        color: #FF7A00;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4rem;
        font-weight: 600;
    }
    .metric-label {
        color: #A1A1AA;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Glowing Ember Pulse Dot */
    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #FF7A00;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(255, 122, 0, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 122, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(255, 122, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 122, 0, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("## 🦊 Adem Ben Halima")
    st.caption("AI & Machine Learning Engineer")
    
    # Styled Status Card with Glowing Ember Pulse Dot
    st.markdown("""
        <div style="margin-bottom: 15px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 4px; border: 1px solid #271A12;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span class="pulse-dot"></span>
                <span style="font-size: 0.9rem; color: #F8FAFC; font-weight: 600;">Kitsune Agent Awake</span>
            </div>
            <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Cergy, Île-de-France</span>
        </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Button
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
    
    # Dynamic Fox Easter Egg (Using a real-time placeholder)
    fox_placeholder = st.empty()
    fox_placeholder.markdown("<div style='text-align: center; font-size: 3.5rem; transition: 0.3s;'>🦊💤</div>", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("# Cyber-Kitsune Architecture")
st.markdown("**Role:** End-to-End AI & Machine Learning Engineer | **Location:** Cergy, Île-de-France")
st.write(
    "Welcome to my digital den. This living portfolio serves as verifiable proof of my ability to build agile, intelligent, "
    "and highly optimized AI pipelines from raw data to secure enterprise deployment."
)

# --- INTERACTIVE PLOTLY RADAR CHART (FOX EDITION) ---
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
    angularaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color="#A1A1AA", size=12))
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

# --- 1. GLOBAL CONTEXT INJECTION & JOB SPEC STEERING ---
st.markdown("### 1. Initialize Scent & Target Role")
st.write("Inject your company name or target Job Description. My digital twin will actively track the requirements and steer its answers to demonstrate my specific fit.")

with st.container(border=True):
    col_comp, col_jd = st.columns(2)
    
    with col_comp:
        company_name = st.text_input("Organization Name", placeholder="e.g., Datadog, Hugging Face...", label_visibility="collapsed")
        submit_company = st.button("Inject Company Context", use_container_width=True)
        
    with col_jd:
        job_description = st.text_area("Paste Target Job Description", placeholder="Paste the core requirements here...", height=68, label_visibility="collapsed")
        submit_jd = st.button("Activate Agentic Steering", use_container_width=True)

    if submit_company and company_name.strip():
        with st.spinner(f"Agent actively tracking web data for {company_name}..."):
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                query = urllib.parse.quote(f"{company_name} company overview tech stack")
                url = f"https://html.duckduckgo.com/html/?q={query}"
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                st.session_state.company_context = f"Company Name: {company_name}\nBackground: {' '.join(snippets[:3])}"
                st.toast(f"Scent locked onto {company_name}", icon="🔥")
            except Exception:
                st.error("Tracking failed.")
                    
    if submit_jd and job_description.strip():
        st.session_state.target_jd = job_description
        st.toast("Agentic Steering Activated. I will adapt my profile to this trail.", icon="🎯")
        with st.status("🦊 Kitsune analyzing Job Description...", expanded=True) as jd_status:
            time.sleep(0.5)
            st.write("🐾 Extracting key technical requirements...")
            time.sleep(0.5)
            st.write("🔥 Mapping requirements to vector memory...")
            jd_status.update(label="Role alignment established. Ready to hunt.", state="complete", expanded=False)

st.divider()

# --- 2. LIVE RAG INTERFACE ---
st.markdown("### 2. Direct Interrogation Interface")

if "quick_prompts" not in st.session_state:
    st.session_state.quick_prompts = [
        "What are your core AI skills?",
        "What architectures have you built?",
        "Why should we hire you?"
    ]

st.markdown("**⚡ Suggested Trails to Follow:**")
chip_col1, chip_col2, chip_col3 = st.columns(3)
selected_prompt = None

with chip_col1:
    if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="btn1"): selected_prompt = st.session_state.quick_prompts[0]
with chip_col2:
    if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="btn2"): selected_prompt = st.session_state.quick_prompts[1]
with chip_col3:
    if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="btn3"): selected_prompt = st.session_state.quick_prompts[2]

st.divider()

rag_chain = initialize_rag_system()

if isinstance(rag_chain, str) and "Failed" in rag_chain:
    st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
else:
    # --- TIME-AWARE KITSUNE GREETING ---
    if "messages" not in st.session_state:
        current_hour = datetime.datetime.now().hour
        greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
        st.session_state.messages = [{"role": "assistant", "content": f"{greeting}. Kitsune digital twin awake and operational. What trail are we tracking today?"}]

    # Chat Container
    chat_container = st.container(height=500, border=True)

    with chat_container:
        for message in st.session_state.messages:
            # Set Custom Avatars: 🦊 for assistant, 🧑‍💻 for user
            avatar_icon = "🦊" if message["role"] == "assistant" else "🧑‍💻"
            with st.chat_message(message["role"], avatar=avatar_icon):
                st.markdown(message["content"])

    user_input = st.chat_input("Input query here...")
    prompt_to_process = user_input or selected_prompt

    if prompt_to_process:
        # Instantly push the awake animation to the sidebar!
        fox_placeholder.markdown("<div style='text-align: center; font-size: 3.5rem; transition: 0.3s; transform: scale(1.1); text-shadow: 0 0 15px #FF7A00;'>🦊🔥</div>", unsafe_allow_html=True)
        
        with chat_container:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt_to_process)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

        with chat_container:
            with st.chat_message("assistant", avatar="🦊"):
                # --- KINETIC PAW PRINT LOADING SEQUENCE ---
                with st.status("🦊 Kitsune Agent tracking query...", expanded=True) as status:
                    st.write("🐾 Catching the scent of the query in ChromaDB...")
                    time.sleep(0.3)
                    st.write("🌲 Navigating the vector forest...")
                    time.sleep(0.3)
                    st.write("⚡ Pouncing on the optimal context blocks...")
                    
                    try:
                        base_context = st.session_state.get("company_context", "General public evaluation.")
                        target_jd = st.session_state.get("target_jd", "")
                        
                        # Persona instruction injection
                        persona_instruction = "\n\nCRITICAL INSTRUCTION: Adopt a subtle, confident 'Cyber-Fox / Kitsune' AI persona. Be highly technical, but occasionally use brief agility/tracking metaphors. "
                        
                        if target_jd:
                            steering = f"The user is hiring for: '{target_jd}'. Actively connect Adem's skills from the vector db directly to this job to prove he is the perfect fit."
                            current_context = base_context + persona_instruction + steering
                        else:
                            current_context = base_context + persona_instruction

                        response = rag_chain.invoke({
                            "input": prompt_to_process, 
                            "company_context": current_context
                        })
                        bot_reply = response["answer"]
                        status.update(label="Target Acquired Successfully", state="complete", expanded=False)
                    except Exception as e:
                        bot_reply = f"Error during inference: {e}"
                        status.update(label="Trail Lost (Pipeline Failure)", state="error")
                
                st.write_stream(stream_response(bot_reply))
                
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        # Put the fox back to sleep after answering
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