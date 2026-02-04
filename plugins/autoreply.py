# plugins/autoreply.py

import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from database import settings

print("✔ autoreply.py loaded (SMART v2 + SEEN ONLY + COMPAT)")

# =====================
# HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on|off\n"
    ".autoreplydelay <sec>\n"
    ".autocooldown <sec>\n\n"
    ".seenonly on|off\n\n"
    ".officehours on|off\n"
    ".officehours set <start>-<end>\n\n"
    ".firstreply on|off\n"
    ".autodisable on|off\n\n"
    ".keyword add <word> | <reply>\n"
    ".keyword del <word>\n"
    ".keyword list\n\n"
    ".scamfilter on|off\n"
    ".scamword add <word>\n"
    ".scamword del <word>\n"
    ".scamword list\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    "• DM only\n"
    "• Owner only\n"
    "• Smart autoreply v2\n"
    "• Seen-only supported\n"
    "• Old data compatible"
)

# =====================
# MEMORY
# =====================
LAST_AUTOREPLY = {}
LAST_OWNER_REPLY = {}
LAST_REPLY_TIME = {}
DISABLED_USERS = set()

OWNER_GRACE = 120

# =====================
# DEFAULT TEXTS
# =====================
TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI’ll reply soon 😊",
    "afternoon": "🌤 Hello!\nI’m busy right now.",
    "evening": "🌆 Good evening!\nWill get back to you.",
    "night": "🌙 Late night.\nPlease text, I’ll reply later 🙏"
}

FIRST_REPLY_TEXT = "👋 Hi! Thanks for messaging.\nI’ll reply shortly."

# =====================
# DB HELPERS
# =====================
def get_var(key, default=None):
    doc = settings.find_one({"_id": key})
    return doc["value"] if doc else default

def set_var(key, value):
    settings.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )

# 🔁 BACKWARD COMPAT HELPER
def get_var_compat(new_key, old_key, default=None):
    return get_var(new_key, get_var(old_key, default))

def get_list(key):
    raw = get_var(key, "")
    return [x for x in raw.split("|") if x]

def save_list(key, data):
    set_var(key, "|".join(data))

# =====================
# FLAGS (FIXED)
# =====================
def enabled():
    return get_var_compat("AR_ON", "AUTOREPLY_ON", "off") == "on"

def cooldown():
    return int(get_var("AR_COOLDOWN", "0"))

def firstreply():
    return get_var("AR_FIRST", "off") == "on"

def autodisable():
    return get_var("AR_AUTODISABLE", "off") == "on"

def scamfilter():
    return get_var("AR_SCAM", "off") == "on"

def seen_only():
    return get_var("AR_SEENONLY", "off") == "on"

# =====================
# OFFICE HOURS
# =====================
def outside_office_hours():
    if get_var("AR_OFFICE", "off") != "on":
        return False

    t = get_var("AR_OFFICE_TIME")
    if not t:
        return False

    s, e = map(int, t.split("-"))
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    return not (s <= h <= e)

# =====================
# TIME TEXT (OLD + NEW KEYS)
# =====================
def time_text():
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour

    if 5 <= h <= 11:
        return get_var_compat("AR_MORNING", "AUTOREPLY_MORNING", TIME_TEXTS["morning"])
    if 12 <= h <= 16:
        return get_var_compat("AR_AFTERNOON", "AUTOREPLY_AFTERNOON", TIME_TEXTS["afternoon"])
    if 17 <= h <= 20:
        return get_var_compat("AR_EVENING", "AUTOREPLY_EVENING", TIME_TEXTS["evening"])
    return get_var_compat("AR_NIGHT", "AUTOREPLY_NIGHT", TIME_TEXTS["night"])

# =====================
# OWNER COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_ON", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_DELAY", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autocooldown (\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_COOLDOWN", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.seenonly (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_SEENONLY", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.officehours (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_OFFICE", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.officehours set (\d+)-(\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AR_OFFICE_TIME", f"{e.pattern_match.group(1)}-{e.pattern_match.group(2)}")
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.(firstreply|autodisable) (on|off)"))
async def _(e):
    if not is_owner(e): return
    key = "AR_FIRST" if "first" in e.raw_text else "AR_AUTODISABLE"
    set_var(key, e.pattern_match.group(2))
    await e.delete()

# =====================
# KEYWORDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.keyword add (.+?) \| (.+)"))
async def _(e):
    if not is_owner(e): return
    d = get_list("AR_KEYS")
    d.append(f"{e.pattern_match.group(1)}::{e.pattern_match.group(2)}")
    save_list("AR_KEYS", d)
    await e.delete()

# =====================
# SCAM WORDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.scamword add (.+)"))
async def _(e):
    if not is_owner(e): return
    d = get_list("AR_SCAMWORDS")
    d.append(e.pattern_match.group(1))
    save_list("AR_SCAMWORDS", d)
    await e.delete()

# =====================
# OWNER ACTIVITY TRACK
# =====================
@bot.on(events.NewMessage(outgoing=True))
async def _(e):
    if e.is_private:
        LAST_OWNER_REPLY[e.chat_id] = datetime.utcnow()
        if autodisable():
            DISABLED_USERS.add(e.chat_id)

# =====================
# AUTOREPLY CORE
# =====================
@bot.on(events.NewMessage(incoming=True))
async def autoreply(e):
    try:
        if not e.is_private or is_owner(e):
            return

        sender = await e.get_sender()
        if sender and sender.bot:
            return

        if not enabled() or outside_office_hours():
            return

        # 👁 SEEN ONLY MODE
        if seen_only():
            try:
                await bot.send_read_acknowledge(e.chat_id)
            except:
                pass
            return

        uid = e.sender_id
        now = datetime.utcnow()

        if uid in DISABLED_USERS:
            return

        if uid in LAST_REPLY_TIME and (now - LAST_REPLY_TIME[uid]).seconds < cooldown():
            return

        if firstreply() and uid not in LAST_REPLY_TIME:
            msg = FIRST_REPLY_TEXT
        else:
            msg = time_text()

        for k in get_list("AR_KEYS"):
            w, r = k.split("::", 1)
            if w.lower() in e.raw_text.lower():
                msg = r

        if scamfilter():
            for w in get_list("AR_SCAMWORDS"):
                if w.lower() in e.raw_text.lower():
                    msg = "⚠️ Please avoid suspicious messages."

        old = LAST_AUTOREPLY.get(uid)
        if old:
            try:
                await old.delete()
            except:
                pass

        await asyncio.sleep(int(get_var_compat("AR_DELAY", "AUTOREPLY_DELAY", "0")))
        LAST_AUTOREPLY[uid] = await e.reply(msg)
        LAST_REPLY_TIME[uid] = now

    except Exception as ex:
        await log_error(bot, "autoreply.py", ex)
