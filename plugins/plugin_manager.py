# plugins/plugin_manager.py

import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_control import enable, disable, is_enabled
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded
from utils.logger import log_error

PLUGIN_NAME = "plugin_manager"
mark_plugin_loaded(PLUGIN_NAME)

mark_plugin_loaded(PLUGIN_NAME)
print("✔ plugin_manager.py loaded")
# =====================
# HELP
# =====================
register_help(
    "plugin",
    ".plugin on <name>\n"
    ".plugin off <name>\n"
    ".pluginstatus\n\n"
    "• Enable / Disable plugins\n"
    "• Owner only\n"
    "• No restart needed"
)

# =====================
# LIST PLUGINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.pluginstatus$"))
async def list_plugins(e):
    if not is_owner(e):
        return

    try:
        from utils.plugin_control import _load
        data = _load()

        if not data:
            await e.reply("ℹ️ No plugin state data found")
            return

        text = "🧩 **PLUGIN STATUS**\n\n"
        for name, state in data.items():
            emoji = "✅" if state else "⛔"
            text += f"{emoji} `{name}`\n"

        await e.reply(text)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# ENABLE / DISABLE
# =====================
@bot.on(events.NewMessage(pattern=r"\.plugin (on|off) (\w+)$"))
async def toggle_plugin(e):
    if not is_owner(e):
        return

    try:
        action, name = e.pattern_match.groups()

        if action == "on":
            enable(name)
            await e.reply(f"✅ Plugin `{name}` enabled")
        else:
            disable(name)
            await e.reply(f"⛔ Plugin `{name}` disabled")

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
