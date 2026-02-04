import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from database import settings

print("✔ autoreply.py loaded")

# =====================
# AUTO HELP
# =====================
register_help(
    "autoreply",
    ".autoreply on | off\n"
    ".autoreplydelay SECONDS\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply)\n"
    ".ablacklist (reply)\n"
    ".awhitelistdel (reply)\n"
    ".ablacklistdel (reply)\n\n"
    "• DM only\n"
    "• Auto delete old reply\n"
    "• Owner grace 120 seconds\n"
    "• Whitelist / Blacklist supported"
)

# =====================
# MEMORY
# =====================
LAST_AUTOREPLY = {}      # user_id -> Message
LAST_OWNER_REPLY = {}   # user_id -> datetime

OWNER_GRACE = 120  # seconds

# =====================
# DEFAULT TEXTS
# =====================
TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI will reply soon 😊",
    "afternoon": "🌤 Hello!\nI am busy right now.",
    "evening": "🌆 Good evening!\nWill get back to you soon.",
    "night": "🌙 It's late night.\nPlease text, I’ll reply later 🙏"
}

# =====================
# MONGO HELPERS
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
# CORE HELPERS
# =====================
def is_enabled():
    return get_var("AUTOREPLY_ON", "off") == "on"

def get_delay():
    try:
        return int(get_var("AUTOREPLY_DELAY", "0"))
    except:
        return 0

def get_time_text():
    ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
    h = ist.hour
    if 5 <= h <= 11:
        return get_var("AUTOREPLY_MORNING", TIME_TEXTS["morning"])
    elif 12 <= h <= 16:
        return get_var("AUTOREPLY_AFTERNOON", TIME_TEXTS["afternoon"])
    elif 17 <= h <= 20:
        return get_var("AUTOREPLY_EVENING", TIME_TEXTS["evening"])
    else:
        return get_var("AUTOREPLY_NIGHT", TIME_TEXTS["night"])

# =====================
# COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def toggle_autoreply(e):
    if not is_owner(e):
        return
    await e.delete()
    state = e.pattern_match.group(1)
    set_var("AUTOREPLY_ON", state)
    msg = await e.respond(f"✅ Auto reply {state.upper()}")
    await asyncio.sleep(4)
    await msg.delete()

@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def set_delay(e):
    if not is_owner(e):
        return
    await e.delete()
    set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
    msg = await e.respond("⏱ Delay updated")
    await asyncio.sleep(4)
    await msg.delete()

@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night)"))
async def set_text(e):
    if not is_owner(e):
        return
    await e.delete()
    text = e.raw_text.split(None, 1)[1]
    key = f"AUTOREPLY_{e.pattern_match.group(1).upper()}"
    set_var(key, text)
    msg = await e.respond("✅ Text updated")
    await asyncio.sleep(4)
    await msg.delete()

# =====================
# WHITELIST / BLACKLIST
# =====================
@bot.on(events.NewMessage(pattern=r"\.a(white|black)list$"))
async def add_list(e):
    if not is_owner(e) or not e.is_reply:
        return
    await e.delete()
    r = await e.get_reply_message()

    key = (
        "AUTOREPLY_WHITELIST"
        if "white" in e.raw_text
        else "AUTOREPLY_BLACKLIST"
    )

    data = get_list(key)
    if r.sender_id not in data:
        data.append(r.sender_id)
        save_list(key, data)

    msg = await e.respond("✅ User added")
    await asyncio.sleep(4)
    await msg.delete()

@bot.on(events.NewMessage(pattern=r"\.a(white|black)listdel$"))
async def remove_list(e):
    if not is_owner(e) or not e.is_reply:
        return
    await e.delete()
    r = await e.get_reply_message()

    key = (
        "AUTOREPLY_WHITELIST"
        if "white" in e.raw_text
        else "AUTOREPLY_BLACKLIST"
    )

    data = get_list(key)
    if r.sender_id in data:
        data.remove(r.sender_id)
        save_list(key, data)

    msg = await e.respond("🗑 User removed")
    await asyncio.sleep(4)
    await msg.delete()

# =====================
# OWNER REPLY TRACK
# =====================
@bot.on(events.NewMessage(outgoing=True))
async def owner_reply_track(e):
    if e.is_private:
        LAST_OWNER_REPLY[e.chat_id] = datetime.utcnow()

# =====================
# AUTOREPLY LISTENER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def autoreply_listener(e):
    try:
        # sirf private chats
        if not e.is_private or is_owner(e):
            return

        sender = await e.get_sender()

        # 🚫 ignore bots
        if sender and sender.bot:
            return

        # 🔘 autoreply off
        if not is_enabled():
            return

        uid = e.sender_id
        now = datetime.utcnow()

        # ⏱ owner grace
        last_owner = LAST_OWNER_REPLY.get(uid)
        if last_owner and (now - last_owner).seconds < OWNER_GRACE:
            return

        # 🚫 blacklist
        if uid in get_list("AUTOREPLY_BLACKLIST"):
            return

        # ✅ whitelist (agar set hai)
        wl = get_list("AUTOREPLY_WHITELIST")
        if wl and uid not in wl:
            return

        # 🧹 delete old autoreply
        old = LAST_AUTOREPLY.get(uid)
        if old:
            try:
                await old.delete()
            except:
                pass

        # ⏳ delay
        delay = get_delay()
        if delay:
            await asyncio.sleep(delay)

        msg = await e.reply(get_time_text())
        LAST_AUTOREPLY[uid] = msg

    except Exception as ex:
        await log_error(bot, "autoreply.py", ex)
