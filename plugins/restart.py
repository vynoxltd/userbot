from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import os
import sys

mark_plugin_loaded("restart.py")

# 🔥 auto help for help4.py
register_help(
    "basic",
    """
.restart
exm: .restart

• Restarts the userbot safely
• Sends confirmation after restart
"""
)

@Client.on_message(owner_only & filters.command("restart", "."))
async def restart(client: Client, m):
    try:
        # 1️⃣ delete command
        await m.delete()

        # 2️⃣ restarting message
        await m.reply("♻️ Restarting userbot...")

        # 3️⃣ save chat id for after-restart message
        os.environ["RESTART_CHAT"] = str(m.chat.id)

        # 4️⃣ restart process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except Exception as e:
        # 🔥 auto-heal + health update
        mark_plugin_error("restart.py", e)
        await log_error(client, "restart.py", e)
