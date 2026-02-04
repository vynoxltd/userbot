# plugins/autoreply.py

import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error
from utils.mongo import settings

PLUGIN_NAME = "autoreply.py"
print("✔ autoreply.py loaded (SMART v2 – CORE ONLY)")

# =====================
# HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on|off\n"
    ".autoreply status\n"
    ".autoreplydelay <sec>\n"
    ".autocooldown <sec>\n\n"
    ".seenonly on|off\n"
    ".firstreply on|off\n"
    ".autodisable on|off\n\n"
    ".officehours on|off\n"
    ".officehours set <start>-<end>\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply/user/id)\n"
    ".awhitelistdel (reply/user/id)\n"
    ".awhitelist list\n\n"
    ".ablacklist (reply/user/id)\n"
    ".ablacklistdel (reply/user/id)\n"
    ".ablacklist list\n\n"
    "• DM only\n"
    "• Owner only\n"
    "• Mongo based (restart safe)\n"
    "• Keyword & Scam filter separate"
)

# =====================
# MEMORY
# =====================
LAST_REPLY_TIME = {}
DISABLED_USERS = set()

# =====================
# DEFAULT TEXTS
# =====================
TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI will reply soon 😊",
    "afternoon": "🌤 Hello!\nI am busy right now.",
    "evening": "🌆 Good evening!\nWill get back to you soon.",
    "night": "🌙 It's late night.\nPlease text, I’ll reply later 🙏"
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

def get_list(key):
    raw = get_var(key, "")
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x.isdigit()]

def save_list(key, data):
    set_var(key, ",".join(str(x) for x in data))

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

# =====================
# FLAGS
# =====================
def enabled():
    return get_var("AUTOREPLY_ON", "off") == "on"

def cooldown():
    return int(get_var("AR_COOLDOWN", "0"))

def seen_only():
    return get_var("AR_SEENONLY", "off") == "on"

def firstreply():
    return get_var("AR_FIRST", "off") == "on"

def autodisable():
    return get_var("AR_AUTODISABLE", "off") == "on"

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
# TIME TEXT (OLD KEYS)
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
async def toggle_autoreply(e):
    if not is_owner(e): return
    state = e.pattern_match.group(1)
    set_var("AUTOREPLY_ON", state)
    msg = await e.reply(f"✅ Autoreply **{state.upper()}**")
    await asyncio.sleep(4)
    await msg.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreply status$"))
async def autoreply_status(e):
    if not is_owner(e): return

    text = (
        "📊 **AUTOREPLY STATUS**\n\n"
        f"• Status: `{ 'ON' if enabled() else 'OFF' }`\n"
        f"• Delay: `{ get_var('AUTOREPLY_DELAY', '0') } sec`\n"
        f"• Cooldown: `{ cooldown() } sec`\n"
        f"• Seen Only: `{ get_var('AR_SEENONLY', 'off').upper() }`\n\n"
        f"• Whitelist: `{ len(get_list('AUTOREPLY_WHITELIST')) } users`\n"
        f"• Blacklist: `{ len(get_list('AUTOREPLY_BLACKLIST')) } users`"
    )

    msg = await e.reply(text)
    await asyncio.sleep(6)
    await msg.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def set_delay(e):
    if not is_owner(e): return
    set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
    await e.reply("⏱ Delay updated")

@bot.on(events.NewMessage(pattern=r"\.autocooldown (\d+)"))
async def set_cooldown(e):
    if not is_owner(e): return
    set_var("AR_COOLDOWN", e.pattern_match.group(1))
    await e.reply("⏳ Cooldown updated")

@bot.on(events.NewMessage(pattern=r"\.seenonly (on|off)"))
async def set_seenonly(e):
    if not is_owner(e): return
    set_var("AR_SEENONLY", e.pattern_match.group(1))
    await e.reply("👁 Seen-only updated")

@bot.on(events.NewMessage(pattern=r"\.(firstreply|autodisable) (on|off)"))
async def set_flags(e):
    if not is_owner(e): return
    key = "AR_FIRST" if "first" in e.raw_text else "AR_AUTODISABLE"
    set_var(key, e.pattern_match.group(2))
    await e.reply("✅ Setting updated")

@bot.on(events.NewMessage(pattern=r"\.officehours (on|off)"))
async def set_office(e):
    if not is_owner(e): return
    set_var("AR_OFFICE", e.pattern_match.group(1))
    await e.reply("🏢 Office hours updated")

@bot.on(events.NewMessage(pattern=r"\.officehours set (\d+)-(\d+)"))
async def set_office_time(e):
    if not is_owner(e): return
    set_var("AR_OFFICE_TIME", f"{e.pattern_match.group(1)}-{e.pattern_match.group(2)}")
    await e.reply("⏰ Office time set")

# =====================
# SET TEXT
# =====================
@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night) (.+)"))
async def set_text(e):
    if not is_owner(e): return
    key = f"AUTOREPLY_{e.pattern_match.group(1).upper()}"
    set_var(key, e.pattern_match.group(2))
    await e.reply("✅ Text updated")

# =====================
# WHITELIST / BLACKLIST
# =====================
@bot.on(events.NewMessage(pattern=r"\.a(white|black)list(?: (.*))?$"))
async def add_list(e):
    if not is_owner(e): return
    uid = await resolve_user(e)
    if not uid: return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)
    if uid not in data:
        data.append(uid)
        save_list(key, data)

    await e.reply("✅ User added")

@bot.on(events.NewMessage(pattern=r"\.a(white|black)listdel(?: (.*))?$"))
async def del_list(e):
    if not is_owner(e): return
    uid = await resolve_user(e)
    if not uid: return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    data = get_list(key)
    if uid in data:
        data.remove(uid)
        save_list(key, data)

    await e.reply("🗑 User removed")

@bot.on(events.NewMessage(pattern=r"\.a(white|black)list list$"))
async def list_users(e):
    if not is_owner(e): return

    key = "AUTOREPLY_WHITELIST" if "white" in e.raw_text else "AUTOREPLY_BLACKLIST"
    users = get_list(key)

    if not users:
        return await e.reply("📭 List is empty")

    text = "📃 **USER LIST**\n\n"
    for uid in users:
        try:
            u = await bot.get_entity(uid)
            text += f"• {u.first_name or 'User'} (`{uid}`)\n"
        except:
            text += f"• `{uid}`\n"

    await e.reply(text)

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
        await e.reply(msg)
        LAST_REPLY_TIME[uid] = now

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
