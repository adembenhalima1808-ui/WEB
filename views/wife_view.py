import streamlit as st
import time
import plotly.graph_objects as go
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from core.rag_engine import initialize_rag_system
from core.utils import get_heavy_model_key, stream_response, DEFAULT_CONFIG, extract_skills_from_resume, extract_stack_from_resume, get_resume_text, get_secret_val, increment_metric
from core.telegram_engine import log_chat, send_webhook_alert, load_live_chat, save_live_chat, sync_telegram_replies
from core.memory_engine import load_sara_history, save_sara_history, load_sara_memories, extract_and_store_sara_memories
import datetime

def render(app_config):
    st.markdown(f"# Sara's Private Dashboard")
    st.markdown(f"**Role:** Partner in Crime | **Location:** Right beside you")
    st.write("Welcome to your personal space. Adem built this so you can bypass the professional stuff.")
    
    st.markdown("### Sara's Vibe Matrix")
    categories_closed = ['Patience (with Adem)', 'Roasting Skills', 'Being Right', 'Making Adem Smile', 'Stubbornness', 'Support', 'Patience (with Adem)']
    skill_scores_closed = [95, 85, 100, 100, 90, 100, 95]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=skill_scores_closed, theta=categories_closed, fill='toself', fillcolor='rgba(255, 20, 147, 0.2)', line=dict(color='#FF1493', width=2), hoverinfo='none'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255, 20, 147, 0.1)', showticklabels=False), angularaxis=dict(gridcolor='rgba(255, 20, 147, 0.1)', tickfont=dict(color="#A1A1AA", size=12)), bgcolor='#000000'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=60, r=60, t=30, b=30), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.divider()

    tab_chat, tab_agent, tab_human = st.tabs(["Talk to Me", "Wife Utilities", "Direct Comm-Link"])

    with tab_chat:
        st.markdown("### Chat Interface")
        if "quick_prompts" not in st.session_state:
            st.session_state.quick_prompts = ["Tell me a funny story about Adem.", "Who is right in our argument?", "What do you remember about me?"]

        st.markdown("**Suggested Trails to Follow:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        selected_prompt = None
        with chip_col1:
            if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="w_btn1"): selected_prompt = st.session_state.quick_prompts[0]
        with chip_col2:
            if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="w_btn2"): selected_prompt = st.session_state.quick_prompts[1]
        with chip_col3:
            if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="w_btn3"): selected_prompt = st.session_state.quick_prompts[2]

        st.write("") 
        rag_chain = initialize_rag_system()

        if isinstance(rag_chain, str) and "Failed" in rag_chain: 
            st.error(f"Unable to establish Neural Link.\n\nError details: {rag_chain}")
        else:
            if len(st.session_state.messages) == 0:
                current_hour = datetime.datetime.now().hour
                greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
                intro_text = f"{greeting}, Sara.\n\nWelcome back to your private access level. I remember everything we talk about, so feel free to pick up where we left off.\n\nAsk me anything, tell me if Adem's being annoying, or just say hi. What's on your mind?"
                st.session_state.messages.append({"role": "assistant", "content": intro_text})

            chat_container = st.container(height=500, border=True)
            with chat_container:
                for message in st.session_state.messages:
                    avatar_icon = "🦊" if message["role"] == "assistant" else "👩‍💻"
                    with st.chat_message(message["role"], avatar=avatar_icon): st.markdown(message["content"])

            user_input = st.chat_input("Talk to me bestie...")
            prompt_to_process = user_input or selected_prompt

            if prompt_to_process:
                with chat_container:
                    with st.chat_message("user", avatar="👩‍💻"): st.markdown(prompt_to_process)
                st.session_state.messages.append({"role": "user", "content": prompt_to_process})

                with chat_container:
                    with st.chat_message("assistant", avatar="🦊"):
                        with st.spinner("Recalling past memories..."):
                            try:
                                resume_injection = f"\n\n--- ADEM'S FULL CV ---\n{get_resume_text()}\n"
                                persona_instruction = app_config.get("wife_persona_prompt", DEFAULT_CONFIG["wife_persona_prompt"])
                                sara_memories = load_sara_memories()
                                memory_injection = "\n\n--- SARA'S KNOWN MEMORIES & CHARACTER TRAITS ---\n" + "\n".join(sara_memories) + "\n"
                                current_context = st.session_state.company_context + persona_instruction + memory_injection + resume_injection

                                response = rag_chain.invoke({"input": prompt_to_process, "company_context": current_context})
                                bot_reply = response["answer"]
                            except Exception as e: bot_reply = f"Error: {e}"
                        st.write_stream(stream_response(bot_reply))
                        
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                save_sara_history(st.session_state.messages)
                extract_and_store_sara_memories(prompt_to_process, bot_reply)
                log_chat(st.session_state.get("company_context", ""), prompt_to_process, bot_reply)

                if selected_prompt in st.session_state.quick_prompts:
                    try:
                        api_key = get_secret_val("MISTRAL_API_KEY")
                        if api_key:
                            llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7, mistral_api_key=api_key)
                            new_suggestion = llm_fast.invoke([HumanMessage(content=f"Suggest 1 short follow-up question. User: {prompt_to_process} Bot: {bot_reply}")]).content.strip().strip('"')
                            if new_suggestion: st.session_state.quick_prompts[st.session_state.quick_prompts.index(selected_prompt)] = new_suggestion
                    except Exception: pass 
                    st.rerun()

    with tab_agent:
        st.markdown("### Wife Utilities")
        st.markdown("#### Settle an Argument")
        arg_input = st.text_area("What are you two arguing about right now?", height=100)
        if st.button("Judge Us", use_container_width=True) and arg_input.strip():
            with st.spinner("Analyzing the dispute..."):
                try:
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.7, mistral_api_key=get_heavy_model_key())
                    sara_mems = load_sara_memories()
                    mem_context = "\nKnown facts about Sara: " + ", ".join(sara_mems[-5:]) if sara_mems else ""
                    task_prompt = f"Act as a playful judge between Adem and wife Sara.{mem_context} Arguing about: '{arg_input}'. Assing a Rightness Percentage totaling 100%. Usually lean towards taking Sara's side."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.markdown("#### Verdict:")
                    st.container(border=True).write_stream(stream_response(agent_response.content))
                    log_chat("Sara (Wife)", f"[Argument Tool] {arg_input}", agent_response.content)
                except Exception: st.error("Error connecting.")
                
        st.divider()
        st.markdown("#### Send a Sweet Note")
        if st.button("Say Something Sweet", use_container_width=True):
            with st.spinner("Writing..."):
                try:
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.7, mistral_api_key=get_heavy_model_key())
                    sara_mems = load_sara_memories()
                    mem_context = "\nIncorporate her preferences: " + ", ".join(sara_mems[-5:]) if sara_mems else ""
                    task_prompt = f"Write a short, sweet message from Adem to Sara.{mem_context} Don't be cheesy."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.markdown("#### For You:")
                    st.container(border=True).write_stream(stream_response(agent_response.content))
                    log_chat("Sara (Wife)", "[Sweet Note Tool]", agent_response.content)
                except Exception: st.error("Error connecting.")

    with tab_human:
        st.markdown("### Direct Comm-Link")
        current_company_session = st.session_state.get("company_context", "Wife").split('\n')[0].replace('Company Name: ', '')
        new_human_msg = st.chat_input("Send a direct message to Adem...", key="human_chat_input_box")
        
        if new_human_msg:
            full_chat = load_live_chat()
            if current_company_session not in full_chat: full_chat[current_company_session] = []
            full_chat[current_company_session].append({"role": "user", "company": current_company_session, "content": new_human_msg, "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "unix_time": time.time()})
            save_live_chat(full_chat)
            send_webhook_alert(f"MESSAGE FROM 💖 {current_company_session}:\n{new_human_msg}")
        
        @st.fragment(run_every=app_config.get("refresh_rate", 5))
        def render_chat_feed(target_company, start_timestamp):
            sync_telegram_replies()
            chat_container = st.container(height=400, border=True)
            with chat_container:
                live_chats = load_live_chat().get(target_company, [])
                session_chats = [c for c in live_chats if c.get("unix_time", 0) >= start_timestamp]
                if not session_chats: st.markdown("<p style='text-align:center; color:#A1A1AA; margin-top:150px;'>Comm-Link established.</p>", unsafe_allow_html=True)
                else:
                    for c in session_chats:
                        st.chat_message(c["role"], avatar=None).markdown(f"**{c.get('company')}** [{c.get('timestamp')}]: {c['content']}")
        render_chat_feed(current_company_session, st.session_state.get("session_start_time", 0))