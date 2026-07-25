import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage

# Import the RAG Engine
from core.rag_engine import initialize_rag_system

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(page_title="AI Engineer | System Architecture", layout="wide")

# --- BRUTAL BUREAUCRATIC CHIC CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #121214; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    [data-testid="stSidebar"] { background-color: #0C0C0D; border-right: 1px solid #27272A; }
    .stButton>button {
        background-color: transparent; color: #FFFFFF; border: 1px solid #3F3F46;
        border-radius: 4px; font-weight: 500; letter-spacing: 0.5px;
        text-transform: uppercase; font-size: 0.8rem; transition: all 0.2s ease-in-out;
        height: 100%;
    }
    .stButton>button:hover { background-color: #3F3F46; border: 1px solid #FFFFFF; }
    
    /* Custom Metric Styling */
    [data-testid="stMetricValue"] { color: #00F0FF !important; font-weight: 400; font-size: 2rem; }
    [data-testid="stMetricLabel"] { color: #A1A1AA !important; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("# System Architecture & AI Portfolio")
st.markdown("**Role:** End-to-End AI & Machine Learning Engineer | **Location:** Cergy, Île-de-France")
st.write(
    "Welcome to my live digital portfolio. This environment acts as verifiable proof of my ability to navigate the full AI lifecycle, "
    "from data ingestion and vector orchestration to secure, enterprise-grade deployment."
)

st.divider()

# --- 1. GLOBAL CONTEXT INJECTION ---
st.markdown("### 1. Initialize Session Context")
st.write("Evaluating on behalf of a specific organization? Enter the name to dynamically align my digital twin to your tech stack and culture.")

with st.container(border=True):
    with st.form("company_context_form"):
        col_input, col_btn = st.columns([4, 1])
        
        with col_input:
            company_name = st.text_input(
                "Organization Name", 
                label_visibility="collapsed", 
                placeholder="e.g., L'Oréal, Datadog, Hugging Face (or leave blank for general)..."
            )
        with col_btn:
            submit_context = st.form_submit_button("Inject Context", use_container_width=True)

    if submit_context:
        if company_name.strip():
            with st.spinner(f"Agent actively scraping web data for {company_name}..."):
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                    query = urllib.parse.quote(f"{company_name} company overview and tech stack")
                    url = f"https://html.duckduckgo.com/html/?q={query}"
                    
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    snippets = [a.text for a in soup.find_all('a', class_='result__snippet')]
                    company_info = " ".join(snippets[:3])
                    
                    if not company_info:
                        company_info = "Could not scrape detailed architectural context. Falling back to general industry alignment."

                    st.session_state.company_context = f"Company Name: {company_name}\nBackground: {company_info}"
                    st.success(f"Context injected. The digital twin will now frame my experience specifically for {company_name}.")
                except Exception as e:
                    st.error(f"Custom scraping pipeline failed. Error: {e}")
        else:
            st.session_state.company_context = "General public evaluation. No specific company context."
            st.info("Reset to general evaluation mode.")

st.divider()

# --- 2. LIVE RAG INTERFACE ---
st.markdown("### 2. Direct Interrogation Interface")
st.write("Chat directly with my Mistral-powered digital twin below.")

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

# Render the dynamic buttons from session state
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
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "RAG system operational. Interrogate me about my skills or professional history."}]

    # --- THE FIXED-HEIGHT CHAT CONTAINER ---
    # This locks the chat window to 500px tall with an internal scrollbar
    chat_container = st.container(height=500, border=True)

    # Render previous messages INSIDE the scrollable container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat Input Logic
    user_input = st.chat_input("Input professional query here...")
    prompt_to_process = user_input or selected_prompt

    if prompt_to_process:
        # 1. Display user prompt inside the container immediately
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_to_process)
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

        # 2. Generate and display Assistant Answer inside the container
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Processing through neural chain..."):
                    try:
                        current_context = st.session_state.get("company_context", "General public evaluation.")
                        response = rag_chain.invoke({
                            "input": prompt_to_process, 
                            "company_context": current_context
                        })
                        bot_reply = response["answer"]
                    except Exception as e:
                        bot_reply = f"Error during inference: {e}"
                
                st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # 4. Targeted Background Generation (Only replace the USED chip)
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
        
        # 5. Instantly rerun the app to reset the input and auto-scroll the container to the bottom
        st.rerun()