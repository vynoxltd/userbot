import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from database import set_note, get_note, del_note

print("✔ notes.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "notes",
    ".setnote NAME TEXT\n"
    "Example: .setnote test hello\n\n"
    ".getnote NAME\n"
    "Example: .getnote test\n\n"
    ".delnote NAME\n"
    "Example: .delnote test\n\n"
    "• Notes are stored persistently\n"
    "• Owner only\n"
    "• Auto delete enabled"
)

# ======================
# SET NOTE
# ======================
@bot.on(events.NewMessage(pattern=r"\.setnote(?: (.*))?$"))
async def setnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        args = (e.pattern_match.group(1) or "").split(None, 1)
        if len(args) < 2:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.setnote NAME TEXT"
            )
            await asyncio.sleep(6)
            await msg.delete()
            return

        name, text = args[0], args[1]
        set_note(name, text)

        msg = await bot.send_message(e.chat_id, "✅ Note saved")
        await asyncio.sleep(5)
        await msg.delete()

    except Exception:
        await log_error(bot, "notes.py")

# ======================
# GET NOTE
# ======================
@bot.on(events.NewMessage(pattern=r"\.getnote(?: (.*))?$"))
async def getnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        name = (e.pattern_match.group(1) or "").strip()
        if not name:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.getnote NAME"
            )
            await asyncio.sleep(6)
            await msg.delete()
            return

        note = get_note(name)
        if not note:
            msg = await bot.send_message(e.chat_id, "❌ Note not found")
            await asyncio.sleep(5)
            await msg.delete()
            return

        msg = await bot.send_message(e.chat_id, note)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception:
        await log_error(bot, "notes.py")

# ======================
# DELETE NOTE
# ======================
@bot.on(events.NewMessage(pattern=r"\.delnote(?: (.*))?$"))
async def delnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        name = (e.pattern_match.group(1) or "").strip()
        if not name:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.delnote NAME"
            )
            await asyncio.sleep(6)
            await msg.delete()
            return

        del_note(name)

        msg = await bot.send_message(e.chat_id, "🗑 Note deleted")
        await asyncio.sleep(5)
        await msg.delete()

    except Exception:
        await log_error(bot, "notes.py")