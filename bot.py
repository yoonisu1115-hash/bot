import discord
from discord.ext import commands
import asyncio
from datetime import timedelta
import time

from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv

# ---------------- KEEP ALIVE ----------------
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    Thread(target=run).start()

# ---------------- BOT SETUP ----------------
load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- DATA ----------------
bad_words = {}
warn_count = {}

PLAN_ROLE = "기획팀"

# ---------------- ROLE CHECK ----------------
def has_role(member):
    return any(role.name == PLAN_ROLE for role in member.roles)

# ---------------- LOG SYSTEM ----------------
async def log(guild, msg):
    channel = discord.utils.get(guild.text_channels, name="log")
    if channel:
        await channel.send(msg)

        # 기획팀 멘션
        for member in guild.members:
            if has_role(member):
                await channel.send(f"📢 {member.mention} 기획팀 알림")

# ---------------- PUNISH SYSTEM ----------------
async def punish(member, guild, word, content):
    uid = member.id
    warn_count[uid] = warn_count.get(uid, 0) + 1
    count = warn_count[uid]

    # DM 전송
    try:
        await member.send(
            f"🚨 금칙어 감지\n"
            f"사유: 금칙어 '{word}' 사용\n"
            f"내용: {content}\n"
            f"현재 경고: {count}회"
        )
    except:
        pass

    # 단계별 처벌
    if count == 1:
        await log(guild, f"⚠️ [경고]\n유저: {member}\n증거: {content}")

    elif count == 2:
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=5))
        await log(guild, f"⏱ [5분 타임아웃]\n유저: {member}\n증거: {content}")

    elif count == 3:
        await member.timeout(discord.utils.utcnow() + timedelta(days=1))
        await log(guild, f"⏱ [1일 타임아웃]\n유저: {member}\n증거: {content}")

    elif count == 4:
        await member.timeout(discord.utils.utcnow() + timedelta(days=7))
        await log(guild, f"⏱ [1주 타임아웃]\n유저: {member}\n증거: {content}")

    else:
        await member.timeout(discord.utils.utcnow() + timedelta(days=30))
        await log(guild, f"⏱ [1달 타임아웃]\n유저: {member}\n증거: {content}")

# ---------------- BAD WORD COMMANDS ----------------
@bot.command()
async def 금칙어추가(ctx, word):
    if not has_role(ctx.author):
        return await ctx.send("권한 없음")

    bad_words[word] = True
    await ctx.send(f"추가됨: {word}")

@bot.command()
async def 금칙어삭제(ctx, word):
    if not has_role(ctx.author):
        return await ctx.send("권한 없음")

    bad_words.pop(word, None)
    await ctx.send(f"삭제됨: {word}")

@bot.command()
async def 금칙어목록(ctx):
    await ctx.send(", ".join(bad_words.keys()) or "없음")

# ---------------- MESSAGE DETECT ----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for word in bad_words:
        if word in message.content:
            await message.delete()

            await punish(
                message.author,
                message.guild,
                word,
                message.content
            )
            break

    await bot.process_commands(message)

# ---------------- BAN / KICK LOG ----------------
@bot.event
async def on_member_ban(guild, user):
    await log(guild, f"🚨 [밴 발생]\n유저: {user}")

@bot.event
async def on_member_remove(member):
    await log(member.guild, f"🚪 [나감]\n유저: {member}")

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"로그인됨: {bot.user}")

# ---------------- START ----------------
keep_alive()
bot.run(TOKEN)
