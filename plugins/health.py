from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.plugin_status import get_broken_plugins, mark_plugin_loaded
from utils.health import get_uptime, mongo_status

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("health.py")
print("✔ health.py loaded")

# =====================
# HEALTH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.health$"))
async def health_handler(e):
    if not is_owner(e):
        return

    broken = get_broken_plugins()

    if not broken:
        text = (
            "🩺 **Userbot Health**\n\n"
            f"⏱ **Uptime:** {get_uptime()}\n"
            f"🗄 **MongoDB:** {mongo_status()}\n\n"
            "✅ **All plugins working fine**"
        )
        await e.reply(text)
        return

    text = (
        "🩺 **Userbot Health**\n\n"
        f"⏱ **Uptime:** {get_uptime()}\n"
        f"🗄 **MongoDB:** {mongo_status()}\n\n"
        "❌ **Broken Plugins:**\n"
    )

    for name, info in broken.items():
        text += f"\n• **{name}**\n`{info['error'][:400]}`"

    await e.reply(text)
