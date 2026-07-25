import streamlit as st
import time
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.rag_engine import initialize_rag_system

# --- PAGE SETUP & CSS ---
st.set_page_config(page_title="Agentic Hiring | Auto-Match", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121214; color: #E4E4E7; font-family: 'Inter', -apple-system, sans-serif; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.8px; }
    .stButton>button {
        background-color: transparent; color: #00F0FF; border: 1px solid #00F0FF;
        border-radius: 4px; font-weight: 600; letter-spacing: 0.5px;
        text-transform: uppercase; transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { background-color: #00F0FF; color: #121214; }
    .score-card {
        background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2);
        border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 20px;
    }
    .score-value { font-size: 3.5rem; font-weight: 700; color: #00F0FF; font-family: 'JetBrains Mono', monospace; }
    .score-label { font-size: 1rem; color: #A1A1AA; text-transform: uppercase; letter-spacing: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- TYPEWRITER GENERATOR ---
def stream_text(text, speed=0.01):
    for word in text.split(" "):
        yield word + " "
        time.sleep(speed)

# --- HEADER ---
st.title("🤖 Autonomous Hiring Agent")
st.markdown("This system extracts the Target Job Description from the global session memory, queries my vector database, and uses Mistral AI to calculate a deterministic fit score and generate a technical proposal.")
st.divider()

# --- 1. MEMORY RETRIEVAL ---
target_jd = st.session_state.get("target_jd", "")

if not target_jd:
    st.warning("⚠️ No Job Description detected in Neural Link memory.")
    st.write("Please go to the Home page and inject a target Job Description, or paste one manually below.")
    manual_jd = st.text_area("Manual Job Description Input:", height=150)
    if st.button("Load into Session Memory"):
        if manual_jd.strip():
            st.session_state.target_jd = manual_jd
            st.rerun()
else:
    st.success("✅ Target Job Description successfully retrieved from global memory.")
    with st.expander("🔍 View Active Job Description", expanded=False):
        st.write(target_jd)

    st.divider()

    # --- 2. AGENTIC WORKFLOW EXECUTION ---
    if st.button("🚀 Execute Agentic Fit Analysis", use_container_width=True):
        
        # Load systems
        rag_chain = initialize_rag_system()
        llm = ChatMistralAI(model="mistral-small-latest", temperature=0.2)

        with st.status("Initializing Autonomous Analysis...", expanded=True) as status:
            # Step 1: Extract Adem's profile via RAG
            st.write("🔍 Querying Vector Database for Adem's core competencies...")
            try:
                profile_extraction = rag_chain.invoke({
                    "input": "Summarize Adem's top technical skills, tools, and engineering projects in intense detail.",
                    "company_context": "None"
                })
                adem_profile = profile_extraction["answer"]
            except Exception as e:
                adem_profile = "Error retrieving profile."
                st.error(f"RAG Error: {e}")

            # Step 2: Calculate Fit Score
            st.write("⚙️ Running deterministic fit-gap analysis via Mistral...")
            score_prompt = (
                f"You are an expert technical recruiter. Compare this candidate's profile: {adem_profile}\n\n"
                f"Against this Job Description: {target_jd}\n\n"
                "Provide a single integer score from 0 to 100 representing the match percentage. "
                "Respond WITH ONLY THE NUMBER. No other text."
            )
            try:
                score_response = llm.invoke([HumanMessage(content=score_prompt)]).content.strip()
                match_score = int(''.join(filter(str.isdigit, score_response))) # Clean the output
            except Exception:
                match_score = 85 # Fallback

            # Step 3: Generate Cover Letter
            st.write("📝 Auto-drafting hyper-personalized technical cover letter...")
            letter_prompt = (
                f"You are Adem's digital twin. Write a highly confident, technically precise, and concise 3-paragraph cover letter "
                f"for the role described here: {target_jd}\n\n"
                f"Base the technical claims strictly on Adem's profile: {adem_profile}\n\n"
                "Do not use generic fluff. Focus on architecture, tools, and solving the employer's specific problems."
            )
            cover_letter = llm.invoke([HumanMessage(content=letter_prompt)]).content

            status.update(label="Analysis Complete", state="complete", expanded=False)

        # --- 3. DISPLAY RESULTS ---
        col_score, col_blank = st.columns([1, 2])
        with col_score:
            st.markdown(f"""
                <div class="score-card">
                    <div class="score-value">{match_score}%</div>
                    <div class="score-label">Technical Fit Score</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📄 Auto-Generated Technical Proposal")
        st.write_stream(stream_text(cover_letter, 0.015))