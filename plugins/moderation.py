# plugins/moderation.py

import time
import asyncio
from datetime import datetime

from telethon import events
from telethon.tl.functions.channels import (
    EditBannedRequest,
    GetParticipantRequest
)
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

import json
import os

PLUGIN_NAME = "moderation.py"
DATA_FILE = "utils/moderation_data.json"

# =====================
# LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded")

# =====================
# STORAGE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"mutes": {}, "gmutes": {}, "bans": {}, "gbans": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

DATA = load()

# =====================
# UTILS
# =====================
def ts():
    return int(time.time())

def parse_time(t):
    if not t:
        return None
    unit = t[-1]
    num = int(t[:-1])
    return (
        num * 60 if unit == "m" else
        num * 3600 if unit == "h" else
        num * 86400 if unit == "d" else None
    )

async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id
    arg = (e.pattern_match.group(1) or "").strip()
    if not arg:
        return None
    if arg.isdigit():
        return int(arg)
    u = await bot.get_entity(arg)
    return u.id

async def is_admin(chat, uid):
    try:
        p = await bot(GetParticipantRequest(chat, uid))
        return p.participant.admin_rights or p.participant.creator
    except:
        return False

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".block / .unblock (reply/user/id)\n"
    ".mute [10m|1h|1d] (reply)\n"
    ".unmute (reply)\n"
    ".gmute / .ungmute\n"
    ".ban / .unban\n"
    ".gban / .ungban\n"
    ".mutelist / .gmutelist\n\n"
    "• Time + permanent mute\n"
    "• Reason supported\n"
    "• Group + global moderation"
)

# =====================
# RIGHTS
# =====================
MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False
)

# =====================
# MUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.mute(?: (\S+))?(?: (.*))?$"))
async def mute_user(e):
    if not e.is_group or not await is_admin(e.chat_id, e.sender_id):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    duration = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"

    until = ts() + duration if duration else None

    DATA["mutes"][f"{e.chat_id}:{uid}"] = {
        "until": until,
        "reason": reason
    }
    save(DATA)

    await bot(EditBannedRequest(e.chat_id, uid, MUTE_RIGHTS))
    await e.reply("🔇 User muted")

# =====================
# UNMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.unmute(?: (.*))?$"))
async def unmute_user(e):
    if not e.is_group or not await is_admin(e.chat_id, e.sender_id):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    DATA["mutes"].pop(f"{e.chat_id}:{uid}", None)
    save(DATA)

    await bot(EditBannedRequest(e.chat_id, uid, UNMUTE_RIGHTS))
    await e.reply("🔊 User unmuted")

# =====================
# GMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmute(?: (.*))?$"))
async def gmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gmutes"][str(uid)] = {"time": ts()}
    save(DATA)
    await e.reply("🔕 Global mute applied")

@bot.on(events.NewMessage(pattern=r"\.ungmute(?: (.*))?$"))
async def ungmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gmutes"].pop(str(uid), None)
    save(DATA)
    await e.reply("🔔 Global mute removed")

# =====================
# GBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gbans"][str(uid)] = {"time": ts()}
    save(DATA)
    await e.reply("🚫 Global ban applied")

@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gbans"].pop(str(uid), None)
    save(DATA)
    await e.reply("✅ Global ban removed")

# =====================
# WATCHER (AUTO)
# =====================
@bot.on(events.NewMessage(incoming=True))
async def moderation_watcher(e):
    try:
        uid = e.sender_id

        if str(uid) in DATA["gbans"]:
            await e.delete()
            return

        if str(uid) in DATA["gmutes"]:
            await e.delete()
            return

        key = f"{e.chat_id}:{uid}"
        mute = DATA["mutes"].get(key)

        if mute:
            if mute["until"] and ts() > mute["until"]:
                DATA["mutes"].pop(key, None)
                save(DATA)
                await bot(EditBannedRequest(e.chat_id, uid, UNMUTE_RIGHTS))
            else:
                await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
