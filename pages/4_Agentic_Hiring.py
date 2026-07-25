import streamlit as st
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables (API Keys)
load_dotenv()

# --- UI HEADER ---
st.markdown("# Agentic Hiring Evaluator")
st.markdown(
    "Paste an open job description below. The autonomous agent will extract core requirements, "
    "cross-reference my repository, and generate a customized matching proposal and 90-day onboarding strategy."
)

# --- LOAD CANDIDATE CONTEXT ---
@st.cache_data
def load_candidate_context():
    """Loads the candidate's professional background into memory."""
    try:
        with open("my_brain.txt", "r") as file:
            return file.read()
    except Exception as e:
        return f"Error loading context: {e}"

candidate_context = load_candidate_context()

# --- INPUT MODULE ---
with st.container(border=True):
    job_desc = st.text_area(
        "Paste the Job Description here:", 
        height=250, 
        placeholder="e.g., We are looking for a Senior AI Engineer with experience in LangChain, Python, and Docker to deploy end-to-end machine learning pipelines..."
    )
    
    initialize_btn = st.button("Initialize Agentic Chain", use_container_width=True)

# --- AGENTIC PIPELINE ---
if initialize_btn:
    if job_desc.strip():
        with st.spinner("Agent initializing tools, extracting keywords, and cross-referencing context..."):
            try:
                # Pull the specific Medium key from your environment vault
                medium_key = os.getenv("MISTRAL_MEDIUM_KEY")

                # Initialize Mistral Medium 3.5 using the dedicated key
                llm = ChatMistralAI(
                    model="mistral-medium-3-5", 
                    temperature=0.1,
                    mistral_api_key=medium_key  # Explicitly overriding the default key
                )
                
                # Define the Agentic Prompt
                agent_prompt = ChatPromptTemplate.from_messages([
                    ("system", (
                        "You are an elite AI technical recruiter and strategic onboarding agent. "
                        "Your objective is to evaluate a candidate based on their professional context and match it against a provided job description. "
                        "\n\nCandidate Context:\n{context}\n\n"
                        "Instructions:\n"
                        "1. Keyword Extraction: Extract the top 5 technical and soft skill keywords from the Job Description.\n"
                        "2. Match Proposal: Write a highly persuasive, 2-paragraph proposal explaining exactly why this candidate is a strategic fit for these specific requirements.\n"
                        "3. 90-Day Onboarding Strategy: Generate a structured, realistic 30/60/90-day onboarding plan tailored to the job description.\n\n"
                        "Format the output entirely in clear, professional Markdown using headers and bullet points."
                    )),
                    ("human", "Job Description:\n{job_description}")
                ])
                
                # Create the orchestration chain
                evaluator_chain = agent_prompt | llm
                
                # Invoke the chain
                response = evaluator_chain.invoke({
                    "context": candidate_context,
                    "job_description": job_desc
                })
                
                st.success("Analysis Complete: Strategic fit generated.")
                st.divider()
                
                # Display the autonomous output
                st.markdown(response.content)

            except Exception as e:
                st.error(f"Agentic evaluation failed. Please verify your Mistral API Key and network connection. Error: {e}")
    else:
        st.error("Missing Input Data. Please paste a job description to begin.")