import streamlit as st
import time
import os
from PIL import Image
from dotenv import load_dotenv

# --- MISTRAL AI & LANGCHAIN IMPORTS ---
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

# Load the secret API key from the .env file
load_dotenv()

# Setup the main layout
st.set_page_config(page_title="AI Portfolio & Digital Twin", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM DEEPTECH CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0A0F24; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #00F0FF !important; font-weight: 600; letter-spacing: 1px; }
    [data-testid="stSidebar"] { background-color: #070B19; border-right: 1px solid #1E293B; }
    .stButton>button {
        background-color: transparent; color: #00F0FF; border: 1px solid #00F0FF;
        border-radius: 4px; padding: 0.5rem 1rem; font-weight: 600; text-transform: uppercase;
        transition: all 0.3s ease-in-out; box-shadow: 0 0 5px rgba(0, 240, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #00F0FF; color: #000000;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.6); border: 1px solid #00F0FF;
    }
    [data-testid="stChatMessage"] { background-color: #111827; border-radius: 10px; border: 1px solid #1F2937; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #0F172A; color: #00F0FF; border: 1px solid #1E293B; }
    [data-testid="stMetricValue"] { color: #00F0FF !important; }
    </style>
""", unsafe_allow_html=True)

# --- MISTRAL RAG INITIALIZATION ---
@st.cache_resource
def initialize_rag_system():
    # 1. Load your custom CV document
    loader = TextLoader("my_brain.txt")
    docs = loader.load()
    
    # 2. Split the text into manageable chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    
    # 3. Create Vector Embeddings using Mistral
    embeddings = MistralAIEmbeddings(model="mistral-embed")
    vector_store = Chroma.from_documents(split_docs, embeddings)
    retriever = vector_store.as_retriever()
    
    # 4. Initialize the Mistral Text-to-Text Model
    llm = ChatMistralAI(model="mistral-small-latest", temperature=0.3)
    
    # 5. Define the Agent's Persona Prompt
    system_prompt = (
        "You are the professional digital twin of this AI Engineer. "
        "Use the provided context to answer questions about their skills, experience, and education. "
        "Be concise, highly professional, and do not hallucinate details not in the text.\n\n"
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # 6. Chain everything together
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("", ["RAG Digital Twin", "Agentic Evaluator", "Multimodal Vision", "Data Architecture"])
st.sidebar.markdown("---")
st.sidebar.markdown("**Location:** Cergy / Paris, Ile-de-France")

# --- 1. RAG DIGITAL TWIN PAGE ---
if page == "RAG Digital Twin":
    st.title("Self-Representational RAG Agent")
    st.write("Powered by Mistral AI Embeddings and Vector Search.")
    
    # Load the RAG system
    try:
        rag_chain = initialize_rag_system()
        st.success("Mistral AI Neural Link Established. Vector Database Ready.")
    except Exception as e:
        st.error(f"Failed to connect to Mistral AI. Did you add your API key to the .env file? Error: {e}")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "System online. Ask me about my skills, education, or projects."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Input query (e.g., 'What are your skills?')..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Ask Mistral to synthesize the answer
        with st.spinner("Searching vector database..."):
            response = rag_chain.invoke({"input": prompt})
            bot_reply = response["answer"]

        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# --- OTHER PAGES OMITTED FOR BREVITY, THE CSS APPLIES TO ALL OF THEM ---
elif page == "Agentic Evaluator":
    st.title("Agentic Job Matching Evaluator")
    st.write("Paste a job description below. The system will compute a match score.")
    
elif page == "Multimodal Vision":
    st.title("Multimodal Vision Evaluator")
    st.write("Upload an image file to test real-time inference.")

elif page == "Data Architecture":
    st.title("Data Pipeline & Architecture")
    st.write("Pipeline Status: Operational")