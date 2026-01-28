import traceback
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error

# =====================
# PLUGIN LOAD
# =====================
print("✔ exec.py loaded")

# =====================
# EXEC COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.exec(?: (.*))?$"))
async def exec_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        code = e.pattern_match.group(1)
        if not code:
            return await bot.send_message(
                e.chat_id,
                "Usage:\n.exec PYTHON_CODE"
            )

        # restricted globals for safety
        exec_globals = {
            "bot": bot,
            "event": e
        }

        try:
            exec(code, exec_globals)
            await bot.send_message(
                e.chat_id,
                "✅ Executed successfully"
            )

        except Exception:
            err = traceback.format_exc(limit=4)
            await bot.send_message(
                e.chat_id,
                f"❌ Error:\n{err}"
            )

    except Exception:
        await log_error(bot, "exec.py")