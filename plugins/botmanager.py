from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    set_var, get_var, del_var,
    start_bot, stop_bot, list_running_bots,
    auto_delete, log_error,
    mark_plugin_loaded, mark_plugin_error,
    register_help        # 🔥 AUTO HELP
)
from config import API_ID, API_HASH

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("botmanager.py")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "botmanager",
    """
.addbot <name> <token>
Add a new bot

.startbot <name>
Start a bot

.stopbot <name>
Stop a running bot

.delbot <name>
Delete bot token

.bots
List running bots

• Multi-bot manager
• Safe start / stop
"""
)

# =====================
# ADD BOT
# =====================
@Client.on_message(owner_only & filters.command("addbot", "."))
async def add_bot(client, m):
    try:
        if len(m.command) < 3:
            msg = await m.reply("Usage:\n.addbot <name> <token>")
            await auto_delete(msg, 5)
            return

        name = m.command[1].lower()
        token = m.command[2]

        set_var(f"BOT_{name.upper()}", token)

        msg = await m.reply(f"✅ Bot added: `{name}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("botmanager.py", e)
        await log_error(client, "botmanager.py", e)


# =====================
# START BOT
# =====================
@Client.on_message(owner_only & filters.command("startbot", "."))
async def start_bot_cmd(client, m):
    try:
        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.startbot <name>")
            await auto_delete(msg, 5)
            return

        name = m.command[1].lower()
        token = get_var(f"BOT_{name.upper()}")

        if not token:
            msg = await m.reply("❌ Bot not found")
            await auto_delete(msg, 5)
            return

        await start_bot(name, token, API_ID, API_HASH)

        msg = await m.reply(f"🚀 Bot started: `{name}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("botmanager.py", e)
        await log_error(client, "botmanager.py", e)


# =====================
# STOP BOT
# =====================
@Client.on_message(owner_only & filters.command("stopbot", "."))
async def stop_bot_cmd(client, m):
    try:
        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.stopbot <name>")
            await auto_delete(msg, 5)
            return

        name = m.command[1].lower()
        await stop_bot(name)

        msg = await m.reply(f"🛑 Bot stopped: `{name}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("botmanager.py", e)
        await log_error(client, "botmanager.py", e)


# =====================
# LIST BOTS
# =====================
@Client.on_message(owner_only & filters.command("bots", "."))
async def bots_cmd(client, m):
    try:
        running = list_running_bots()

        if not running:
            msg = await m.reply("No bots running")
        else:
            msg = await m.reply(
                "🤖 RUNNING BOTS\n\n" +
                "\n".join(f"• {b}" for b in running)
            )

        await auto_delete(msg, 8)

    except Exception as e:
        mark_plugin_error("botmanager.py", e)
        await log_error(client, "botmanager.py", e)


# =====================
# DELETE BOT
# =====================
@Client.on_message(owner_only & filters.command("delbot", "."))
async def del_bot(client, m):
    try:
        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.delbot <name>")
            await auto_delete(msg, 5)
            return

        name = m.command[1].lower()
        del_var(f"BOT_{name.upper()}")

        msg = await m.reply(f"🗑️ Bot removed: `{name}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("botmanager.py", e)
        await log_error(client, "botmanager.py", e)
