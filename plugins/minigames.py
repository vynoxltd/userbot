import random
import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "minigames.py"

mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "minigames",
    ".guess\n"
    ".typefast\n"
    ".mathrace\n"
    ".spin\n"
    "guess\n"
    ".bomb\n"
    ".roulette\n"
    ".truthmeter\n"
    ".react\n\n"
    "• Lightweight mini games\n"
    "• No DB / No leaderboard\n"
    "• Auto delete fun 😄"
)

# =====================
# GUESS GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.guesss$"))
async def guess(e):
    try:
        await e.delete()
        num = random.randint(1, 10)
        m = await e.reply(
            "🎯 Guess the number (1-10)\n"
            f"Answer: `{num}` 😄"
        )
        await asyncio.sleep(8)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
# =====================
# TYPE FAST
# =====================
@bot.on(events.NewMessage(pattern=r"\.typefast$"))
async def typefast(e):
    try:
        await e.delete()
        word = random.choice([
            "asynchronous",
            "telethon",
            "python",
            "userbot",
            "leaderboard"
        ])
        m = await e.reply(
            "⌨️ **TYPE FAST**\n\n"
            f"`{word}`"
        )
        await asyncio.sleep(10)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# MATH RACE
# =====================
@bot.on(events.NewMessage(pattern=r"\.mathrace$"))
async def mathrace(e):
    try:
        await e.delete()
        a, b = random.randint(10, 50), random.randint(10, 50)
        m = await e.reply(
            "🧮 **MATH RACE**\n\n"
            f"{a} + {b} = ?"
        )
        await asyncio.sleep(10)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
# =====================
# 1️⃣ GUESS THE NUMBER
# =====================
@bot.on(events.NewMessage(pattern=r"\.guess$"))
async def guess(e):
    try:
        await e.delete()
        correct = random.randint(1, 5)
        user_guess = random.randint(1, 5)

        m = await e.reply(
            "🎯 **GUESS THE NUMBER**\n\n"
            f"You guessed: `{user_guess}`\n"
            f"Correct number: `{correct}`\n\n"
            + ("🎉 **YOU WON!**" if user_guess == correct else "😢 You lost")
        )
        await asyncio.sleep(8)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# 2️⃣ SPIN THE BOTTLE
# =====================
@bot.on(events.NewMessage(pattern=r"\.spin$"))
async def spin(e):
    try:
        await e.delete()
        targets = ["You 😎", "Bot 🤖", "Nobody 😅", "Someone 👀"]
        m = await e.reply("🍾 Spinning bottle...")
        await asyncio.sleep(1.5)
        await m.edit(f"🍾 **Bottle stopped at:** {random.choice(targets)}")
        await asyncio.sleep(6)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
# =====================
# 3️⃣ BOMB DEFUSE
# =====================
@bot.on(events.NewMessage(pattern=r"\.bomb$"))
async def bomb(e):
    try:
        await e.delete()
        wires = ["Red 🔴", "Blue 🔵", "Green 🟢"]
        correct = random.choice(wires)
        chosen = random.choice(wires)

        m = await e.reply(
            "💣 **BOMB DEFUSING**\n\n"
            f"You cut: {chosen}\n"
            f"Correct wire: {correct}\n\n"
            + ("✅ Bomb defused!" if chosen == correct else "💥 BOOM!")
        )
        await asyncio.sleep(8)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# 5️⃣ RUSSIAN ROULETTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.roulette$"))
async def roulette(e):
    try:
        await e.delete()
        bullet = random.randint(1, 6)
        chamber = random.randint(1, 6)

        m = await e.reply(
            "🔫 **RUSSIAN ROULETTE**\n\n"
            f"Chamber: `{chamber}`\n"
            f"Bullet: `{bullet}`\n\n"
            + ("💀 You died" if bullet == chamber else "😎 You survived")
        )
        await asyncio.sleep(8)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# 6️⃣ TRUTH METER
# =====================
@bot.on(events.NewMessage(pattern=r"\.truthmeter$"))
async def truth(e):
    try:
        await e.delete()
        percent = random.randint(1, 100)
        m = await e.reply(f"🧪 **Truth Level:** `{percent}%`")
        await asyncio.sleep(6)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# 7️⃣ FAST REACTION
# =====================
@bot.on(events.NewMessage(pattern=r"\.react$"))
async def react(e):
    try:
        await e.delete()
        wait = random.uniform(1, 3)
        m = await e.reply("⚡ Get ready...")
        await asyncio.sleep(wait)
        await m.edit("🔥 **CLICK NOW!**")
        await asyncio.sleep(2)
        await m.delete()
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
