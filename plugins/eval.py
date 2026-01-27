from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help          # 🔥 AUTO HELP
)
import traceback

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("eval.py")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "dev",
    """
.eval <python code>

Execute python code dynamically
• Owner only
• Useful for debugging
• Errors are logged safely
"""
)

# =====================
# EVAL COMMAND
# =====================
@Client.on_message(filters.me & filters.command("eval", prefixes="."))
async def eval_cmd(client: Client, m):
    try:
        # owner_only function compatibility
        if callable(owner_only):
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

    except Exception as e:
        mark_plugin_error("eval.py", e)
        await log_error(client, "eval.py", e)
