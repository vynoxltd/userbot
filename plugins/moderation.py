import time
import json
import os
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
# LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ moderation.py loaded")

# =====================
# STORAGE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"mutes": {}, "gmutes": {}, "gbans": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

DATA = load()

# =====================
# UTILS
# =====================
def now():
    return int(time.time())

def parse_time(t):
    if not t:
        return None
    try:
        n = int(t[:-1])
        u = t[-1]
        return n * 60 if u == "m" else n * 3600 if u == "h" else n * 86400 if u == "d" else None
    except:
        return None

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
        return bool(p.participant.admin_rights or p.participant.creator)
    except:
        return False

# =====================
# RIGHTS
# =====================
MUTE = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE = ChatBannedRights(until_date=None, send_messages=False)
BAN = ChatBannedRights(until_date=None, view_messages=True)
UNBAN = ChatBannedRights(until_date=None, view_messages=False)

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".mute [10m|1h|1d] [reason]\n"
    ".unmute\n"
    ".gmute [10m|1h|1d] [reason]\n"
    ".ungmute\n"
    ".ban / .unban\n"
    ".gban / .ungban\n"
    ".mutelist\n"
    ".gmutelist\n"
    ".gbanlist\n\n"
    "• Group + Global moderation\n"
    "• Time based auto-unmute (gmute only)\n"
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
    dur = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"

    DATA["gmutes"][str(uid)] = {
        "until": now() + dur if dur else None,
        "reason": reason,
        "time": now()
    }
    save(DATA)

    await e.delete()
    await e.respond(
        f"🔕 **Global Mute**\nUser: `{uid}`\n"
        f"Duration: `{e.pattern_match.group(1) or 'Permanent'}`\n"
        f"Reason: `{reason}`"
    )

@bot.on(events.NewMessage(pattern=r"\.ungmute(?: (.*))?$"))
async def ungmute(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    DATA["gmutes"].pop(str(uid), None)
    save(DATA)
    await e.delete()
    await e.respond("🔔 Global mute removed")

# =====================
# GBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    DATA["gbans"][str(uid)] = {"time": now()}
    save(DATA)
    await e.delete()
    await e.respond("🚫 Global ban applied")

@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return
    uid = await resolve_user(e)
    DATA["gbans"].pop(str(uid), None)
    save(DATA)
    await e.delete()
    await e.respond("✅ Global ban removed")

# =====================
# LISTS
# =====================
@bot.on(events.NewMessage(pattern=r"\.gmutelist$"))
async def gmutelist(e):
    if not is_owner(e):
        return
    text = "🔕 **Global Mutes**\n\n"
    for uid, d in DATA["gmutes"].items():
        text += f"• `{uid}` → {d.get('reason','')}\n"
    await e.reply(text or "Empty")

@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return
    text = "🚫 **Global Bans**\n\n"
    for uid in DATA["gbans"]:
        text += f"• `{uid}`\n"
    await e.reply(text or "Empty")

# =====================
# WATCHER
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
                save(DATA)
                return
            await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
