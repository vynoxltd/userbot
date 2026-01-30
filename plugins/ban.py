# plugins/ban.py

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
    ".unban <reply/user/id> [reason]\n\n"
    "• Works in groups & channels\n"
    "• Reply / username / user id supported\n"
    "• Reason supported"
)

# =====================
# BAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ban(?: (.*))?$"))
async def ban_user(e):
    if not e.is_group:
        return

    if not await is_admin(e.chat_id):
        return

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
