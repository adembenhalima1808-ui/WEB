import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(page_title="AI Engineer & Architect Portfolio", layout="wide")

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
    }
    .stButton>button:hover { background-color: #3F3F46; border: 1px solid #FFFFFF; }
    </style>
""", unsafe_allow_html=True)

# Main Landing Page Content
st.markdown("# System Architecture Overview")
st.markdown("Welcome to my technical portfolio. Please select a module from the sidebar to review my capabilities.")

st.divider()
st.markdown("### Active Microservices")
col1, col2 = st.columns(2)
with col1:
    st.info("**Digital Twin:** RAG-enabled background synthesis.")
    st.info("**Agentic Hiring:** Autonomous job description evaluation.")
with col2:
    st.info("**Multimodal Vision:** Real-time unstructured data inference.")
    st.info("**Data Architecture:** Pipeline visualization and telemetry.")