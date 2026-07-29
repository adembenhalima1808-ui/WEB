import streamlit as st
import datetime
import json
import os
import time
import requests
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from core.rag_engine import initialize_rag_system
from core.utils import load_analytics, load_chat_logs, get_secret_val, get_heavy_model_key, save_config, DEFAULT_CONFIG, get_resume_text
from core.telegram_engine import send_webhook_alert
from core.memory_engine import save_sara_history

def render(app_config):
    st.markdown("### ROOT COMMAND CENTER")
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs(["Telemetry & Wiretap", "Telegram Diagnostics", "Agentic Training Simulator", "CMS & Identity", "Vector Brain Injection"])
    
    with adm_tab1:
        analytics_data = load_analytics()
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Total Visits</div><div class="admin-metric-value">{analytics_data["total_visits"]}</div></div>', unsafe_allow_html=True)
        col_t2.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Bot Interactions</div><div class="admin-metric-value">{analytics_data["messages_sent"]}</div></div>', unsafe_allow_html=True)
        col_t3.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">CVs Downloaded</div><div class="admin-metric-value">{analytics_data["cv_downloads"]}</div></div>', unsafe_allow_html=True)
        col_t4.markdown(f'<div class="admin-metric-card"><div class="admin-metric-label">Cover Letters</div><div class="admin-metric-value">{analytics_data["cover_letters_generated"]}</div></div>', unsafe_allow_html=True)

        st.markdown("#### Scanned Corporate Entities")
        if analytics_data["companies_logged"]: 
            st.markdown("".join([f"<span class='company-pill'>{comp}</span>" for comp in analytics_data["companies_logged"]]), unsafe_allow_html=True)
        else: st.write("No specific company queries logged yet.")

        st.markdown("---")
        col_wire1, col_wire2 = st.columns([3, 1])
        col_wire1.markdown("#### Live Chat Wiretap Logs (AI Bot)")
        if col_wire2.button("Refresh Logs", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        chat_history = load_chat_logs()
        if chat_history:
            grouped_logs = {}
            for log in reversed(chat_history):
                comp = log.get("company", "Unknown Entity")
                if comp not in grouped_logs: grouped_logs[comp] = []
                grouped_logs[comp].append(log)
            
            for comp, logs in grouped_logs.items():
                if "sara" in comp.lower() or "wife" in comp.lower(): expander_label, user_color = f"Intercepted: {comp}", "#FF1493"
                elif "egi" in comp.lower(): expander_label, user_color = f"Intercepted: {comp}", "#8A2BE2"
                else: expander_label, user_color = f"Intercepted: {comp}", "#FF7A00"
                    
                with st.expander(f"{expander_label} ({len(logs)} messages)"):
                    with st.container(height=350, border=False):
                        for log in logs:
                            st.markdown(f"""
                            <div style="background: #000; border: 1px solid #333; padding: 12px; border-radius: 6px; margin-bottom: 10px; font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #E4E4E7;">
                                <div style="color: #A1A1AA; font-size: 0.75rem; margin-bottom: 6px;">{log['timestamp']}</div>
                                <div style="margin-bottom: 4px;"><span style="color: {user_color}; font-weight: 600;">User:</span> {log['user']}</div>
                                <div><span style="color: #A1A1AA; font-weight: 600;">Agent:</span> {log['bot']}</div>
                            </div>
                            """, unsafe_allow_html=True)
        else: st.write("No conversations intercepted yet.")

    with adm_tab2:
        st.markdown("### Telegram Connection Diagnostics & Repair")
        col_diag1, col_diag2 = st.columns(2)
        with col_diag1:
            st.markdown("#### Test Telegram Alert Delivery")
            if st.button("Send Test Alert Message", use_container_width=True):
                success, response_text = send_webhook_alert("TEST ALERT: Telegram connection verified from Kitsune Command Center!", return_debug=True)
                if success: st.success(f"SUCCESS: {response_text}")
                else: st.error(f"FAILURE: {response_text}")
        with col_diag2:
            st.markdown("#### Clear Stuck Webhooks")
            if st.button("Force Clear Webhooks", use_container_width=True):
                tg_token = get_secret_val("telegram_token")
                if tg_token:
                    import re
                    if tg_token.lower().startswith("bot"): tg_token = tg_token[3:]
                    tg_token = re.sub(r'[^a-zA-Z0-9:-]', '', tg_token)
                    try:
                        url = f"https://api.telegram.org/bot{tg_token}/deleteWebhook?drop_pending_updates=true"
                        res_data = requests.get(url, timeout=5).json()
                        if res_data and res_data.get("ok"): st.success("Telegram Webhook purged! getUpdates polling is now unblocked.")
                        else: st.error(f"Failed to clear webhook: {res_data.get('description', 'Unknown Error')}")
                    except Exception as e: st.error(f"Error connecting: {e}")
                else: st.error("Missing TELEGRAM_TOKEN secret.")

    with adm_tab3:
        st.markdown("### Agentic Training Simulator")
        st.write("Run a simulated interview loop. An AI Recruiter will interrogate the Kitsune Agent, and a Master Evaluator will score the response and suggest prompt adjustments.")
        
        target_role = st.text_input("Target Company & Role", value="Senior AI Engineer at Datadog")
        
        if st.button("Start Simulation Sequence", type="primary"):
            with st.spinner("AI Recruiter generating question..."):
                try:
                    llm_fast = ChatMistralAI(model="mistral-small-latest", temperature=0.7, mistral_api_key=get_secret_val("MISTRAL_API_KEY"))
                    q_prompt = f"You are a strict technical recruiter hiring a {target_role}. Ask one highly challenging, specific technical interview question to test the candidate's system design and practical AI experience. Ask the question directly."
                    question = llm_fast.invoke([HumanMessage(content=q_prompt)]).content.strip()
                    
                    st.markdown("#### AI Recruiter")
                    st.info(question)
                    
                    rag_chain = initialize_rag_system()
                    resume_raw = get_resume_text()
                    persona = app_config.get("persona_prompt", DEFAULT_CONFIG["persona_prompt"])
                    full_context = f"Company/Role: {target_role}\n{persona}\n\n--- ADEM'S FULL CV ---\n{resume_raw}"
                    
                    response = rag_chain.invoke({"input": question, "company_context": full_context})
                    answer = response["answer"]
                    
                    st.markdown("#### Kitsune Agent (Candidate)")
                    st.success(answer)
                    
                    llm_heavy = ChatMistralAI(model="mistral-medium-latest", temperature=0.2, mistral_api_key=get_heavy_model_key())
                    eval_prompt = f"""
                    You are a Master AI Evaluator. Review this interview exchange for the role of {target_role}:
                    
                    QUESTION: {question}
                    KITSUNE'S ANSWER: {answer}
                    
                    CURRENT MASTER PROMPT:
                    {persona}
                    
                    Evaluate Kitsune's answer based on technical accuracy, confidence, and adherence to the persona.
                    Provide exactly:
                    1. SCORE: (Out of 100)
                    2. CRITIQUE: (What was missing, weak, or overly robotic)
                    3. SUGGESTED PROMPT ADJUSTMENT: (Provide a slightly modified version of the Master Prompt to fix these flaws)
                    """
                    evaluation = llm_heavy.invoke([HumanMessage(content=eval_prompt)]).content
                    
                    st.markdown("#### Master Evaluator")
                    st.warning(evaluation)
                    
                except Exception as e:
                    st.error(f"Simulation Error: {e}")

    with adm_tab4:
        st.info("Security Enforcement Active: API keys locked to Secrets.")
        with st.form("config_form"):
            new_title = st.text_input("Main Hero Title", value=app_config.get("title", ""))
            new_intro = st.text_area("Hero Introduction Text", value=app_config.get("intro_text", ""), height=100)
            new_sidebar_subtitle = st.text_input("Sidebar Subtitle", value=app_config.get("sidebar_subtitle", ""))
            col_cfg_role, col_cfg_loc = st.columns(2)
            with col_cfg_role: new_role_title = st.text_input("Hero Role Title", value=app_config.get("role_title", ""))
            with col_cfg_loc: new_location = st.text_input("Location", value=app_config.get("location", ""))

            col_cfg1, col_cfg2 = st.columns(2)
            with col_cfg1: new_status = st.text_input("Availability Status", value=app_config.get("status_text", ""))
            with col_cfg2: new_color = st.color_picker("Status Pulse Color", value=app_config.get("status_color", "#FF7A00"))

            st.markdown("#### Human Comm-Link Controls")
            col_hc1, col_hc2 = st.columns(2)
            with col_hc1: new_human_enabled = st.checkbox("Enable Human Comm-Link Tab", value=app_config.get("human_comm_enabled", True))
            with col_hc2: new_refresh_rate = st.number_input("Auto-Refresh Rate (Seconds)", min_value=2, max_value=60, value=int(app_config.get("refresh_rate", 5)))

            st.markdown("#### System AI Identity")
            new_persona = st.text_area("Master Persona Prompt", value=app_config.get("persona_prompt", ""), height=150)
            new_wife_persona = st.text_area("Wife Mode Prompt", value=app_config.get("wife_persona_prompt", DEFAULT_CONFIG["wife_persona_prompt"]), height=150)
            new_egi_persona = st.text_area("Egi Mode Prompt", value=app_config.get("egi_persona_prompt", DEFAULT_CONFIG["egi_persona_prompt"]), height=100)
            
            st.markdown("#### Security & Maintenance Protocols")
            new_maintenance = st.checkbox("Enable Maintenance Mode (Lock out ALL non-admins)", value=app_config.get("maintenance_mode", False))
            new_maintenance_reason = st.text_area("Maintenance Notice Message", value=app_config.get("maintenance_reason", DEFAULT_CONFIG["maintenance_reason"]), height=80)
            
            new_resume = st.file_uploader("Upload New Resume (PDF)", type=["pdf"], label_visibility="collapsed")
            
            if st.form_submit_button("Deploy Configuration Overrides", type="primary"):
                app_config.update({
                    "title": new_title, "intro_text": new_intro, "sidebar_subtitle": new_sidebar_subtitle,
                    "role_title": new_role_title, "location": new_location, "status_text": new_status,
                    "status_color": new_color, "human_comm_enabled": new_human_enabled, "refresh_rate": int(new_refresh_rate),
                    "persona_prompt": new_persona, "wife_persona_prompt": new_wife_persona,
                    "egi_persona_prompt": new_egi_persona, 
                    "maintenance_mode": new_maintenance,
                    "maintenance_reason": new_maintenance_reason
                })
                save_config(app_config)
                if new_resume is not None:
                    with open("resume.pdf", "wb") as f: f.write(new_resume.getbuffer())
                st.cache_data.clear()
                st.success("Overrides injected successfully. Rebooting interface...")
                time.sleep(1.5)
                st.rerun()

        col_wipe1, col_wipe2 = st.columns(2)
        with col_wipe1:
            if st.button("Force Clear Neural Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Application memory cache cleared.")
        with col_wipe2:
            if st.button("Wipe Sara's Chat Logs", use_container_width=True):
                save_sara_history([])
                st.success("Sara's chat history wiped!")

    with adm_tab5:
        st.markdown("### Bulk Vector Upload")
        new_knowledge = st.file_uploader("Select .txt file to append", type=["txt"])
        if st.button("Inject File Knowledge", type="primary") and new_knowledge:
            raw_text = new_knowledge.getvalue().decode("utf-8")
            try:
                with open("my_brain.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n\n--- NEW KNOWLEDGE INJECTED ON {datetime.datetime.now().strftime('%Y-%m-%d')} ---\n{raw_text}")
                st.cache_data.clear()
                st.success("Knowledge fused!"); time.sleep(1.5); st.rerun()
            except Exception as e: st.error(f"Error: {e}")
                
        st.divider()
        st.markdown("### Direct Memory Editor")
        current_brain_content = ""
        if os.path.exists("my_brain.txt"):
            with open("my_brain.txt", "r", encoding="utf-8") as f: current_brain_content = f.read()
        
        with st.form("brain_editor_form"):
            edited_brain = st.text_area("Live `my_brain.txt` Contents", value=current_brain_content, height=400)
            if st.form_submit_button("Overwrite Neural Core", type="primary"):
                try:
                    with open("my_brain.txt", "w", encoding="utf-8") as f: f.write(edited_brain)
                    st.cache_data.clear()
                    st.success("Core overwritten!"); time.sleep(1.5); st.rerun()
                except Exception as e: st.error(f"Error: {e}")