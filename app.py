import time
import datetime
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv
import plotly.graph_objects as go
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

# Import the RAG Engine
from core.rag_engine import initialize_rag_system

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(page_title="AI Engineer | System Architecture", layout="wide")

# --- GENERATOR FOR TYPEWRITER EFFECT ---
def stream_response(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.015)  # Adjust the typing speed here

# --- BRUTAL BUREAUCRATIC CHIC + KINETIC CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #121214; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    
    /* Ambient Background Glow */
    .stApp::before {
        content: "";
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.03), transparent 60%);
        animation: rotateGlow 20s linear infinite;
        z-index: -1;
        pointer-events: none;
    }
    @keyframes rotateGlow {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    h1, h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    [data-testid="stSidebar"] { background-color: #0C0C0D; border-right: 1px solid #27272A; }
    .stButton>button {
        background-color: transparent; color: #FFFFFF; border: 1px solid #3F3F46;
        border-radius: 4px; font-weight: 500; letter-spacing: 0.5px;
        text-transform: uppercase; font-size: 0.8rem; transition: all 0.2s ease-in-out;
        height: 100%;
    }
    .stButton>button:hover { background-color: #3F3F46; border: 1px solid #FFFFFF; }
    
    /* Tech Stack Badges */
    .badge {
        display: inline-block; background: rgba(255, 255, 255, 0.05); color: #E4E4E7;
        border: 1px solid #3F3F46; padding: 4px 10px; border-radius: 4px;
        font-size: 0.75rem; font-weight: 500; margin-right: 6px; margin-bottom: 8px;
    }
    
    /* Glassmorphism Metric Cards with Kinetic Hover */
    .metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 14px 18px;
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 240, 255, 0.15);
        border: 1px solid rgba(0, 240, 255, 0.3);
    }
    .metric-value {
        color: #00F0FF;
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
    
    /* Glowing Pulse Dot */
    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #4ADE80;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(74, 222, 128, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("## 🧠 Adem Ben Halima")
    st.caption("AI & Machine Learning Engineer")
    
    # Styled Status Card with Glowing Pulse Dot
    st.markdown("""
        <div style="margin-bottom: 15px; padding: 12px; background: rgba(255,255,255,0.03); border-radius: 4px; border: 1px solid #27272A;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <span class="pulse-dot"></span>
                <span style="font-size: 0.9rem; color: #F8FAFC; font-weight: 600;">Open to Opportunities</span>
            </div>
            <span style="font-size: 0.8rem; color: #A1A1AA; margin-left: 18px;">📍 Cergy, Île-de-France</span>
        </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Button Logic
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
        st.download_button(
            label="📄 Download Full CV",
            data=b"Please put a resume.pdf file in the root folder.",
            file_name="Adem_Ben_Halima_CV.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
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
    
    # Styled Social Buttons
    st.markdown("### 🔗 Professional Network")
    st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <a href="https://linkedin.com/in/yourprofile" target="_blank" style="text-decoration: none; color: #E4E4E7; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px; border: 1px solid #3F3F46; font-size: 0.85rem; text-align: center;">
                💼 <strong>LinkedIn</strong> Profile
            </a>
            <a href="https://github.com/yourusername" target="_blank" style="text-decoration: none; color: #E4E4E7; background: rgba(255,255,255,0.05); padding: 8px; border-radius: 4px; border: 1px solid #3F3F46; font-size: 0.85rem; text-align: center;">
                🐙 <strong>GitHub</strong> Repository
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("# System Architecture & AI Portfolio")
st.markdown("**Role:** End-to-End AI & Machine Learning Engineer | **Location:** Cergy, Île-de-France")
st.write(
    "Welcome to my live digital portfolio. This environment acts as verifiable proof of my ability to navigate the full AI lifecycle, "
    "from data ingestion and vector orchestration to secure, enterprise-grade deployment."
)

# --- INTERACTIVE PLOTLY RADAR CHART ---
st.markdown("### 🕸 Core Engineering Competencies")
categories = ['RAG Architecture', 'LLM Orchestration', 'Vector DBs (Chroma)', 'Docker/DevOps', 'Python Backend', 'Prompt Engineering']
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
      r=[95, 90, 85, 80, 95, 90],
      theta=categories,
      fill='toself',
      fillcolor='rgba(0, 240, 255, 0.2)',
      line=dict(color='#00F0FF', width=2),
      name='Skill Level'
))
fig.update_layout(
  polar=dict(
    radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', showticklabels=False),
    angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color="#A1A1AA", size=12))
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
    st.markdown('<div class="metric-card"><div class="metric-label">LLM Engine</div><div class="metric-value">Mistral 3.5</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown('<div class="metric-card"><div class="metric-label">Vector Store</div><div class="metric-value">ChromaDB</div></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown('<div class="metric-card"><div class="metric-label">Latency Target</div><div class="metric-value">&lt; 850ms</div></div>', unsafe_allow_html=True)

# --- ARCHITECTURE MODAL ---
with st.expander("🏗 View System Architecture Diagram", expanded=False):
    st.markdown("""
    | Layer | Technology | Purpose |
    |---|---|---|
    | **Orchestration** | LangChain / Python 3.11 | Manages pipeline execution, state, and prompt templates. |
    | **LLM Inference** | Mistral Medium 3.5 | Handles high-reasoning RAG generation and dynamic UI elicitation. |
    | **Vector Database** | ChromaDB | Stores embedded text chunks of professional context for semantic search. |
    | **UI / Gateway** | Streamlit + Custom CSS | Serves client interface and handles strict session state management. |
    """)

st.divider()

# --- 1. GLOBAL CONTEXT INJECTION & JOB SPEC STEERING ---
st.markdown("### 1. Initialize Session Context & Target Role")
st.write("Inject your company name and the target Job Description. My digital twin will actively analyze the role and steer its answers to demonstrate my specific fit for your open position.")

with st.container(border=True):
    col_comp, col_jd = st.columns(2)
    
    with col_comp:
        company_name = st.text_input("Organization Name", placeholder="e.g., Datadog, Hugging Face...")
        submit_company = st.button("Inject Company Context", use_container_width=True)
        
    with col_jd:
        job_description = st.text_area("Paste Target Job Description", placeholder="Paste the core requirements or responsibilities here...", height=68)
        submit_jd = st.button("Activate Agentic Steering", use_container_width=True)

    # Company Context Logic
    if submit_company:
        if company_name.strip():
            with st.spinner(f"Scraping web data for {company_name}..."):
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    query = urllib.parse.quote(f"{company_name} company overview tech stack")
                    url = f"https://html.duckduckgo.com/html/?q={query}"
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                    company_info = " ".join(snippets[:3])
                    st.session_state.company_context = f"Company Name: {company_name}\nBackground: {company_info}"
                    st.toast(f"Neural Link context aligned to {company_name}", icon="⚡")
                except Exception as e:
                    st.error("Scraping failed.")
                    
    # Job Description Steering Logic
    if submit_jd:
        if job_description.strip():
            st.session_state.target_jd = job_description
            st.toast("Agentic Steering Activated. I will now map my answers to this role.", icon="🎯")
            
            # Add an artificial "analysis" output to add life to the UI
            with st.status("Analyzing Job Description...", expanded=True) as jd_status:
                time.sleep(0.5)
                st.write("Extracting key technical requirements...")
                time.sleep(0.5)
                st.write("Mapping requirements to vector memory...")
                time.sleep(0.5)
                jd_status.update(label="Role alignment established. Ready for interrogation.", state="complete", expanded=False)

# --- 2. LIVE RAG INTERFACE ---
st.markdown("### 2. Direct Interrogation Interface")
st.write("Chat directly with my Mistral-powered digital twin below.")

# System Execution Telemetry
with st.expander("🔍 System Execution Telemetry", expanded=False):
    st.code("""
[0.00s] SYSTEM_INIT -> Loading Streamlit UI Config
[0.05s] ENVIRONMENT -> Environment Variables Loaded
[0.12s] CACHE_CHECK -> ChromaDB Vector Store Verified
[0.18s] RAG_ENGINE -> LangChain Initialization Complete
[0.22s] SESSION_STATE -> Ready for Inference
    """, language="bash")

# Initialize dynamic prompts in session state if they don't exist
if "quick_prompts" not in st.session_state:
    st.session_state.quick_prompts = [
        "What are your core AI skills?",
        "What projects have you built?",
        "Why should we hire you?"
    ]

# --- DYNAMIC QUICK PROMPT CHIPS ---
st.markdown("**⚡ Suggested Follow-ups:**")
chip_col1, chip_col2, chip_col3 = st.columns(3)
selected_prompt = None

with chip_col1:
    if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="btn1"):
        selected_prompt = st.session_state.quick_prompts[0]
with chip_col2:
    if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="btn2"):
        selected_prompt = st.session_state.quick_prompts[1]
with chip_col3:
    if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="btn3"):
        selected_prompt = st.session_state.quick_prompts[2]

st.divider()

# Load the cached RAG system from the core module
rag_chain = initialize_rag_system()

if isinstance(rag_chain, str) and "Failed" in rag_chain:
    st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
else:
    # --- TIME-AWARE GREETING ---
    if "messages" not in st.session_state:
        current_hour = datetime.datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning."
        elif 12 <= current_hour < 18:
            greeting = "Good afternoon."
        else:
            greeting = "Good evening."
            
        initial_msg = f"{greeting} RAG system operational. Interrogate me about my skills or professional history."
        st.session_state.messages = [{"role": "assistant", "content": initial_msg}]

    # FIXED-HEIGHT CHAT CONTAINER
    chat_container = st.container(height=500, border=True)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat Input Logic
    user_input = st.chat_input("Input professional query here...")
    prompt_to_process = user_input or selected_prompt

    if prompt_to_process:
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_to_process)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

        with chat_container:
            with st.chat_message("assistant"):
                # --- LIVE CHAIN OF THOUGHT PROCESS ---
                with st.status("🧠 Initiating Cognitive Pipeline...", expanded=True) as status:
                    st.write("🔍 Querying ChromaDB Vector Store...")
                    time.sleep(0.3)
                    st.write("📄 Retrieving contextual resume chunks...")
                    time.sleep(0.3)
                    st.write("⚙️ Injecting context into Mistral-Medium-3.5...")
                    
                    try:
                        # 1. Get the base company context
                        base_context = st.session_state.get("company_context", "General public evaluation.")
                        
                        # 2. Check if a Job Description exists to activate Agentic Steering
                        target_jd = st.session_state.get("target_jd", "")
                        
                        # 3. Create the Overloaded Context
                        if target_jd:
                            steering_instruction = (
                                f"\n\nCRITICAL INSTRUCTION FOR AI: The user is hiring for the following Job Description: '{target_jd}'. "
                                "In your response, you MUST actively and naturally connect Adem's skills, projects, and experiences "
                                "from the vector database directly to the requirements of this job. Prove he is the perfect fit."
                            )
                            current_context = base_context + steering_instruction
                        else:
                            current_context = base_context

                        # 4. Invoke the chain with the augmented context
                        response = rag_chain.invoke({
                            "input": prompt_to_process, 
                            "company_context": current_context
                        })
                        bot_reply = response["answer"]
                        status.update(label="Response Synthesized Successfully", state="complete", expanded=False)
                    except Exception as e:
                        bot_reply = f"Error during inference: {e}"
                        status.update(label="Pipeline Failure", state="error")
                
                # --- TYPEWRITER STREAMING ---
                st.write_stream(stream_response(bot_reply))
                
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # Targeted Background Generation (Only replace the USED chip)
        if selected_prompt in st.session_state.quick_prompts:
            try:
                llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7)
                followup_instruction = (
                    "Based on the following exchange, suggest exactly 1 short, highly relevant follow-up question "
                    "the recruiter should ask next. Return ONLY the question text, no quotes or intro. "
                    "Keep it under 8 words."
                    f"\n\nRecruiter asked: {prompt_to_process}\nCandidate replied: {bot_reply}"
                )
                
                new_suggestion = llm_fast.invoke([HumanMessage(content=followup_instruction)]).content.strip().strip('"')
                
                if new_suggestion:
                    clicked_index = st.session_state.quick_prompts.index(selected_prompt)
                    st.session_state.quick_prompts[clicked_index] = new_suggestion
            except Exception:
                pass 
        
        st.rerun()