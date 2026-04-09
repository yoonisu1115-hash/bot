import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True  # 👈 이거 필수!

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- 준비 --------------------
@bot.event
async def on_ready():
    print(f"✅ 로그인됨: {bot.user}")

# -------------------- 밴 감지 --------------------
@bot.event
async def on_member_ban(guild, user):
    channel = discord.utils.get(guild.text_channels, name="log")

    if not channel:
        return

    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                await channel.send(
                    f"🚨 [밴]\n👤 유저: {user}\n👮 관리자: {entry.user}"
                )
                return
    except:
        pass

    await channel.send(f"🚨 [밴]\n👤 유저: {user} (관리자 확인 불가)")

# -------------------- 킥 + 나감 감지 --------------------
@bot.event
async def on_member_remove(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name="log")

    if not channel:
        return

    await asyncio.sleep(1)  # 감사 로그 반영 대기

    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                await channel.send(
                    f"👢 [킥]\n👤 유저: {member}\n👮 관리자: {entry.user}"
                )
                return

        # 킥 로그 없으면 그냥 나간 것
        await channel.send(f"🚪 [나감]\n👤 유저: {member}")

    except:
        await channel.send(f"⚠️ {member} 나감 (확인 불가)")

# -------------------- 실행 --------------------
bot.run("MTQ5MTQwMDM2MzM3NzY5Mjg0Mw.Gevlu8.PuwYpG_1y_6ahvwtb-lLJKwyPREPIIVLLsPkSk")