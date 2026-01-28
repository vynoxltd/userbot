import traceback
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

# =====================
# PLUGIN LOAD
# =====================
print("✔ eval.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "dev",
    ".eval PYTHON_CODE\n\n"
    "Execute python code dynamically\n"
    "• Owner only\n"
    "• Useful for debugging\n"
    "• Errors are logged safely"
)

# =====================
# EVAL COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.eval(?: (.*))?$"))
async def eval_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        code = e.pattern_match.group(1)
        if not code:
            return await bot.send_message(
                e.chat_id,
                "Usage:\n.eval PYTHON_CODE"
            )

        # limited local scope for safety
        local_vars = {
            "bot": bot,
            "event": e
        }

        try:
            result = eval(code, {}, local_vars)
            if result is None:
                output = "Executed successfully"
            else:
                output = str(result)

            await bot.send_message(
                e.chat_id,
                f"✅ Result:\n{output}"
            )

        except Exception:
            err = traceback.format_exc()
            await bot.send_message(
                e.chat_id,
                f"❌ Error:\n{err}"
            )

    except Exception:
        await log_error(bot, "eval.py")