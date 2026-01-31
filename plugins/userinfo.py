# plugins/userinfo.py

import asyncio
from datetime import datetime

from telethon import events
from telethon.tl.functions.users import GetFullUserRequest

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "userinfo.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ userinfo.py loaded")

# =====================
# HELP
# =====================
register_help(
    "userinfo",
    ".userinfo (reply / username / userid)\n\n"
    "• Shows full Telegram user info\n"
    "• Phone number if visible\n"
    "• Respects Telegram privacy\n"
    "• Works in groups & PM"
)

# =====================
# UTILS
# =====================
async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = (e.pattern_match.group(1) or "").strip()
    if not arg:
        return e.sender_id

    if arg.isdigit():
        return int(arg)

    u = await bot.get_entity(arg)
    return u.id

def yn(val):
    return "Yes ✅" if val else "No ❌"

# =====================
# USER INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.userinfo(?: (.*))?$"))
async def user_info(e):
    try:
        uid = await resolve_user(e)
        if not uid:
            return

        full = await bot(GetFullUserRequest(uid))
        user = full.user

        try:
            await e.delete()
        except:
            pass

        phone = f"+{user.phone}" if user.phone else "Hidden / Not Accessible"

        text = (
            "👤 **USER INFO**\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"👤 Name: `{(user.first_name or '')} {(user.last_name or '')}`\n"
            f"🔗 Username: `@{user.username}`\n" if user.username else
            f"👤 Name: `{(user.first_name or '')} {(user.last_name or '')}`\n"
        )

        text += (
            f"📞 Phone: `{phone}`\n\n"
            f"🤖 Bot: {yn(user.bot)}\n"
            f"⚠️ Scam: {yn(user.scam)}\n"
            f"🚨 Fake: {yn(user.fake)}\n"
            f"🕒 Last seen: `{user.status.__class__.__name__}`"
        )

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(15)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
