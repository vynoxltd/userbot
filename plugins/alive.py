from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete
from datetime import datetime
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("alive.py")

START_TIME = datetime.now()

def uptime():
    return str(datetime.now() - START_TIME).split(".")[0]


@Client.on_message(owner_only & filters.command("alive", prefixes="."))
async def alive(_, m):
    await m.delete()  # ❌ delete command message

    msg = await m.reply(
        f"✅ **Alive**\n"
        f"⏱ Uptime: `{uptime()}`"
    )
    await auto_delete(msg, 6)


@Client.on_message(owner_only & filters.command("ping", prefixes="."))
async def ping(_, m):
    await m.delete()  # ❌ delete command message

    msg = await m.reply("🏓 Pong!")
    await auto_delete(msg, 4)