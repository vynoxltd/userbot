import asyncio
import random
from telethon import events
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

from userbot import bot
from utils.help_registry import register_help

PLUGIN_NAME = "poem.py"
print("✔ poem.py loaded (RANDOM FUN POEMS)")

DEFAULTUSER = "ULTROID USER"

POEMS = [
    "Roses are red 🌹\n"
    "Violets are blue 💙\n"
    "Life is confusing\n"
    "And so are you 😌",

    "Roses are red 🌹\n"
    "Coffee is brown ☕\n"
    "Mondays are evil\n"
    "But we still get around 😴",

    "Roses are red 🌹\n"
    "Sky is wide 🌌\n"
    "I had motivation\n"
    "But it suddenly died 💀",

    "Roses are red 🌹\n"
    "Night feels deep 🌙\n"
    "I planned to work\n"
    "But chose to sleep 😴",

    "Roses are red 🌹\n"
    "Hope is bright ✨\n"
    "Trust the process\n"
    "You’ll be alright 💪",

    "Roses are red 🌹\n"
    "Phone is my fate 📱\n"
    "I came to study\n"
    "But started to scroll… again 😭",
]

@bot.on(events.NewMessage(pattern=r"\.dpoem$"))
async def random_poem(e):
    poem = random.choice(POEMS)

    await e.edit("✍️ Writing a poem...")
    await asyncio.sleep(2)

    await e.edit(
        f"{poem}\n\n"
        f"✍️ **{DEFAULTUSER}**"
    )

# =====================
# HELP
# =====================
register_help(
    "poem",
    ".dpoem\n\n"
    "• Sends a random fun poem\n"
    "• Safe & clean content\n"
    "• Telethon compatible"
)
