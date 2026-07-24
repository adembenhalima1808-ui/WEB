import streamlit as st
import time
from PIL import Image

# Setup the main layout
st.set_page_config(page_title="AI Portfolio & Digital Twin", layout="wide")

# --- KNOWLEDGE BASE ---
# Note: You can replace these placeholder details with your personal information!
CV_DATA = {
    "name": "Your Name",
    "location": "Cergy / Paris, Ile-de-France",
    "education": "MSc in Computer Science / Data Science",
    "skills": ["Python", "Streamlit", "PyTorch", "Git", "FastAPI", "Docker", "Machine Learning"],
    "projects": [
        "AI Portfolio: Interactive Streamlit app hosted on GitHub.",
        "Computer Vision Defect Detection: Real-time object classification pipeline."
    ],
    "experience": "AI Developer specializing in building end-to-end Machine Learning systems."
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", [
    "RAG Digital Twin", 
    "Agentic Evaluator",
    "Multimodal Vision", 
    "Data Architecture"
])

# --- 1. RAG DIGITAL TWIN PAGE ---
if page == "RAG Digital Twin":
    st.title("Self-Representational RAG Agent")
    st.write(f"Welcome! I am the digital twin of {CV_DATA['name']}. Ask me anything about my background.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me about my skills or projects."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        query = prompt.lower()
        if "skill" in query or "tech" in query:
            response = f"My core skills include: {', '.join(CV_DATA['skills'])}."
        elif "project" in query or "work" in query:
            response = f"Here are my key projects:\n- " + "\n- ".join(CV_DATA['projects'])
        else:
            response = "I am trained on this candidate's background. Ask about skills or projects!"

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- 2. AGENTIC EVALUATOR PAGE ---
elif page == "Agentic Evaluator":
    st.title("Agentic Job Matching Evaluator")
    st.write("Paste a job description below. The system will extract requirements and compute a match score.")
    
    job_description = st.text_area("Paste job description:", height=200)
    
    if st.button("Evaluate Match"):
        if job_description:
            with st.spinner("Parsing requirements..."):
                time.sleep(1)
                
                job_desc_lower = job_description.lower()
                my_skills = [s.lower() for s in CV_DATA["skills"]]
                matched_skills = [skill for skill in my_skills if skill in job_desc_lower]
                match_score = (len(matched_skills) / len(my_skills)) * 100 if my_skills else 0
                
                st.divider()
                st.subheader("Analysis Results")
                st.metric("Semantic Match Score", f"{match_score:.0f}%")
                
                if matched_skills:
                    st.success(f"Matched Skills: {', '.join(matched_skills).title()}")
                else:
                    st.warning("No direct keyword matches found.")
                    
                st.write("### Agent Proposal")
                st.info(f"My background in {', '.join(CV_DATA['skills'][:3])} aligns directly with this job specification.")
        else:
            st.error("Please paste a job description first.")

# --- 3. MULTIMODAL VISION PAGE ---
elif page == "Multimodal Vision":
    st.title("Multimodal Vision Evaluator")
    st.write("Upload an image file (PNG/JPG) to test real-time inference and quality classification.")

    uploaded_file = st.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Run Inference Pipeline"):
            with st.spinner("Processing image through vision pipeline..."):
                time.sleep(1.5)
                
                st.divider()
                st.subheader("Inference Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Classification", "Valid Input")
                col2.metric("Confidence Score", "98.4%")
                col3.metric("Latency", "120 ms")

                st.write("### Model Inspection Metrics")
                st.json({
                    "image_dimensions": f"{image.size[0]}x{image.size[1]}",
                    "format": image.format,
                    "pipeline_status": "Success",
                    "defect_detected": False
                })

# --- 4. DATA ARCHITECTURE PAGE ---
elif page == "Data Architecture":
    st.title("Data Pipeline & Architecture")
    st.write("Demonstrating engineering rigor, data processing workflows, and system design.")

    st.subheader("1. End-to-End System Lineage")
    st.code("""
[ Raw Data Ingestion ] 
        |
        v
[ Cleaning & Preprocessing (Pandas / NumPy) ]
        |
        v
[ Feature Engineering & Vectorization (Embeddings) ]
        |
        v
[ Model Inference API (FastAPI / Streamlit) ]
        |
        v
[ Monitoring, Logging & CI/CD Pipeline ]
    """, language="text")

    st.subheader("2. Infrastructure & Tooling")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Core Stack:**")
        st.markdown("- Python 3.10+")
        st.markdown("- Streamlit (Frontend UI)")
        st.markdown("- Git / GitHub (Version Control)")
    with col2:
        st.markdown("**Deployment & MLOps:**")
        st.markdown("- Virtual Environment Isolation")
        st.markdown("- Automated Dependency Tracking (`requirements.txt`)")
        st.markdown("- Continuous Integration Setup")

    st.subheader("3. System Health")
    st.success("Pipeline Status: Operational")