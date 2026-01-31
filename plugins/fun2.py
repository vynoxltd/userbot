# plugins/fun2.py

import asyncio
import random
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.owner import is_owner

PLUGIN_NAME = "fun2.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun2.py loaded (FUN + ANIMATION MODE)")

# =====================
# HELP
# =====================
register_help(
    "fun2",
    ".hack\n"
    ".hackip\n"
    ".decrypt\n"
    ".scan\n"
    ".pingpong\n\n"
    "• Fake hacking animations\n"
    "• Table tennis game\n"
    "• Message edit effects\n"
    "• Just for fun 😄"
)

# =====================
# UTILS
# =====================
async def animate(msg, frames, delay=0.7):
    for f in frames:
        await msg.edit(f)
        await asyncio.sleep(delay)

# =====================
# FAKE HACK GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.hack$"))
async def hack_game(e):
    try:
        m = await e.reply("💻 Initializing hack module...")
        frames = [
            "💻 Connecting to server █▒▒▒▒▒▒▒ 10%",
            "💻 Bypassing firewall ███▒▒▒▒▒ 30%",
            "💻 Injecting payload █████▒▒▒ 55%",
            "💻 Cracking password ███████▒ 78%",
            "💻 Access granted █████████ 100%",
            "✅ **HACK COMPLETE**\n\n🔓 System owned 😎"
        ]
        await animate(m, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# FAKE IP HACK
# =====================
@bot.on(events.NewMessage(pattern=r"\.hackip$"))
async def hack_ip(e):
    try:
        fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        m = await e.reply("📡 Locating IP address...")
        frames = [
            f"📡 Tracing route to {fake_ip}",
            "🛰 Accessing satellite uplink...",
            "🔍 Scanning open ports...",
            "⚠️ Firewall detected",
            "✅ IP TRACE COMPLETE\n\n"
            f"🌍 IP: `{fake_ip}`\n"
            "📍 Location: Unknown 😏"
        ]
        await animate(m, frames, 0.9)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# DECRYPT GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.decrypt$"))
async def decrypt_game(e):
    try:
        m = await e.reply("🔐 Starting decryption engine...")
        frames = [
            "🔐 Loading AES module...",
            "🔐 Bruteforce running ░░░░░░░",
            "🔐 Bruteforce running ███░░░░",
            "🔐 Bruteforce running ██████░",
            "🔓 DECRYPTION SUCCESSFUL",
            "📂 File unlocked ✔️"
        ]
        await animate(m, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# SCAN GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.scan$"))
async def scan_game(e):
    try:
        m = await e.reply("🧪 Running system scan...")
        frames = [
            "🧪 Checking memory...",
            "🧪 Checking CPU...",
            "🧪 Checking network...",
            "🧪 Checking security...",
            "✅ Scan complete\n\n🟢 No threats found"
        ]
        await animate(m, frames, 0.7)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# PING PONG GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.pingpong$"))
async def pingpong_game(e):
    try:
        m = await e.reply("🏓 Starting Table Tennis...")

        frames = [
            "🏓 |●        |",
            "🏓 |  ●      |",
            "🏓 |    ●    |",
            "🏓 |      ●  |",
            "🏓 |        ●|",
            "🏓 |      ●  |",
            "🏓 |    ●    |",
            "🏓 |  ●      |",
        ]

        score_a = 0
        score_b = 0

        for _ in range(3):
            for f in frames:
                await m.edit(
                    f"🎮 **TABLE TENNIS**\n\n"
                    f"`{f}`\n\n"
                    f"Player A: `{score_a}`\n"
                    f"Player B: `{score_b}`"
                )
                await asyncio.sleep(0.35)

            score_a += 1

            for f in reversed(frames):
                await m.edit(
                    f"🎮 **TABLE TENNIS**\n\n"
                    f"`{f}`\n\n"
                    f"Player A: `{score_a}`\n"
                    f"Player B: `{score_b}`"
                )
                await asyncio.sleep(0.35)

            score_b += 1

        await m.edit(
            "🏁 **MATCH OVER** 🏓\n\n"
            f"Final Score\n"
            f"Player A: `{score_a}`\n"
            f"Player B: `{score_b}`\n\n"
            "GG 😄"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
