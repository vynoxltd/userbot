import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.auto_delete import auto_delete
from database import set_note, get_note, del_note, all_notes

PLUGIN_NAME = "notes.py"
print("✔ notes.py loaded")

MAX_LEN = 3500  # telegram safe

# =====================
# HELP REGISTER
# =====================
register_help(
    "notes",
    ".setnote NAME TEXT\n"
    ".setnote force NAME TEXT\n\n"
    ".getnote NAME\n"
    ".delnote NAME\n"
    ".notes\n\n"
    "• Persistent notes (MongoDB)\n"
    "• Owner only\n"
    "• Safe & auto delete enabled"
)

# =====================
# SAFE SEND (LONG)
# =====================
async def send_long(chat_id, text, delete_after=15):
    msgs = []
    for i in range(0, len(text), MAX_LEN):
        msg = await bot.send_message(chat_id, text[i:i + MAX_LEN])
        msgs.append(msg)

    for m in msgs:
        await auto_delete(m, delete_after)

# =====================
# SET NOTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.setnote(?: (.*))?$"))
async def setnote(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        raw = (e.pattern_match.group(1) or "").strip()

        if not raw:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.setnote NAME TEXT\n.setnote force NAME TEXT"
            )
            return await auto_delete(msg, 6)

        force = False
        if raw.startswith("force "):
            force = True
            raw = raw[6:]

        parts = raw.split(None, 1)
        if len(parts) < 2:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.setnote NAME TEXT"
            )
            return await auto_delete(msg, 6)

        name, text = parts[0], parts[1]

        if get_note(name) and not force:
            msg = await bot.send_message(
                e.chat_id,
                "⚠️ Note already exists\nUse `.setnote force NAME TEXT`"
            )
            return await auto_delete(msg, 6)

        set_note(name, text)

        msg = await bot.send_message(e.chat_id, "✅ Note saved")
        await auto_delete(msg, 5)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# GET NOTE
# =====================
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
            return await auto_delete(msg, 6)

        note = get_note(name)
        if not note:
            msg = await bot.send_message(e.chat_id, "❌ Note not found")
            return await auto_delete(msg, 5)

        await send_long(e.chat_id, note, delete_after=15)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# DELETE NOTE
# =====================
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
            return await auto_delete(msg, 6)

        if not get_note(name):
            msg = await bot.send_message(e.chat_id, "❌ Note not found")
            return await auto_delete(msg, 5)

        del_note(name)

        msg = await bot.send_message(e.chat_id, "🗑 Note deleted")
        await auto_delete(msg, 5)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# LIST NOTES
# =====================
@bot.on(events.NewMessage(pattern=r"\.notes$"))
async def list_notes(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        notes = all_notes()

        if not notes:
            msg = await bot.send_message(e.chat_id, "📭 No notes found")
            return await auto_delete(msg, 5)

        text = "📝 **Saved Notes:**\n\n"
        for name in sorted(notes.keys()):
            text += f"• `{name}`\n"

        await send_long(e.chat_id, text, delete_after=15)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
