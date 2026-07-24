import streamlit as st

# Setup the main layout
st.set_page_config(page_title="My AI Portfolio", page_icon="🚀", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.write("Explore my interactive AI projects.")
page = st.sidebar.radio("Go to:", [
    "Home - RAG Agent", 
    "Data Architecture", 
    "Multimodal Vision", 
    "Agentic Evaluator"
])

# --- MAIN PAGE CONTENT ---
if page == "Home - RAG Agent":
    st.title("🤖 My Self-Representational RAG Agent")
    st.write("Welcome to my interactive CV! Instead of reading a static document, ask my digital twin a question.")
    st.text_input("Ask about my experience, skills, or academic background:")
    st.button("Send")

elif page == "Data Architecture":
    st.title("📊 Data Pipeline & Engineering")
    st.write("Showcasing the 'hidden 90%' of AI: Data collection, cleaning, and deployment.")
    st.info("Deployment pipelines, Docker configurations, and Git history will be displayed here.")

elif page == "Multimodal Vision":
    st.title("👁️ Multimodal Interaction")
    st.write("Upload an image, dataset, or error code below for real-time inference.")
    st.file_uploader("Upload your file here:")

elif page == "Agentic Evaluator":
    st.title("💼 Agentic Hiring Evaluator")
    st.write("Paste your company's job description below. My agent will autonomously compute a semantic match score against my skills.")
    st.text_area("Paste Job Description:")
    st.button("Evaluate Match")