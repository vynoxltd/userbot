from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
import traceback

@Client.on_message(filters.me & filters.command("eval", prefixes="."))
async def eval_cmd(_, m):
    if not owner_only(m):
        return

    code = m.text.split(" ", 1)
    if len(code) < 2:
        await m.reply("Usage: `.eval python_code`")
        return

    try:
        result = eval(code[1])
        await m.reply(f"✅ Result:\n`{result}`")
    except Exception:
        await m.reply(f"❌ Error:\n`{traceback.format_exc()}`")