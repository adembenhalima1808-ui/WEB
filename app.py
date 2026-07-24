import streamlit as st

# Setup the main layout
st.set_page_config(page_title="AI Portfolio & Digital Twin", page_icon="🤖", layout="wide")

# --- KNOWLEDGE BASE (Your Digital Twin's Memory) ---
# Customize this section with your actual details!
CV_DATA = {
    "name": "Your Name",
    "location": "Cergy / Paris, Île-de-France",
    "education": "MSc / Degree in Computer Science / Data Science",
    "skills": ["Python", "Streamlit", "PyTorch", "Git", "FastAPI", "Docker", "RAG / LangChain"],
    "projects": [
        "AI Portfolio: Interactive Streamlit app hosted on GitHub.",
        "Computer Vision Defect Detection: Real-time object classification pipeline."
    ],
    "experience": "AI Developer specializing in building end-to-end Machine Learning systems and LLM applications."
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", [
    "🤖 RAG Digital Twin", 
    "📊 Data Architecture", 
    "👁️ Multimodal Vision", 
    "💼 Agentic Evaluator"
])

# --- 1. RAG DIGITAL TWIN PAGE ---
if page == "🤖 RAG Digital Twin":
    st.title("🤖 Self-Representational RAG Agent")
    st.write(f"Welcome! I am the digital twin of **{CV_DATA['name']}**. Ask me anything about my experience, projects, or background in tech!")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! Ask me about my skills, education, or projects in Île-de-France!"}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question (e.g., 'What are your top skills?' or 'Where are you located?'):"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Simple RAG retrieval logic (matching query against knowledge base)
        query = prompt.lower()
        if "skill" in query or "technology" in query or "tech" in query:
            response = f"My core technical skills include: {', '.join(CV_DATA['skills'])}."
        elif "project" in query or "work" in query or "build" in query:
            response = f"Here are my key projects:\n- " + "\n- ".join(CV_DATA['projects'])
        elif "education" in query or "study" in query or "university" in query:
            response = f"Education Background: {CV_DATA['education']}."
        elif "location" in query or "where" in query or "cergy" in query:
            response = f"I am based in {CV_DATA['location']}."
        else:
            response = f"I am trained on {CV_DATA['name']}'s background. You can ask me about education, technical skills, key projects, or location!"

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- OTHER PAGES ---
elif page == "📊 Data Architecture":
    st.title("📊 Data Pipeline & Architecture")
    st.write("Showcasing data lineage, cleaning processes, and deployment pipelines.")

elif page == "👁️ Multimodal Vision":
    st.title("👁️ Multimodal Vision Interface")
    st.write("Upload an image or model log for real-time inference.")

elif page == "💼 Agentic Evaluator":
    st.title("💼 Agentic Job Matching Evaluator")
    st.write("Paste a job description to calculate semantic match scores.")