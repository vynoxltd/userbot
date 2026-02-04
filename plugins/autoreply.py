# plugins/autoreply.py

import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.mongo import settings

print("✔ autoreply.py loaded (SMART v2 + SEEN ONLY + COMPAT + FIXED)")

# =====================
# HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on|off\n"
    ".autoreplydelay <sec>\n"
    ".autocooldown <sec>\n"
    ".autoreply status\n\n"
    ".seenonly on|off\n\n"
    ".officehours on|off\n"
    ".officehours set <start>-<end>\n\n"
    ".firstreply on|off\n"
    ".autodisable on|off\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply)\n"
    ".ablacklist (reply)\n"
    ".awhitelistdel (reply)\n"
    ".ablacklistdel (reply)\n\n"
    ".keyword add <word> | <reply>\n"
    ".scamfilter on|off\n"
    ".scamword add <word>\n\n"
    "• DM only\n"
    "• Owner only\n"
    "• Old behaviour preserved"
)

# =====================
# MEMORY
# =====================
LAST_AUTOREPLY = {}
LAST_REPLY_TIME = {}
DISABLED_USERS = set()

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
def get_var(k, d=None):
    doc = settings.find_one({"_id": k})
    return doc["value"] if doc else d

def set_var(k, v):
    settings.update_one({"_id": k}, {"$set": {"value": v}}, upsert=True)

def get_list(k):
    raw = get_var(k, "")
    return [int(x) for x in raw.split(",") if x.isdigit()]

def save_list(k, data):
    set_var(k, ",".join(str(x) for x in data))

# =====================
# FLAGS
# =====================
def enabled(): return get_var("AUTOREPLY_ON", "off") == "on"
def cooldown(): return int(get_var("AR_COOLDOWN", "0"))
def seen_only(): return get_var("AR_SEENONLY", "off") == "on"
def firstreply(): return get_var("AR_FIRST", "off") == "on"
def autodisable(): return get_var("AR_AUTODISABLE", "off") == "on"
def scamfilter(): return get_var("AR_SCAM", "off") == "on"

# =====================
# TIME TEXT
# =====================
def time_text():
    h = (datetime.utcnow() + timedelta(hours=5, minutes=30)).hour
    if 5 <= h <= 11:
        return get_var("AUTOREPLY_MORNING", TIME_TEXTS["morning"])
    if 12 <= h <= 16:
        return get_var("AUTOREPLY_AFTERNOON", TIME_TEXTS["afternoon"])
    if 17 <= h <= 20:
        return get_var("AUTOREPLY_EVENING", TIME_TEXTS["evening"])
    return get_var("AUTOREPLY_NIGHT", TIME_TEXTS["night"])

# =====================
# OWNER COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def _(e):
    if not is_owner(e): return
    set_var("AUTOREPLY_ON", e.pattern_match.group(1))
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def _(e):
    if not is_owner(e): return
    set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
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

@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night) (.+)"))
async def _(e):
    if not is_owner(e): return
    key = f"AUTOREPLY_{e.pattern_match.group(1).upper()}"
    set_var(key, e.pattern_match.group(2))
    await e.delete()

# =====================
# WHITELIST / BLACKLIST
# =====================
@bot.on(events.NewMessage(pattern=r"\.a(white|black)list$"))
async def _(e):
    if not is_owner(e) or not e.is_reply: return
    r = await e.get_reply_message()
    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)
    if r.sender_id not in data:
        data.append(r.sender_id)
        save_list(key, data)
    await e.delete()

@bot.on(events.NewMessage(pattern=r"\.a(white|black)listdel$"))
async def _(e):
    if not is_owner(e) or not e.is_reply: return
    r = await e.get_reply_message()
    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)
    if r.sender_id in data:
        data.remove(r.sender_id)
        save_list(key, data)
    await e.delete()

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

        if not enabled():
            return

        uid = e.sender_id

        if uid in get_list("AUTOREPLY_BLACKLIST"):
            return

        wl = get_list("AUTOREPLY_WHITELIST")
        if wl and uid not in wl:
            return

        if seen_only():
            await bot.send_read_acknowledge(e.chat_id)
            return

        now = datetime.utcnow()
        if uid in LAST_REPLY_TIME and (now - LAST_REPLY_TIME[uid]).seconds < cooldown():
            return

        msg = FIRST_REPLY_TEXT if firstreply() and uid not in LAST_REPLY_TIME else time_text()

        await asyncio.sleep(int(get_var("AUTOREPLY_DELAY", "0")))
        LAST_AUTOREPLY[uid] = await e.reply(msg)
        LAST_REPLY_TIME[uid] = now

    except Exception as ex:
        await log_error(bot, "autoreply.py", ex)
