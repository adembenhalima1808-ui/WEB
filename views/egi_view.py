import streamlit as st
import time
import plotly.graph_objects as go
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from core.rag_engine import initialize_rag_system
from core.utils import get_heavy_model_key, stream_response, DEFAULT_CONFIG, get_resume_text, get_secret_val
from core.telegram_engine import log_chat, send_webhook_alert, load_live_chat, save_live_chat, sync_telegram_replies
import datetime

def render(app_config):
    st.markdown(f"# The Loser's Lounge")
    st.markdown(f"**Role:** Sara's Sister | **Location:** In Adem's Shadow")
    st.write("Welcome to the roast room, Egi. Try not to cry.")
    
    st.markdown("### Egi's Flaw Radar")
    categories_closed = ['Being Loud', 'Annoying Adem', 'Delusion', 'Sarcasm', 'Complaining', 'Actually Trying', 'Being Loud']
    skill_scores_closed = [99, 100, 95, 85, 90, 10, 99]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=skill_scores_closed, theta=categories_closed, fill='toself', fillcolor='rgba(138, 43, 226, 0.2)', line=dict(color='#8A2BE2', width=2), hoverinfo='none'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(138, 43, 226, 0.1)', showticklabels=False), angularaxis=dict(gridcolor='rgba(138, 43, 226, 0.1)', tickfont=dict(color="#A1A1AA", size=12)), bgcolor='#000000'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=60, r=60, t=30, b=30), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.divider()

    tab_chat, tab_agent, tab_human = st.tabs(["Roast Session", "Reality Check", "Direct Comm-Link"])

    with tab_chat:
        st.markdown("### The Roast Box")
        if "quick_prompts" not in st.session_state:
            st.session_state.quick_prompts = ["Am I the favorite?", "Roast me.", "Tell me a joke about me."]

        chip_col1, chip_col2, chip_col3 = st.columns(3)
        selected_prompt = None
        with chip_col1:
            if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="e_btn1"): selected_prompt = st.session_state.quick_prompts[0]
        with chip_col2:
            if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="e_btn2"): selected_prompt = st.session_state.quick_prompts[1]
        with chip_col3:
            if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="e_btn3"): selected_prompt = st.session_state.quick_prompts[2]

        st.write("") 
        rag_chain = initialize_rag_system()

        if len(st.session_state.messages) == 0:
            current_hour = datetime.datetime.now().hour
            greeting = "Ugh, morning" if current_hour < 12 else "Whatever, afternoon" if current_hour < 18 else "Look who it is, evening"
            intro_text = f"{greeting}.\n\nI am Adem's highly advanced AI agent. He built me because he's a genius, something you wouldn't know much about. \n\nGo ahead, ask me something. I'll try to use small words so you can understand."
            st.session_state.messages.append({"role": "assistant", "content": intro_text})

        chat_container = st.container(height=500, border=True)
        with chat_container:
            for message in st.session_state.messages:
                avatar_icon = "😈" if message["role"] == "assistant" else "🤡"
                with st.chat_message(message["role"], avatar=avatar_icon): st.markdown(message["content"])

        user_input = st.chat_input("Say something dumb...")
        prompt_to_process = user_input or selected_prompt

        if prompt_to_process:
            with chat_container:
                with st.chat_message("user", avatar="🤡"): st.markdown(prompt_to_process)
            st.session_state.messages.append({"role": "user", "content": prompt_to_process})

            with chat_container:
                with st.chat_message("assistant", avatar="😈"):
                    with st.spinner("Formulating a roast..."):
                        try:
                            resume_injection = f"\n\n--- ADEM'S FULL CV ---\n{get_resume_text()}\n"
                            persona_instruction = app_config.get("egi_persona_prompt", DEFAULT_CONFIG["egi_persona_prompt"])
                            current_context = st.session_state.company_context + persona_instruction + resume_injection
                            response = rag_chain.invoke({"input": prompt_to_process, "company_context": current_context})
                            bot_reply = response["answer"]
                        except Exception as e: bot_reply = f"Error: {e}"
                    st.write_stream(stream_response(bot_reply))
                    
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            log_chat("Egi (Sister-in-law)", prompt_to_process, bot_reply)
            st.rerun()

    with tab_agent:
        st.markdown("### Reality Check")
        st.markdown("#### Request a Custom Roast")
        roast_input = st.text_input("What did you do today that deserves to be mocked?", placeholder="e.g., I woke up at 2 PM...")
        if st.button("Roast Me", use_container_width=True) and roast_input.strip():
            with st.spinner("Loading insults..."):
                try:
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.8, mistral_api_key=get_heavy_model_key())
                    task_prompt = f"You are Adem's AI. Sara's sister and Adem's sister-in-law, Egi, just admitted: '{roast_input}'. Write a hilarious, sarcastic 3-sentence roast. Remind her she's the lesser family member."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.container(border=True).write_stream(stream_response(agent_response.content))
                    log_chat("Egi (Sister-in-law)", f"[Roast Tool] {roast_input}", agent_response.content)
                except Exception: st.error("Error generating roast.")
                
        st.divider()
        st.markdown("#### Why Adem is Better")
        if st.button("Remind Me", use_container_width=True):
            with st.spinner("Fetching cold hard facts..."):
                try:
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.8, mistral_api_key=get_heavy_model_key())
                    task_prompt = "You are Adem's AI. Write a funny, arrogant list of 3 undeniable reasons why Adem is the smarter, better, and favorite family member compared to his sister-in-law (Sara's sister) Egi."
                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.container(border=True).write_stream(stream_response(agent_response.content))
                    log_chat("Egi (Sister-in-law)", "[Better Tool]", agent_response.content)
                except Exception: pass

    with tab_human:
        st.markdown("### Direct Comm-Link")
        current_company_session = "Egi"
        new_human_msg = st.chat_input("Send a message...", key="egi_chat_input_box")
        if new_human_msg:
            full_chat = load_live_chat()
            if current_company_session not in full_chat: full_chat[current_company_session] = []
            full_chat[current_company_session].append({"role": "user", "company": current_company_session, "content": new_human_msg, "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "unix_time": time.time()})
            save_live_chat(full_chat)
            send_webhook_alert(f"MESSAGE FROM 😈 {current_company_session}:\n{new_human_msg}")
        
        @st.fragment(run_every=app_config.get("refresh_rate", 5))
        def render_chat_feed(target_company, start_timestamp):
            sync_telegram_replies()
            chat_container = st.container(height=400, border=True)
            with chat_container:
                live_chats = load_live_chat().get(target_company, [])
                session_chats = [c for c in live_chats if c.get("unix_time", 0) >= start_timestamp]
                if not session_chats: st.markdown("<p style='text-align:center; color:#A1A1AA; margin-top:150px;'>Comm-Link established.</p>", unsafe_allow_html=True)
                else:
                    for c in session_chats: st.chat_message(c["role"], avatar=None).markdown(f"**{c.get('company')}** [{c.get('timestamp')}]: {c['content']}")
        render_chat_feed(current_company_session, st.session_state.get("session_start_time", 0))