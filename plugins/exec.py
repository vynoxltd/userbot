from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
import traceback

@Client.on_message(filters.me & filters.command("exec", prefixes="."))
async def exec_cmd(_, m):
    if not owner_only(m):
        return

    code = m.text.split(" ", 1)
    if len(code) < 2:
        await m.reply("Usage: `.exec python_code`")
        return

    try:
        exec(code[1], globals())
        await m.reply("✅ Executed successfully")
    except Exception:
        await m.reply(f"❌ Error:\n`{traceback.format_exc()}`")