from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.auto_delete import auto_delete
from database import settings
from config import API_ID, API_HASH

from utils.bot_manager import (
    start_bot,
    stop_bot,
    list_running_bots
)

# =====================
# PLUGIN LOAD
# =====================
print("✔ botmanager.py loaded")

# =====================
# AUTO HELP REGISTER (NO < >)
# =====================
register_help(
    "botmanager",
    ".addbot NAME TOKEN\n"
    "Add a new bot token\n\n"
    ".startbot NAME\n"
    "Start a saved bot\n\n"
    ".stopbot NAME\n"
    "Stop a running bot\n\n"
    ".delbot NAME\n"
    "Delete saved bot token\n\n"
    ".bots\n"
    "List running bots"
)

# =====================
# DB HELPERS
# =====================
def set_var(key, value):
    settings.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )

def get_var(key):
    doc = settings.find_one({"_id": key})
    return doc["value"] if doc else None

def del_var(key):
    settings.delete_one({"_id": key})

# =====================
# ADD BOT
# =====================
@bot.on(events.NewMessage(pattern=r"\.addbot"))
async def add_bot(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        parts = e.raw_text.split(maxsplit=2)

        if len(parts) < 3:
            msg = await e.respond("Usage:\n.addbot NAME TOKEN")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        token = parts[2]

        set_var(f"BOT_{name.upper()}", token)

        msg = await e.respond(f"✅ Bot added: {name}")
        await auto_delete(msg, 5)

    except Exception:
        await log_error(bot, "botmanager.py")

# =====================
# START BOT
# =====================
@bot.on(events.NewMessage(pattern=r"\.startbot"))
async def start_bot_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        parts = e.raw_text.split(maxsplit=1)

        if len(parts) < 2:
            msg = await e.respond("Usage:\n.startbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        token = get_var(f"BOT_{name.upper()}")

        if not token:
            msg = await e.respond("❌ Bot not found")
            return await auto_delete(msg, 5)

        await start_bot(name, token, API_ID, API_HASH)

        msg = await e.respond(f"🚀 Bot started: {name}")
        await auto_delete(msg, 5)

    except Exception:
        await log_error(bot, "botmanager.py")

# =====================
# STOP BOT
# =====================
@bot.on(events.NewMessage(pattern=r"\.stopbot"))
async def stop_bot_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        parts = e.raw_text.split(maxsplit=1)

        if len(parts) < 2:
            msg = await e.respond("Usage:\n.stopbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        await stop_bot(name)

        msg = await e.respond(f"🛑 Bot stopped: {name}")
        await auto_delete(msg, 5)

    except Exception:
        await log_error(bot, "botmanager.py")

# =====================
# LIST BOTS
# =====================
@bot.on(events.NewMessage(pattern=r"\.bots$"))
async def bots_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        running = list_running_bots()

        if not running:
            msg = await e.respond("No bots running")
        else:
            msg = await e.respond(
                "🤖 RUNNING BOTS\n\n" +
                "\n".join(f"• {b}" for b in running)
            )

        await auto_delete(msg, 8)

    except Exception:
        await log_error(bot, "botmanager.py")

# =====================
# DELETE BOT
# =====================
@bot.on(events.NewMessage(pattern=r"\.delbot"))
async def del_bot(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        parts = e.raw_text.split(maxsplit=1)

        if len(parts) < 2:
            msg = await e.respond("Usage:\n.delbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        del_var(f"BOT_{name.upper()}")

        msg = await e.respond(f"🗑 Bot removed: {name}")
        await auto_delete(msg, 5)

    except Exception:
        await log_error(bot, "botmanager.py")