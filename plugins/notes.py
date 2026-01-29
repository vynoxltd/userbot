# plugins/notes.py

import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from database.notes import set_note, get_note, del_note, all_notes

PLUGIN_NAME = "notes.py"
print("✔ notes.py loaded")
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP REGISTER
# =====================
register_help(
    "notes",
    ".setnote NAME TEXT\n"
    ".getnote NAME\n"
    ".delnote NAME\n"
    ".notes\n\n"
    "• Notes are stored in MongoDB\n"
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
            msg = await bot.send_message(e.chat_id, "Usage:\n.setnote NAME TEXT")
            await asyncio.sleep(6)
            return await msg.delete()

        name, text = args
        set_note(name, text)

        msg = await bot.send_message(e.chat_id, "✅ Note saved")
        await asyncio.sleep(5)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

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
            msg = await bot.send_message(e.chat_id, "Usage:\n.getnote NAME")
            await asyncio.sleep(6)
            return await msg.delete()

        note = get_note(name)
        if not note:
            msg = await bot.send_message(e.chat_id, "❌ Note not found")
            await asyncio.sleep(5)
            return await msg.delete()

        msg = await bot.send_message(e.chat_id, note)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

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
            msg = await bot.send_message(e.chat_id, "Usage:\n.delnote NAME")
            await asyncio.sleep(6)
            return await msg.delete()

        del_note(name)
        msg = await bot.send_message(e.chat_id, "🗑 Note deleted")
        await asyncio.sleep(5)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# ======================
# LIST NOTES
# ======================
@bot.on(events.NewMessage(pattern=r"\.notes$"))
async def list_notes(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        notes = all_notes()

        if not notes:
            msg = await bot.send_message(e.chat_id, "📭 No notes saved")
            await asyncio.sleep(6)
            return await msg.delete()

        text = "🗒 **Saved Notes**\n\n"
        for i, name in enumerate(notes.keys(), 1):
            text += f"{i}. `{name}`\n"

        text += f"\n📊 Total: {len(notes)} notes"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
