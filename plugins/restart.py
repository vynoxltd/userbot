from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
import os, sys
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("restart.py")

@Client.on_message(owner_only & filters.command("restart", "."))
async def restart(_, m):
    # 1️⃣ command delete
    await m.delete()

    # 2️⃣ restarting message
    msg = await m.reply("♻️ Restarting userbot...")

    # 3️⃣ chat id save
    os.environ["RESTART_CHAT"] = str(m.chat.id)

    # 4️⃣ restart
    os.execv(sys.executable, [sys.executable] + sys.argv)