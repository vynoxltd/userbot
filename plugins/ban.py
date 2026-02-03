# plugins/ban.py

import time
import asyncio
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "ban.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ ban.py loaded")

# =====================
# RIGHTS (TELETHON SAFE)
# =====================
BAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=False
)

# =====================
# MUTE RIGHTS
# =====================
MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True
)
# =====================
# UNMUTE RIGHTS
# =====================
UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False
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
        return None

    if arg.isdigit():
        return int(arg)

    try:
        u = await bot.get_entity(arg)
        return u.id
    except:
        return None

async def is_admin(chat_id):
    try:
        me = await bot.get_me()
        p = await bot(GetParticipantRequest(chat_id, me.id))
        return bool(p.participant.admin_rights or p.participant.creator)
    except:
        return False

# =====================
# HELP
# =====================
register_help(
    "ban",
    ".ban <reply/user/id> [reason]\n"
    ".unban <reply/user/id> [reason]\n"
    ".mute <time> <reason>\n"
    ".unmute [reason]\n\n"
    "• Works in groups & channels\n"
    "• Reply / username / user id supported\n"
    "• Reason supported"
)

def parse_time(text):
    """
    10m, 2h, 1d → seconds
    """
    if not text:
        return None

    try:
        unit = text[-1]
        val = int(text[:-1])

        if unit == "m":
            return val * 60
        if unit == "h":
            return val * 3600
        if unit == "d":
            return val * 86400
    except:
        return None
# =====================
# BAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ban(?: (.*))?$"))
async def ban_user(e):
    # 1️⃣ Sirf group me
    if not e.is_group:
        return

    # 2️⃣ Command sirf USERBOT OWNER se
    if not is_owner(e):
        return  # silently ignore

    # 3️⃣ Userbot admin hona chahiye
    if not await is_admin(e.chat_id):
        await e.reply("❌ I am not admin here")
    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, BAN_RIGHTS))

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"🚫 **USER BANNED**\n"
            f"User: `{uid}`\n"
            f"Reason: `{reason}`"
        )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# UNBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.unban(?: (.*))?$"))
async def unban_user(e):
    if not e.is_group:
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, UNBAN_RIGHTS))

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"✅ **USER UNBANNED**\n"
            f"User: `{uid}`\n"
            f"Note: `{reason}`"
        )
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
# =====================
# MUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.mute(?: (.*))?$"))
async def mute_user(e):
    if not e.is_group:
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        args = (e.pattern_match.group(1) or "").split()
        duration = parse_time(args[0]) if args else None

        reason = " ".join(args[1:]) if duration else " ".join(args)
        reason = reason or "No reason"

        until = None
        if duration:
            until = int(time.time()) + duration

        rights = MUTE_RIGHTS
        rights.until_date = until

        await bot(EditBannedRequest(e.chat_id, uid, rights))

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"🔇 **USER MUTED**\n"
            f"User: `{uid}`\n"
            f"Duration: `{args[0] if duration else 'Permanent'}`\n"
            f"Reason: `{reason}`"
        )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
# =====================
# UNMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.unmute(?: (.*))?$"))
async def unmute_user(e):
    if not e.is_group:
        return

    if not await is_admin(e.chat_id):
        return

    try:
        uid = await resolve_user(e)
        if not uid:
            return

        reason = e.pattern_match.group(1) or "No reason"

        await bot(EditBannedRequest(e.chat_id, uid, UNMUTE_RIGHTS))

        await e.delete()
        msg = await bot.send_message(
            e.chat_id,
            f"🔊 **USER UNMUTED**\n"
            f"User: `{uid}`\n"
            f"Note: `{reason}`"
        )

        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
