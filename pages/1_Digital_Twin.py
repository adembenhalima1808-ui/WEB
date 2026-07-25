import streamlit as st
from core.rag_engine import initialize_rag_system

st.markdown("# Interactive Digital Twin")
st.markdown("An authorized Retrieval-Augmented Generation (RAG) system based on the candidate's professional repository.")

# Load the cached RAG system from the core module
rag_chain = initialize_rag_system()

if isinstance(rag_chain, str) and "Failed" in rag_chain:
    st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
    st.stop()
else:
    st.success("System Initialized. Vector Database Sync Complete.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "RAG system operational. Interrogate me about my skills or professional history."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Input professional query..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Processing through neural chain..."):
        try:
            # Pull the company context from memory (default to general if empty)
            current_context = st.session_state.get("company_context", "General public evaluation.")
            
            # Pass BOTH the user's question and the company context to Mistral
            response = rag_chain.invoke({
                "input": prompt, 
                "company_context": current_context
            })
            bot_reply = response["answer"]
        except Exception as e:
            bot_reply = f"Error during inference: {e}"

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})