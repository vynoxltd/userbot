# plugins/moderation.py

import time
import json
import os
import asyncio
from datetime import datetime

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.tl.types import ChatBannedRights

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "moderation.py"
DATA_FILE = "utils/moderation_data.json"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded (FULL & STABLE)")

# =====================
# STORAGE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"gmutes": {}, "gbans": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load()

# =====================
# TIME UTILS
# =====================
def now():
    return int(time.time())

def parse_time(t):
    if not t:
        return None
    try:
        n = int(t[:-1])
        u = t[-1]
        return (
            n * 60 if u == "m" else
            n * 3600 if u == "h" else
            n * 86400 if u == "d" else None
        )
    except:
        return None

# =====================
# USER RESOLVE
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

# =====================
# ADMIN CHECK
# =====================
async def is_admin(chat_id):
    try:
        me = await bot.get_me()
        p = await bot(GetParticipantRequest(chat_id, me.id))
        return bool(p.participant.admin_rights or p.participant.creator)
    except:
        return False

# =====================
# RIGHTS
# =====================
MUTE = ChatBannedRights(send_messages=True)
UNMUTE = ChatBannedRights(send_messages=False)
BAN = ChatBannedRights(view_messages=True)
UNBAN = ChatBannedRights(view_messages=False)

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".gmute [10m|1h|1d] [reason]\n"
    ".ungmute <user>\n"
    ".gban <user> [reason]\n"
    ".ungban <user>\n"
    ".gbaninfo <user>\n"
    ".gmutelist\n"
    ".gbanlist\n\n"
    "• REAL global moderation\n"
    "• Auto-unmute (gmute only)\n"
    "• Works in all groups/channels where you are admin\n"
    "• Reason supported"
)

# =====================
# GMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmute(?: (\S+))?(?: (.*))?$"))
async def gmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    dur = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"

    DATA["gmutes"][str(uid)] = {
        "until": now() + dur if dur else None,
        "reason": reason,
        "time": now()
    }
    save()

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🔕 **GLOBAL MUTE**\n"
        f"User: `{uid}`\n"
        f"Duration: `{e.pattern_match.group(1) or 'Permanent'}`\n"
        f"Reason: `{reason}`"
    )
    await asyncio.sleep(6)
    await msg.delete()

# =====================
# UNGMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungmute(?: (.*))?$"))
async def ungmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gmutes"].pop(str(uid), None)
    save()

    await e.delete()
    msg = await bot.send_message(e.chat_id, f"🔔 **GLOBAL MUTE REMOVED**\nUser: `{uid}`")
    await asyncio.sleep(6)
    await msg.delete()

# =====================
# GBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    reason = e.pattern_match.group(1) or "No reason"
    DATA["gbans"][str(uid)] = {"time": now(), "reason": reason}
    save()

    async for d in bot.iter_dialogs():
        if not (d.is_group or d.is_channel):
            continue
        if not await is_admin(d.id):
            continue
        try:
            await bot(EditBannedRequest(d.id, uid, BAN))
        except:
            pass

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🚫 **GLOBAL BAN**\nUser: `{uid}`\nReason: `{reason}`"
    )
    await asyncio.sleep(6)
    await msg.delete()

# =====================
# UNGBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gbans"].pop(str(uid), None)
    save()

    async for d in bot.iter_dialogs():
        if not (d.is_group or d.is_channel):
            continue
        if not await is_admin(d.id):
            continue
        try:
            await bot(EditBannedRequest(d.id, uid, UNBAN))
        except:
            pass

    await e.delete()
    msg = await bot.send_message(e.chat_id, f"✅ **GLOBAL BAN REMOVED**\nUser: `{uid}`")
    await asyncio.sleep(6)
    await msg.delete()

# =====================
# GBAN INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.gbaninfo(?: (.*))?$"))
async def gbaninfo(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    data = DATA["gbans"].get(str(uid))

    await e.delete()

    if not data:
        msg = await bot.send_message(
            e.chat_id,
            f"ℹ️ User `{uid}` is **NOT globally banned**"
        )
        await asyncio.sleep(6)
        await msg.delete()
        return

    msg = await bot.send_message(
        e.chat_id,
        "🚫 **GBAN INFO**\n\n"
        f"User: `{uid}`\n"
        f"Banned at: `{datetime.fromtimestamp(data['time']).strftime('%d %b %Y %I:%M %p')}`\n"
        f"Reason: `{data.get('reason')}`"
    )
    await asyncio.sleep(10)
    await msg.delete()

# =====================
# LISTS
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmutelist$"))
async def gmutelist(e):
    if not is_owner(e):
        return

    txt = "🔕 **GLOBAL MUTES**\n\n"
    for u, d in DATA["gmutes"].items():
        txt += f"• `{u}` → {d.get('reason')}\n"

    await e.reply(txt or "No global mutes")

@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return

    txt = "🚫 **GLOBAL BANS**\n\n"
    for u, d in DATA["gbans"].items():
        txt += f"• `{u}` → {d.get('reason')}\n"

    await e.reply(txt or "No global bans")

# =====================
# WATCHER (AUTO ENFORCE)
# =====================
@bot.on(events.NewMessage(incoming=True))
async def moderation_watcher(e):
    try:
        uid = str(e.sender_id)

        # GBAN
        if uid in DATA["gbans"]:
            await e.delete()
            return

        # GMUTE
        gm = DATA["gmutes"].get(uid)
        if gm:
            if gm["until"] and now() > gm["until"]:
                DATA["gmutes"].pop(uid, None)
                save()
            else:
                await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
