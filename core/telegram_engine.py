import time
import datetime
import json
import requests
import re
from core.utils import get_secret_val, load_config, save_config, load_live_chat, save_live_chat, load_chat_logs, CHAT_LOGS_FILE

def send_webhook_alert(message, return_debug=False):
    discord_url = get_secret_val("discord_webhook")
    if discord_url:
        try: requests.post(discord_url, json={"content": f"🦊 **KITSUNE PAGER:** {message}"}, timeout=2)
        except Exception: pass

    tg_token = get_secret_val("telegram_token")
    tg_chat_id = get_secret_val("telegram_chat_id")
    if not tg_token or not tg_chat_id: return False
    if tg_token.lower().startswith("bot"): tg_token = tg_token[3:]
    
    safe_message = message.replace("**", "").replace("*", "").replace("_", "")
    tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = {"chat_id": str(tg_chat_id), "text": f"🦊 KITSUNE PAGER:\n{safe_message}"}
    
    try:
        res = requests.post(tg_url, json=payload, timeout=5)
        if res.json().get("ok"): return True
    except Exception: pass
    return False

def sync_telegram_replies():
    tg_token = get_secret_val("telegram_token")
    tg_chat_id = get_secret_val("telegram_chat_id")
    if not tg_token or not tg_chat_id: return
    if tg_token.lower().startswith("bot"): tg_token = tg_token[3:]
    
    fresh_config = load_config()
    last_update_id = fresh_config.get("telegram_last_update_id", 0)
    
    try:
        url = f"https://api.telegram.org/bot{tg_token}/getUpdates?offset={last_update_id + 1}&timeout=1"
        res = requests.get(url, timeout=1.5).json()
        
        if res.get("ok") and res.get("result"):
            chat_data = load_live_chat()
            found_new = False
            
            for item in res["result"]:
                update_id = item["update_id"]
                if update_id > last_update_id:
                    last_update_id = update_id
                    msg = item.get("message", {})
                    if str(msg.get("chat", {}).get("id")) == str(tg_chat_id):
                        text = msg.get("text", "")
                        if text and not text.startswith("/"):
                            target_company = "General Public"
                            if "reply_to_message" in msg:
                                orig_text = msg["reply_to_message"].get("text", "")
                                if "MESSAGE FROM" in orig_text:
                                    try:
                                        target_company = orig_text.split("MESSAGE FROM ")[1].split(":")[0].strip()
                                        target_company = target_company.replace("*", "").replace("🦊", "").replace("💖", "").replace("😈", "").strip()
                                    except Exception: pass
                            
                            if target_company not in chat_data: chat_data[target_company] = []
                            chat_data[target_company].append({
                                "role": "assistant", "company": "Adem (Admin)", "content": text,
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"), "unix_time": time.time()
                            })
                            found_new = True
            if found_new:
                save_live_chat(chat_data)
                fresh_config["telegram_last_update_id"] = last_update_id
                save_config(fresh_config)
    except Exception: pass

def log_chat(company, user_msg, bot_msg):
    logs = load_chat_logs()
    clean_company = company.split('\n')[0].replace('Company Name: ', '') if 'Company Name:' in company else company
    logs.append({"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "company": clean_company, "user": user_msg, "bot": bot_msg})
    try:
        import os
        with open(CHAT_LOGS_FILE + ".tmp", "w") as f: json.dump(logs, f)
        os.replace(CHAT_LOGS_FILE + ".tmp", CHAT_LOGS_FILE)
    except Exception: pass
    
    icon = "😈" if "egi" in clean_company.lower() else "💖" if "sara" in clean_company.lower() or "wife" in clean_company.lower() else "🦊"
    send_webhook_alert(f"{icon} {clean_company} asked AI: \"{user_msg}\"")