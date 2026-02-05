# plugins/afk.py

import asyncio
from datetime import datetime
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "afk.py"
print("✔ afk.py loaded (SMART AFK + AUTO OFF)")

AFK = {
    "on": False,
    "since": None,
    "reason": None,
}
REPLIED = set()

# =====================
# HELP
# =====================
register_help(
    "afk",
    ".afk [reason]\n\n"
    "• Auto AFK\n"
    "• Auto OFF on message\n"
    "• First reply only\n"
)

# =====================
# AFK ON
# =====================
@bot.on(events.NewMessage(pattern=r"\.afk(?:\s+(.*))?$"))
async def afk_on(e):
    global AFK, REPLIED

    AFK["on"] = True
    AFK["since"] = datetime.utcnow()
    AFK["reason"] = e.pattern_match.group(1) or "AFK"
    REPLIED.clear()

    await e.edit(
        f"😴 **AFK enabled**\n"
        f"Reason: `{AFK['reason']}`"
    )

# =====================
# AUTO OFF (OWNER MESSAGE)
# =====================
@bot.on(events.NewMessage(outgoing=True))
async def afk_auto_off(e):
    global AFK, REPLIED

    if not AFK["on"]:
        return

    # ignore .afk command itself
    if e.raw_text.startswith(".afk"):
        return

    AFK["on"] = False
    AFK["since"] = None
    AFK["reason"] = None
    REPLIED.clear()

    msg = await e.respond("✅ **AFK disabled (you are back)**")
    await asyncio.sleep(3)
    await msg.delete()

# =====================
# AFK AUTO REPLY
# =====================
@bot.on(events.NewMessage(incoming=True))
async def afk_reply(e):
    try:
        if not AFK["on"]:
            return

        if e.sender_id == (await bot.get_me()).id:
            return

        # reply only in DM or mention
        if not e.is_private and not e.mentioned:
            return

        uid = e.sender_id
        if uid in REPLIED:
            return

        REPLIED.add(uid)

        mins = int((datetime.utcnow() - AFK["since"]).total_seconds() // 60)
        text = (
            "😴 **AFK MODE**\n\n"
            f"Reason: `{AFK['reason']}`\n"
            f"Away since: `{mins} min`\n\n"
            "I’ll reply soon 👋"
        )

        m = await e.reply(text)
        await asyncio.sleep(5)
        await m.delete()

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
