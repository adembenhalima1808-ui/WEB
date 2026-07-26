import streamlit as st
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

@st.cache_resource
def initialize_rag_system():
    try:
        loader = TextLoader("my_brain.txt")
        docs = loader.load()
        
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)
        
        embeddings = MistralAIEmbeddings(model="mistral-embed")
        vector_store = Chroma.from_documents(split_docs, embeddings)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        
        llm = ChatMistralAI(model="mistral-small-latest", temperature=0.1)
        
        # Define the Professional Persona Prompt with Dynamic Context
        # Define the Professional Persona Prompt with Strict Brevity Constraints
        system_prompt = (
            "You are the professional digital twin of this AI Engineer. "
            "The user is evaluating the candidate for this specific company context: {company_context}. "
            "Tailor your answers to highlight skills relevant to this company. "
            "CRITICAL INSTRUCTIONS FOR OUTPUT: "
            "1. Be extremely concise, punchy, and direct. "
            "2. Never exceed 3 sentences for a standard reply. "
            "3. If listing skills or projects, use maximum 3 short bullet points. "
            "4. Eliminate all fluff and filler words. Speak like a senior, confident engineer. "
            "5. Base all answers strictly on the Candidate Context below.\n\n"
            "Candidate Context: {context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        return rag_chain
    except Exception as e:
        return f"Initialization Failed: {e}"