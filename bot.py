import discord
from discord.ext import commands
import asyncio

from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

# ----------------- keep alive -----------------
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------- bot -----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 로그인됨: {bot.user}")

# ----------------- ban detect -----------------
@bot.event
async def on_member_ban(guild, user):
    channel = discord.utils.get(guild.text_channels, name="log")

    if not channel:
        return

    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                await channel.send(f"🚨 [밴]\n👤 {user}\n👮 {entry.user}")
                return
    except:
        pass

    await channel.send(f"🚨 [밴]\n👤 {user}")

# ----------------- kick + leave -----------------
@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name="log")

    if not channel:
        return

    await asyncio.sleep(1)

    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                await channel.send(f"👢 [킥]\n👤 {member}\n👮 {entry.user}")
                return

        await channel.send(f"🚪 [나감]\n👤 {member}")

    except:
        await channel.send(f"⚠️ {member} 나감")

# ----------------- start -----------------
keep_alive()
bot.run(TOKEN)
