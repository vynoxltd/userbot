# plugins/moderation.py

import time
import json
import os

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
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
print("✔ moderation.py loaded")

# =====================
# STORAGE
# =====================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"gmutes": {}, "gbans": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load_data()

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

    u = await bot.get_entity(arg)
    return u.id

# =====================
# TELETHON SAFE RIGHTS
# =====================
MUTE = ChatBannedRights(
    until_date=None,
    send_messages=True
)

UNMUTE = ChatBannedRights(
    until_date=None,
    send_messages=False
)

BAN = ChatBannedRights(
    until_date=None,
    view_messages=True
)

UNBAN = ChatBannedRights(
    until_date=None,
    view_messages=False
)

# =====================
# HELP
# =====================
register_help(
    "moderation",
    ".gmute [10m|1h|1d] [reason]\n"
    ".ungmute\n"
    ".gban [reason]\n"
    ".ungban\n"
    ".gmutelist\n"
    ".gbanlist\n\n"
    "• REAL global moderation\n"
    "• Auto-unmute (gmute only)\n"
    "• Multi-group ban/mute\n"
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

    duration = parse_time(e.pattern_match.group(1))
    reason = e.pattern_match.group(2) or "No reason"

    DATA["gmutes"][str(uid)] = {
        "until": now() + duration if duration else None,
        "reason": reason,
        "time": now()
    }
    save_data()

    await e.delete()
    await e.respond(
        f"🔕 **GMUTED**\n"
        f"User: `{uid}`\n"
        f"Duration: `{e.pattern_match.group(1) or 'Permanent'}`\n"
        f"Reason: `{reason}`"
    )

# =====================
# UNGMUTE
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungmute(?: (.*))?$"))
async def ungmute(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gmutes"].pop(str(uid), None)
    save_data()

    await e.delete()
    await e.respond("🔔 Global mute removed")

# =====================
# GBAN (REAL GROUP BAN)
# =====================
@bot.on(events.NewMessage(pattern=r"\.gban(?: (.*))?$"))
async def gban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    reason = e.pattern_match.group(1) or "No reason"

    DATA["gbans"][str(uid)] = {
        "time": now(),
        "reason": reason
    }
    save_data()

    async for d in bot.iter_dialogs():
        if d.is_group or d.is_channel:
            try:
                await bot(EditBannedRequest(d.id, uid, BAN))
            except:
                pass

    await e.delete()
    await e.respond(f"🚫 **GBANNED** `{uid}`\nReason: `{reason}`")

# =====================
# UNGBAN
# =====================
@bot.on(events.NewMessage(pattern=r"\.ungban(?: (.*))?$"))
async def ungban(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    DATA["gbans"].pop(str(uid), None)
    save_data()

    async for d in bot.iter_dialogs():
        if d.is_group or d.is_channel:
            try:
                await bot(EditBannedRequest(d.id, uid, UNBAN))
            except:
                pass

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
        text += f"• `{uid}` → {d.get('reason')}\n"

    await e.reply(text or "No global mutes")

@bot.on(events.NewMessage(pattern=r"\.gbanlist$"))
async def gbanlist(e):
    if not is_owner(e):
        return

    text = "🚫 **Global Bans**\n\n"
    for uid, d in DATA["gbans"].items():
        text += f"• `{uid}` → {d.get('reason')}\n"

    await e.reply(text or "No global bans")

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
                save_data()
            else:
                await e.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
