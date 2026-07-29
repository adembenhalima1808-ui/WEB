import streamlit as st
import time
import datetime
import plotly.graph_objects as go
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from core.rag_engine import initialize_rag_system
from core.utils import (
    get_heavy_model_key, stream_response, DEFAULT_CONFIG, 
    extract_skills_from_resume, get_resume_text, get_secret_val, increment_metric
)
from core.telegram_engine import log_chat, send_webhook_alert, load_live_chat, save_live_chat, sync_telegram_replies

def render(app_config):
    st.markdown(f"# {app_config.get('title', 'Cyber-Kitsune Architecture')}")
    st.markdown(f"**Role:** {app_config.get('role_title', 'End-to-End AI & Machine Learning Engineer')} | **Location:** {app_config.get('location', 'Cergy, Île-de-France')}")
    st.write(app_config.get('intro_text', 'Welcome to my digital den.'))

    st.markdown("### Core Engineering Competencies")
    with st.spinner("Agent extracting core competencies from CV..."):
        current_context = st.session_state.get("company_context", "General public evaluation.")
        categories, skill_scores = extract_skills_from_resume(current_context)
    
    categories_closed = categories + [categories[0]]
    skill_scores_closed = skill_scores + [skill_scores[0]]
    fillcolor = 'rgba(255, 122, 0, 0.2)'
    linecolor = '#FF7A00'
    gridcol = 'rgba(255,255,255,0.05)'

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=skill_scores_closed, theta=categories_closed, fill='toself', fillcolor=fillcolor, line=dict(color=linecolor, width=2), name='Score', hoverinfo='none'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor=gridcol, showticklabels=False), angularaxis=dict(gridcolor=gridcol, tickfont=dict(color="#A1A1AA", size=12)), bgcolor='#000000'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=60, r=60, t=30, b=30), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
    st.divider()

    is_human_comm_active = app_config.get("human_comm_enabled", True)
    if is_human_comm_active:
        tab_chat, tab_agent, tab_human = st.tabs(["Direct Interrogation", "Agentic Operations", "Direct Comm-Link"])
    else:
        tab_chat, tab_agent = st.tabs(["Direct Interrogation", "Agentic Operations"])

    with tab_chat:
        st.markdown("### Direct Interrogation Interface")
        if "quick_prompts" not in st.session_state:
            st.session_state.quick_prompts = ["What are your core AI skills?", "What architectures have you built?", "Why should we hire you?"]

        st.markdown("**Suggested Trails to Follow:**")
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        selected_prompt = None
        with chip_col1:
            if st.button(st.session_state.quick_prompts[0], use_container_width=True, key="p_btn1"): selected_prompt = st.session_state.quick_prompts[0]
        with chip_col2:
            if st.button(st.session_state.quick_prompts[1], use_container_width=True, key="p_btn2"): selected_prompt = st.session_state.quick_prompts[1]
        with chip_col3:
            if st.button(st.session_state.quick_prompts[2], use_container_width=True, key="p_btn3"): selected_prompt = st.session_state.quick_prompts[2]

        st.write("") 
        rag_chain = initialize_rag_system()

        if isinstance(rag_chain, str) and "Failed" in rag_chain: 
            st.error(f"Unable to establish Neural Link. Check configuration.\n\nError details: {rag_chain}")
        else:
            if len(st.session_state.messages) == 0:
                current_hour = datetime.datetime.now().hour
                greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"
                scent_context = "General tracking initialized."
                if "Company Name:" in st.session_state.company_context:
                    extracted_name = st.session_state.company_context.split("\n")[0].replace("Company Name: ", "")
                    scent_context = f"Context locked to {extracted_name}."
                
                intro_text = (
                    f"{greeting}. I am the Kitsune Agent—Adem's autonomous digital twin. 🦊 {scent_context}\n\n"
                    "Welcome to the Command Center. Here is your tactical breakdown:\n\n"
                    "- **The Radar Web (Above):** Live visualization of Adem's core engineering competencies, dynamically re-weighted based on your company's profile.\n"
                    "- **Direct Interrogation (Here):** Ask me anything about Adem's experience, system architectures, or problem-solving approaches.\n"
                    "- **Agentic Operations (Next Tab):** Feed me a Job Description. I can autonomously calculate a Fit Score, draft a targeted cover letter, or generate technical interview questions.\n"
                )
                if is_human_comm_active:
                    intro_text += "- **Direct Comm-Link (3rd Tab):** Bypass the AI and ping Adem's personal phone in real-time.\n"
                intro_text += "- **Feedback Box (Sidebar):** Notice a bug or have a suggestion? Drop an anonymous note straight to the developer.\n\n"
                intro_text += "How can I assist you today?"
                st.session_state.messages.append({"role": "assistant", "content": intro_text})

            chat_container = st.container(height=500, border=True)
            with chat_container:
                for message in st.session_state.messages:
                    avatar_icon = "🦊" if message["role"] == "assistant" else "🧑‍💻"
                    with st.chat_message(message["role"], avatar=avatar_icon): st.markdown(message["content"])

            user_input = st.chat_input("Input query here...")
            prompt_to_process = user_input or selected_prompt

            if prompt_to_process:
                increment_metric("messages_sent")
                with chat_container:
                    with st.chat_message("user", avatar="🧑‍💻"): st.markdown(prompt_to_process)
                st.session_state.messages.append({"role": "user", "content": prompt_to_process})

                with chat_container:
                    with st.chat_message("assistant", avatar="🦊"):
                        with st.spinner("Processing query..."):
                            time.sleep(0.6)
                            try:
                                resume_raw = get_resume_text()
                                chat_categories, _ = extract_skills_from_resume(current_context)
                                resume_injection = f"\n\n--- ADEM'S FULL CV ---\n{resume_raw}\n\n--- CORE SKILLS ---\n{', '.join(chat_categories)}\n"
                                persona_instruction = app_config.get("persona_prompt", DEFAULT_CONFIG["persona_prompt"])
                                full_context = st.session_state.company_context + persona_instruction + resume_injection + st.session_state.agentic_memory

                                response = rag_chain.invoke({"input": prompt_to_process, "company_context": full_context})
                                bot_reply = response["answer"]
                            except Exception as e:
                                bot_reply = f"Error during inference: {e}"
                        st.write_stream(stream_response(bot_reply))
                        
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                log_chat(current_context, prompt_to_process, bot_reply)

                if selected_prompt in st.session_state.quick_prompts:
                    try:
                        api_key = get_secret_val("MISTRAL_API_KEY")
                        if api_key:
                            llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7, mistral_api_key=api_key)
                            new_suggestion = llm_fast.invoke([HumanMessage(content=f"Suggest exactly 1 short follow-up question. User: {prompt_to_process} Bot: {bot_reply}")]).content.strip().strip('"')
                            if new_suggestion:
                                st.session_state.quick_prompts[st.session_state.quick_prompts.index(selected_prompt)] = new_suggestion
                    except Exception: pass 
                    st.rerun()

    with tab_agent:
        st.markdown("### Agentic Operations")
        st.write("Inject a Job Description below to run autonomous candidate evaluations.")
        jd_input = st.text_area("Target Job Description", placeholder="Paste the full job description here...", height=200)
        
        col_act1, col_act2, col_act3 = st.columns(3)
        agent_action = None
        if col_act1.button("Calculate Fit Score", use_container_width=True): agent_action = "Fit Score Analysis"
        if col_act2.button("Draft Cover Letter", use_container_width=True): agent_action = "Cover Letter Generation"
        if col_act3.button("Extract Interview Qs", use_container_width=True): agent_action = "Interview Question Extraction"

        if agent_action and not jd_input.strip(): st.warning("Please paste a Job Description first.")
        elif agent_action and jd_input.strip():
            if agent_action == "Cover Letter Generation": increment_metric("cover_letters_generated")
            with st.spinner(f"Executing agentic protocol: {agent_action}..."):
                try:
                    api_key = get_heavy_model_key()
                    llm_ops = ChatMistralAI(model="mistral-medium-latest", temperature=0.3, mistral_api_key=api_key)
                    resume_content = get_resume_text()
                    
                    if agent_action == "Fit Score Analysis":
                        task_prompt = f"Compare this candidate's resume to the Job Description. Give a definitive 'Fit Score' out of 100. Then provide 3 'Strongest Alignments' and 2 'Potential Gaps/Growth Areas'.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                    elif agent_action == "Cover Letter Generation":
                        current_date = datetime.datetime.now().strftime("%B %d, %Y")
                        task_prompt = f"Write a highly tailored, technical cover letter for Adem Ben Halima based on the Job Description below. Include today's date ({current_date}). Limit to 3 paragraphs. OUTPUT ONLY THE COVER LETTER.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"
                    elif agent_action == "Interview Question Extraction":
                        task_prompt = f"Based on this candidate's resume and the Job Description, generate the 4 most critical technical interview questions the hiring manager should ask them.\n\nResume:\n{resume_content}\n\nJob Description:\n{jd_input}"

                    agent_response = llm_ops.invoke([HumanMessage(content=task_prompt)])
                    st.session_state.messages.append({"role": "user", "content": f"System Command Executed: {agent_action} based on the provided Job Description."})
                    st.session_state.messages.append({"role": "assistant", "content": agent_response.content})
                    st.session_state.agentic_memory += f"\n\n--- RECENT SYSTEM OPERATION: {agent_action} ---\n{agent_response.content}\n\n"
                    
                    st.markdown(f"#### {agent_action} Output:")
                    st.container(border=True).write_stream(stream_response(agent_response.content))
                    
                    if agent_action == "Cover Letter Generation":
                        st.download_button(label="Download Cover Letter (TXT)", data=agent_response.content, file_name="Cover_Letter_Adem_Ben_Halima.txt", mime="text/plain", use_container_width=True)
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    if is_human_comm_active:
        with tab_human:
            st.markdown("### Direct Comm-Link")
            st.write("Bypass the AI and send a message directly to my personal device. I will reply here if available.")
            current_company_session = st.session_state.get("company_context", "General Public").split('\n')[0].replace('Company Name: ', '')
            
            new_human_msg = st.chat_input("Send a direct message to Adem...", key="human_chat_input_box")
            if new_human_msg:
                full_chat = load_live_chat()
                if current_company_session not in full_chat: full_chat[current_company_session] = []
                full_chat[current_company_session].append({"role": "user", "company": current_company_session, "content": new_human_msg, "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "unix_time": time.time()})
                save_live_chat(full_chat)
                send_webhook_alert(f"MESSAGE FROM {current_company_session}:\n{new_human_msg}\n\n(Swipe to reply directly to this message to answer them)")
            
            @st.fragment(run_every=app_config.get("refresh_rate", 5))
            def render_chat_feed(target_company, start_timestamp):
                sync_telegram_replies()
                chat_container = st.container(height=400, border=True)
                with chat_container:
                    live_chats = load_live_chat().get(target_company, [])
                    session_chats = [c for c in live_chats if c.get("unix_time", 0) >= start_timestamp]
                    if not session_chats: st.markdown("<p style='text-align:center; color:#A1A1AA; margin-top:150px;'>Comm-Link established. Awaiting input.</p>", unsafe_allow_html=True)
                    else:
                        for c in session_chats:
                            sender_label = f"**{c.get('company', 'Guest')}**" if c["role"] == "user" else "**Adem (Admin)**"
                            st.chat_message(c["role"], avatar=None).markdown(f"{sender_label} [{c.get('timestamp')}]: {c['content']}")

            render_chat_feed(current_company_session, st.session_state.get("session_start_time", 0))