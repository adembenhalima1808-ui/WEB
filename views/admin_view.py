import streamlit as st
import datetime
import json
import os
import time
from core.utils import load_analytics, load_chat_logs, get_secret_val, save_config, DEFAULT_CONFIG
from core.telegram_engine import send_webhook_alert, execute_curl_telegram_get
from core.memory_engine import load_sara_memories, save_sara_memories, save_sara_history

def render(app_config):
    st.markdown("### ROOT COMMAND CENTER")
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs(["Telemetry & Wiretap", "Telegram Diagnostics 🛠️", "Sara's Core Memories 💖", "CMS & Identity", "Vector Brain Injection"])
    
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
        if col_wire2.button("🔄 Refresh Logs", use_container_width=True):
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
                if "sara" in comp.lower() or "wife" in comp.lower(): expander_label, user_color = f"💖 Intercepted: {comp}", "#FF1493"
                elif "egi" in comp.lower(): expander_label, user_color = f"😈 Intercepted: {comp}", "#8A2BE2"
                else: expander_label, user_color = f"🦊 Intercepted: {comp}", "#FF7A00"
                    
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
                success, response_text = send_webhook_alert("🔔 TEST ALERT: Telegram connection verified from Kitsune Command Center!", return_debug=True)
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
                        res_data = execute_curl_telegram_get(tg_token, clear_webhook=True)
                        if res_data and res_data.get("ok"): st.success("Telegram Webhook purged! getUpdates polling is now unblocked.")
                        else: st.error(f"Failed to clear webhook: {res_data.get('description', 'Unknown Error')}")
                    except Exception as e: st.error(f"Error connecting: {e}")
                else: st.error("Missing TELEGRAM_TOKEN secret.")

    with adm_tab3:
        st.markdown("### Sara's Learned Memories & Character Profile")
        current_sara_memories = load_sara_memories()
        
        if current_sara_memories:
            st.markdown("#### Current Memory Database:")
            for i, mem in enumerate(current_sara_memories):
                col_m1, col_m2 = st.columns([11, 1])
                col_m1.markdown(f"- `{mem}`")
                if col_m2.button("❌", key=f"del_mem_{i}", help="Delete this memory permanently"):
                    current_sara_memories.pop(i)
                    save_sara_memories(current_sara_memories)
                    st.rerun()
        else:
            st.info("No memories logged for Sara yet.")
            
        st.divider()
        st.markdown("#### Inject Manual Memory:")
        with st.form("add_sara_mem_form", clear_on_submit=True):
            new_mem_input = st.text_input("New Memory / Fact about Sara", placeholder="e.g. Sara loves peonies...")
            if st.form_submit_button("Inject to Sara's Memory") and new_mem_input.strip():
                current_sara_memories.append(f"[{datetime.datetime.now().strftime('%Y-%m-%d')}] (Manual) {new_mem_input.strip()}")
                save_sara_memories(current_sara_memories)
                st.success("Memory injected!")
                time.sleep(1)
                st.rerun()
                    
        col_sm1, col_sm2 = st.columns(2)
        if col_sm1.button("Purge ALL Sara's Memories", use_container_width=True):
            save_sara_memories([])
            st.success("Cleared!"); st.rerun()
        if col_sm2.button("Wipe Sara's Chat Logs", use_container_width=True):
            save_sara_history([])
            st.success("Wiped!"); st.rerun()

    with adm_tab4:
        st.info("🔒 **Security Enforcement Active:** API keys locked to Secrets.")
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
            
            new_maintenance = st.checkbox("Enable Maintenance Mode", value=app_config.get("maintenance_mode", False))
            new_resume = st.file_uploader("Upload New Resume (PDF)", type=["pdf"], label_visibility="collapsed")
            
            if st.form_submit_button("Deploy Configuration Overrides", type="primary"):
                app_config.update({
                    "title": new_title, "intro_text": new_intro, "sidebar_subtitle": new_sidebar_subtitle,
                    "role_title": new_role_title, "location": new_location, "status_text": new_status,
                    "status_color": new_color, "human_comm_enabled": new_human_enabled, "refresh_rate": int(new_refresh_rate),
                    "persona_prompt": new_persona, "wife_persona_prompt": new_wife_persona,
                    "egi_persona_prompt": new_egi_persona, "maintenance_mode": new_maintenance
                })
                save_config(app_config)
                if new_resume is not None:
                    with open("resume.pdf", "wb") as f: f.write(new_resume.getbuffer())
                st.cache_data.clear()
                st.success("Overrides injected successfully. Rebooting interface...")
                time.sleep(1.5)
                st.rerun()

        if st.button("Force Clear Neural Cache"): st.cache_data.clear(); st.success("Cache cleared.")

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