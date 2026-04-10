import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# ⚠️ 여기에 너 서버 ID 넣어라
GUILD_ID = 1482003697830596774  # ← 수정 필수

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=None, intents=intents)

# ---------------- 데이터 ----------------
bad_words = set()
warn = {}

ROLE_NAME = "기획팀"

# ---------------- 역할 체크 ----------------
def is_planner(member: discord.Member):
    return any(role.name == ROLE_NAME for role in member.roles)

# ---------------- 로그 ----------------
async def log(guild, msg):
    channel = discord.utils.get(guild.text_channels, name="log")
    if channel:
        await channel.send(msg)

# ---------------- 처벌 ----------------
async def punish(member, guild, word, message: discord.Message):
    uid = member.id
    warn[uid] = warn.get(uid, 0) + 1
    count = warn[uid]

    proof = (
        f"📌 원본 증거\n"
        f"유저: {member}\n"
        f"내용: {message.content}\n"
        f"채널: {message.channel}\n"
        f"링크: {message.jump_url}"
    )

    try:
        await member.send(
            f"🚨 금칙어 감지\n"
            f"단어: {word}\n"
            f"경고: {count}회\n\n"
            f"{proof}"
        )
    except:
        pass

    if count == 1:
        await log(guild, f"⚠️ 1회 경고\n{proof}")

    elif count == 2:
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=5))
        await log(guild, f"⏱ 5분 타임아웃\n{proof}")

    elif count == 3:
        await member.timeout(discord.utils.utcnow() + timedelta(days=1))
        await log(guild, f"⏱ 1일 타임아웃\n{proof}")

    elif count == 4:
        await member.timeout(discord.utils.utcnow() + timedelta(days=7))
        await log(guild, f"⏱ 1주 타임아웃\n{proof}")

    else:
        await member.timeout(discord.utils.utcnow() + timedelta(days=30))
        await log(guild, f"⏱ 1달 타임아웃\n{proof}")

# ---------------- 메시지 감지 ----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for word in bad_words:
        if word in message.content:
            await message.delete()
            await punish(message.author, message.guild, word, message)
            break

# ---------------- 슬래시 명령어 ----------------

@bot.tree.command(name="금칙어추가", description="금칙어 추가", guild=discord.Object(id=GUILD_ID))
async def add_badword(interaction: discord.Interaction, word: str):

    if not is_planner(interaction.user):
        return await interaction.response.send_message("권한 없음", ephemeral=True)

    bad_words.add(word)
    await interaction.response.send_message(f"추가됨: {word}")

@bot.tree.command(name="금칙어삭제", description="금칙어 삭제", guild=discord.Object(id=GUILD_ID))
async def remove_badword(interaction: discord.Interaction, word: str):

    if not is_planner(interaction.user):
        return await interaction.response.send_message("권한 없음", ephemeral=True)

    bad_words.discard(word)
    await interaction.response.send_message(f"삭제됨: {word}")

@bot.tree.command(name="금칙어목록", description="금칙어 목록", guild=discord.Object(id=GUILD_ID))
async def list_badword(interaction: discord.Interaction):

    if not bad_words:
        return await interaction.response.send_message("없음")

    await interaction.response.send_message(", ".join(bad_words))

# ---------------- 시작 ----------------
@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    print("슬래시 동기화 중...")
    await bot.tree.sync(guild=guild)
    print("슬래시 동기화 완료")

    print(f"로그인됨: {bot.user}")

bot.run(TOKEN)
