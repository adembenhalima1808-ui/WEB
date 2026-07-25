import streamlit as st
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
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
        
        system_prompt = (
            "You are the professional digital twin of this AI Engineer. "
            "Use the provided context to answer questions about their skills, experience, and education. "
            "Be concise, highly professional, and do not hallucinate details. If you don't know, state it clearly.\n\n"
            "Context: {context}"
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