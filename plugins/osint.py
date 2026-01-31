# plugins/osint.py

import os
import json
import time
import math
from datetime import datetime

from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "osint.py"
DATA_FILE = "utils/osint_store.json"

# =====================
# LOAD / SAVE
# =====================
def load():
    if not os.path.exists(DATA_FILE):
        return {"track": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

DATA = load()

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ osint.py loaded (STABLE OSINT MODE)")

# =====================
# HELP
# =====================
register_help(
    "osint",
    ".userinfo / .userinfo osint\n"
    ".numberinfo\n"
    ".userphotos\n"
    ".trackuser\n"
    ".untrackuser\n"
    ".tracklist\n\n"
    "• Telegram OSINT (ToS-safe)\n"
    "• Risk scoring\n"
    "• History tracking\n"
    "• No privacy bypass"
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


def approx_account_age(uid: int):
    # heuristic only (NOT exact)
    try:
        year = 2013 + int(math.log10(uid))
        return f"~{year}"
    except:
        return "Unknown"


def risk_score(user, full):
    score = 0

    if not user.username:
        score += 15
    if not user.photo:
        score += 20
    if not full.about:
        score += 10
    if user.bot:
        score += 40
    if user.scam:
        score += 50
    if user.fake:
        score += 30
    if user.verified:
        score -= 10
    if user.premium:
        score -= 5

    return max(0, min(score, 100))


# =====================
# USERINFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.userinfo(?: (osint))?$"))
async def userinfo(e):
    try:
        uid = await resolve_user(e)
        if not uid:
            return

        user = await bot.get_entity(uid)
        full = await bot(GetFullUserRequest(uid))

        risk = risk_score(user, full)

        text = (
            "🧠 **USER OSINT REPORT**\n\n"
            f"• ID: `{user.id}`\n"
            f"• Name: `{(user.first_name or '')} {(user.last_name or '')}`\n"
            f"• Username: `@{user.username}`\n"
            f"• Bio: `{full.about or 'N/A'}`\n"
            f"• Phone: `{user.phone or 'Hidden'}`\n"
            f"• Premium: `{bool(user.premium)}`\n"
            f"• Verified: `{bool(user.verified)}`\n"
            f"• Bot: `{bool(user.bot)}`\n"
            f"• Scam flag: `{bool(user.scam)}`\n"
            f"• Fake flag: `{bool(user.fake)}`\n"
            f"• Approx Account Age: `{approx_account_age(user.id)}`\n\n"
            f"⚠️ **RISK SCORE:** `{risk}%`\n"
            f"STATUS: `{'HIGH RISK' if risk >= 60 else 'LOW / NORMAL'}`"
        )

        await e.reply(text)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)


# =====================
# NUMBER INFO
# =====================
@bot.on(events.NewMessage(pattern=r"\.numberinfo$"))
async def numberinfo(e):
    try:
        uid = await resolve_user(e)
        user = await bot.get_entity(uid)

        if not user.phone:
            return await e.reply("❌ Phone number hidden by privacy settings")

        await e.reply(
            "📞 **NUMBER INFO (OSINT)**\n\n"
            f"• Number: `+{user.phone}`\n"
            f"• Country: `Approx by prefix`\n"
            f"• Visibility: `Public to you`\n"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)


# =====================
# USER PHOTOS
# =====================
@bot.on(events.NewMessage(pattern=r"\.userphotos$"))
async def userphotos(e):
    try:
        uid = await resolve_user(e)
        photos = await bot(GetUserPhotosRequest(uid, 0, 0, 20))
        await e.reply(f"📸 Profile photos found: `{len(photos.photos)}`")
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)


# =====================
# TRACK USER
# =====================
@bot.on(events.NewMessage(pattern=r"\.trackuser$"))
async def track_user(e):
    uid = await resolve_user(e)
    user = await bot.get_entity(uid)

    DATA["track"][str(uid)] = {
        "username": user.username,
        "name": f"{user.first_name or ''} {user.last_name or ''}",
        "time": int(time.time())
    }
    save()

    await e.reply("📌 User added to OSINT tracking")


@bot.on(events.NewMessage(pattern=r"\.untrackuser$"))
async def untrack_user(e):
    uid = await resolve_user(e)
    DATA["track"].pop(str(uid), None)
    save()
    await e.reply("❌ User removed from tracking")


@bot.on(events.NewMessage(pattern=r"\.tracklist$"))
async def track_list(e):
    if not DATA["track"]:
        return await e.reply("📭 No tracked users")

    txt = "📌 **TRACKED USERS**\n\n"
    for uid, d in DATA["track"].items():
        t = datetime.fromtimestamp(d["time"]).strftime("%d %b %Y")
        txt += f"• `{uid}` | since `{t}`\n"

    await e.reply(txt)
