import json
import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import bot_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

SAVE_FILE = "record.json"

def save_record(record):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=4)

def load_record():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

record = load_record()

app = Flask("")

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot_commands.setup(bot, record, save_record)
keep_alive()
bot.run(os.environ['TOKEN'])
