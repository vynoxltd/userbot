import asyncio
from datetime import datetime, timedelta
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from database import settings

# =====================
# PLUGIN LOAD MARK
# =====================
print("✔ autoreply.py loaded")

# =====================
# AUTO HELP REGISTER (NO < > USED)
# =====================
register_help(
    "autoreply",
    ".autoreply on | off\n"
    "Enable or disable auto reply\n\n"
    ".autoreplydelay SECONDS\n"
    "Set auto reply delay\n\n"
    ".setmorning TEXT\n"
    ".setafternoon TEXT\n"
    ".setevening TEXT\n"
    ".setnight TEXT\n\n"
    ".awhitelist (reply to user)\n"
    ".ablacklist (reply to user)\n"
    ".awhitelistdel (reply to user)\n"
    ".ablacklistdel (reply to user)\n\n"
    "• DM only\n"
    "• Time based replies\n"
    "• One reply per user"
)

# =====================
# MEMORY
# =====================
LAST_REPLY = {}          # user_id -> message_id
LAST_MANUAL_REPLY = {}  # user_id -> datetime

# =====================
# DEFAULT TIME TEXTS
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
    hour = ist.hour

    if 5 <= hour <= 11:
        return get_var("AUTOREPLY_MORNING", TIME_TEXTS["morning"])
    elif 12 <= hour <= 16:
        return get_var("AUTOREPLY_AFTERNOON", TIME_TEXTS["afternoon"])
    elif 17 <= hour <= 20:
        return get_var("AUTOREPLY_EVENING", TIME_TEXTS["evening"])
    else:
        return get_var("AUTOREPLY_NIGHT", TIME_TEXTS["night"])

# =====================
# COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.autoreply (on|off)"))
async def autoreply_toggle(e):
    if not is_owner(e):
        return
    try:
        await e.delete()
        state = e.pattern_match.group(1)
        set_var("AUTOREPLY_ON", state)
        msg = await e.respond(f"✅ Auto reply {state.upper()}")
        await asyncio.sleep(4)
        await msg.delete()
    except Exception:
        await log_error(bot, "autoreply.py")


@bot.on(events.NewMessage(pattern=r"\.autoreplydelay (\d+)"))
async def autoreply_delay(e):
    if not is_owner(e):
        return
    try:
        await e.delete()
        set_var("AUTOREPLY_DELAY", e.pattern_match.group(1))
        msg = await e.respond("⏱ Auto reply delay updated")
        await asyncio.sleep(4)
        await msg.delete()
    except Exception:
        await log_error(bot, "autoreply.py")


@bot.on(events.NewMessage(pattern=r"\.set(morning|afternoon|evening|night)"))
async def set_time_text(e):
    if not is_owner(e):
        return
    try:
        await e.delete()
        text = e.raw_text.split(None, 1)[1]
        key = f"AUTOREPLY_{e.pattern_match.group(1).upper()}"
        set_var(key, text)
        msg = await e.respond("✅ Auto reply text updated")
        await asyncio.sleep(4)
        await msg.delete()
    except Exception:
        await log_error(bot, "autoreply.py")

# =====================
# WHITELIST / BLACKLIST
# =====================
@bot.on(events.NewMessage(pattern=r"\.a(white|black)list$"))
async def add_list(e):
    if not is_owner(e) or not e.is_reply:
        return
    try:
        await e.delete()
        reply = await e.get_reply_message()

        key = (
            "AUTOREPLY_WHITELIST"
            if "white" in e.raw_text
            else "AUTOREPLY_BLACKLIST"
        )

        data = get_list(key)
        if reply.sender_id not in data:
            data.append(reply.sender_id)
            save_list(key, data)

        msg = await e.respond("✅ User added")
        await asyncio.sleep(4)
        await msg.delete()
    except Exception:
        await log_error(bot, "autoreply.py")


@bot.on(events.NewMessage(pattern=r"\.a(white|black)listdel$"))
async def remove_list(e):
    if not is_owner(e) or not e.is_reply:
        return
    try:
        await e.delete()
        reply = await e.get_reply_message()

        key = (
            "AUTOREPLY_WHITELIST"
            if "white" in e.raw_text
            else "AUTOREPLY_BLACKLIST"
        )

        data = get_list(key)
        if reply.sender_id in data:
            data.remove(reply.sender_id)
            save_list(key, data)

        msg = await e.respond("🗑 User removed")
        await asyncio.sleep(4)
        await msg.delete()
    except Exception:
        await log_error(bot, "autoreply.py")