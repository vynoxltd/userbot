from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help          # 🔥 AUTO HELP
)
from datetime import datetime

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("alive.py")

# =====================
# HELP AUTO REGISTER
# =====================
register_help(
    "basic",
    """
.alive | exm: .alive
Check if userbot is running

.ping | exm: .ping
Simple ping test
"""
)

# =====================
# START TIME
# =====================
START_TIME = datetime.now()


def uptime():
    return str(datetime.now() - START_TIME).split(".")[0]


# =====================
# ALIVE
# =====================
@Client.on_message(owner_only & filters.command("alive", prefixes="."))
async def alive_cmd(client: Client, m):
    try:
        await m.delete()

        msg = await m.reply(
            f"✅ **Alive**\n"
            f"⏱ Uptime: `{uptime()}`"
        )
        await auto_delete(msg, 6)

    except Exception as e:
        mark_plugin_error("alive.py", e)
        await log_error(client, "alive.py", e)


# =====================
# PING
# =====================
@Client.on_message(owner_only & filters.command("ping", prefixes="."))
async def ping_cmd(client: Client, m):
    try:
        await m.delete()

        msg = await m.reply("🏓 Pong!")
        await auto_delete(msg, 4)

    except Exception as e:
        mark_plugin_error("alive.py", e)
        await log_error(client, "alive.py", e)
