from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.auto_delete import auto_delete
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

from database import settings
from config import API_ID, API_HASH

from utils.bot_manager import (
    start_bot,
    stop_bot,
    list_running_bots
)

PLUGIN_NAME = "botmanager.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ botmanager.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "botmanager",
    ".addbot NAME TOKEN\n"
    ".startbot NAME\n"
    ".stopbot NAME\n"
    ".delbot NAME\n"
    ".bots\n\n"
    "• Manage bot tokens\n"
    "• Start / Stop multiple bots\n"
    "• Owner only"
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
    d = settings.find_one({"_id": key})
    return d["value"] if d else None

def del_var(key):
    settings.delete_one({"_id": key})

# =====================
# ADD BOT
# =====================
@bot.on(events.NewMessage(pattern=r"^\.addbot(\s|$)"))
async def add_bot(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        parts = e.raw_text.split(maxsplit=2)
        if len(parts) < 3:
            msg = await e.respond("Usage:\n.addbot NAME TOKEN")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        token = parts[2]

        set_var(f"BOT_{name.upper()}", token)

        msg = await e.respond(f"✅ Bot added: `{name}`")
        await auto_delete(msg, 5)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# START BOT (FIXED)
# =====================
@bot.on(events.NewMessage(pattern=r"^\.startbot(\s|$)"))
async def start_bot_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        parts = e.raw_text.split(maxsplit=1)
        if len(parts) < 2:
            msg = await e.respond("Usage:\n.startbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        token = get_var(f"BOT_{name.upper()}")

        if not token:
            msg = await e.respond("❌ Bot not found")
            return await auto_delete(msg, 5)

        if not API_ID or not API_HASH:
            msg = await e.respond("❌ API_ID / API_HASH missing in env")
            return await auto_delete(msg, 6)

        # 🔥 ACTUAL START
        await start_bot(name, token, API_ID, API_HASH)

        msg = await e.respond(f"🚀 Bot started: `{name}`")
        await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

        msg = await e.respond(
            f"❌ Failed to start bot `{name}`\n\n"
            f"**Error:** `{ex}`"
        )
        await auto_delete(msg, 10)

# =====================
# STOP BOT
# =====================
@bot.on(events.NewMessage(pattern=r"^\.stopbot(\s|$)"))
async def stop_bot_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        parts = e.raw_text.split(maxsplit=1)
        if len(parts) < 2:
            msg = await e.respond("Usage:\n.stopbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        await stop_bot(name)

        msg = await e.respond(f"🛑 Bot stopped: `{name}`")
        await auto_delete(msg, 5)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# LIST BOTS
# =====================
@bot.on(events.NewMessage(pattern=r"^\.bots$"))
async def bots_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        bots = list_running_bots()

        if not bots:
            msg = await e.respond("🤖 No bots running")
        else:
            msg = await e.respond(
                "🤖 **RUNNING BOTS**\n\n" +
                "\n".join(f"• `{b}`" for b in bots)
            )

        await auto_delete(msg, 8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# DELETE BOT
# =====================
@bot.on(events.NewMessage(pattern=r"^\.delbot(\s|$)"))
async def del_bot_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    try:
        parts = e.raw_text.split(maxsplit=1)
        if len(parts) < 2:
            msg = await e.respond("Usage:\n.delbot NAME")
            return await auto_delete(msg, 5)

        name = parts[1].lower()
        del_var(f"BOT_{name.upper()}")

        msg = await e.respond(f"🗑 Bot removed: `{name}`")
        await auto_delete(msg, 5)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
