from plugins.utils import log_error
from pyrogram import Client, filters
from database import get_setting, set_setting
from plugins.owner import owner_only
from plugins.utils import auto_delete
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("autoreply.py")

@Client.on_message(owner_only & filters.command("autoreply", prefixes="."))
async def toggle_autoreply(_, m):
    # 🔥 command delete
    await m.delete()

    # no argument → show status
    if len(m.command) < 2:
        status = "ON ✅" if get_setting("autoreply") else "OFF ❌"
        msg = await m.reply(f"🤖 Auto-reply is currently: **{status}**")
        await auto_delete(msg, 5)
        return

    arg = m.command[1].lower()

    if arg in ("on", "1", "true"):
        set_setting("autoreply", 1)
        msg = await m.reply("✅ Auto-reply enabled")

    elif arg in ("off", "0", "false"):
        set_setting("autoreply", 0)
        msg = await m.reply("❌ Auto-reply disabled")

    else:
        msg = await m.reply("⚠️ Usage: `.autoreply on / off`")

    # ⏱ auto delete final message
    await auto_delete(msg, 5)