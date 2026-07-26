import os
import streamlit as st
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

@st.cache_resource(show_spinner=False)
def initialize_rag_system():
    try:
        # Strictly fetch the Standard API Key for RAG
        api_key = os.getenv("MISTRAL_API_KEY", "")
        if not api_key and "MISTRAL_API_KEY" in st.secrets:
            api_key = st.secrets["MISTRAL_API_KEY"]
            
        if not api_key:
            return "Initialization Failed: Missing MISTRAL_API_KEY."

        # Initialize Embeddings and LLM on the SMALL model
        embeddings = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)
        llm = ChatMistralAI(model="mistral-small-latest", temperature=0.3, mistral_api_key=api_key)

        # Fallback if brain file is missing
        if not os.path.exists("my_brain.txt"):
            with open("my_brain.txt", "w", encoding="utf-8") as f:
                f.write("Adem Ben Halima is a highly skilled AI & Machine Learning Engineer.")
        
        loader = TextLoader("my_brain.txt", encoding="utf-8")
        documents = loader.load()

        # Split text into manageable chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)

        # Create Vector Store
        vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # Define the Prompt Template
        system_prompt = (
            "You are the Kitsune Agent, an autonomous digital twin of Adem Ben Halima.\n"
            "Use the following retrieved context to answer the user's question accurately.\n"
            "Context: {context}\n\n"
            "Target Company Context: {company_context}\n"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # Build Retrieval Chains
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        return rag_chain
    except Exception as e:
        return f"Initialization Failed: {str(e)}"