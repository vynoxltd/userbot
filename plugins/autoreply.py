from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    set_var,
    get_var
)
import asyncio
from datetime import datetime, timedelta

mark_plugin_loaded("autoreply.py")

# =====================
# MEMORY (PER USER)
# =====================
LAST_REPLY = {}   # user_id -> message_id

# =====================
# DEFAULT TEXTS
# =====================
DEFAULT_TEXT = (
    "👋 Hello!\n\n"
    "I am currently unavailable.\n"
    "Please leave your message 😊"
)

TIME_TEXTS = {
    "morning": "☀️ Good morning!\nI will reply soon 😊",
    "afternoon": "🌤 Hello!\nI am busy right now.",
    "evening": "🌙 Good evening!\nWill get back to you soon.",
    "night": "🌌 It's late night.\nPlease text, I’ll reply later 🙏"
}

# =====================
# HELPERS
# =====================
def is_enabled():
    return get_var("AUTOREPLY_ON", "off") == "on"

def get_delay():
    try:
        return int(get_var("AUTOREPLY_DELAY", "0"))
    except:
        return 0

def get_time_based_text():
    # 🇮🇳 IST = UTC + 5:30
    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    hour = ist_time.hour

    if 5 <= hour < 12:
        return TIME_TEXTS["morning"]
    elif 12 <= hour < 18:
        return TIME_TEXTS["afternoon"]
    elif 18 <= hour < 23:
        return TIME_TEXTS["evening"]
    else:
        return TIME_TEXTS["night"]

def get_reply_text():
    custom = get_var("AUTOREPLY_TEXT")
    return custom if custom else get_time_based_text()

def get_list(name):
    raw = get_var(name, "")
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x.isdigit()]

def save_list(name, data):
    set_var(name, ",".join(str(x) for x in data))

# =====================
# AUTO REPLY HANDLER (DM ONLY)
# =====================
@Client.on_message(filters.private & ~filters.bot & ~filters.me)
async def auto_reply_handler(client: Client, m):
    try:
        if not is_enabled():
            return

        user_id = m.from_user.id

        blacklist = get_list("AUTOREPLY_BLACKLIST")
        whitelist = get_list("AUTOREPLY_WHITELIST")

        # ❌ blacklist
        if user_id in blacklist:
            return

        # ✅ whitelist only
        if whitelist and user_id not in whitelist:
            return

        # 🧹 delete old auto reply
        old_msg_id = LAST_REPLY.get(user_id)
        if old_msg_id:
            try:
                await client.delete_messages(m.chat.id, old_msg_id)
            except:
                pass

        delay = get_delay()
        if delay > 0:
            await asyncio.sleep(delay)

        sent = await m.reply_text(get_reply_text())
        LAST_REPLY[user_id] = sent.id

    except Exception as e:
        await log_error(client, "autoreply.py", e)

# =====================
# AUTOREPLY ON / OFF
# =====================
@Client.on_message(owner_only & filters.command("autoreply", "."))
async def autoreply_toggle(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.autoreply on | off"
            )
            await auto_delete(msg, 4)
            return

        state = m.command[1].lower()
        if state not in ("on", "off"):
            return

        set_var("AUTOREPLY_ON", state)

        msg = await client.send_message(
            m.chat.id,
            f"✅ Auto reply {state.upper()}"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)

# =====================
# SET CUSTOM TEXT
# =====================
@Client.on_message(owner_only & filters.command("setautoreply", "."))
async def set_autoreply_text(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.setautoreply <text>"
            )
            await auto_delete(msg, 5)
            return

        text = m.text.split(None, 1)[1]
        set_var("AUTOREPLY_TEXT", text)

        msg = await client.send_message(
            m.chat.id,
            "✅ Auto reply text updated"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)

# =====================
# SET DELAY
# =====================
@Client.on_message(owner_only & filters.command("autoreplydelay", "."))
async def set_delay(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2 or not m.command[1].isdigit():
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.autoreplydelay <seconds>"
            )
            await auto_delete(msg, 4)
            return

        set_var("AUTOREPLY_DELAY", m.command[1])

        msg = await client.send_message(
            m.chat.id,
            f"⏱ Reply delay set to {m.command[1]}s"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)

# =====================
# WHITELIST / BLACKLIST
# =====================
@Client.on_message(owner_only & filters.command(["awhitelist", "ablacklist"], ".") & filters.reply)
async def list_manager(client: Client, m):
    try:
        await m.delete()

        user_id = m.reply_to_message.from_user.id
        cmd = m.command[0]

        key = (
            "AUTOREPLY_WHITELIST"
            if cmd == "awhitelist"
            else "AUTOREPLY_BLACKLIST"
        )

        data = get_list(key)

        if user_id not in data:
            data.append(user_id)
            save_list(key, data)

        msg = await client.send_message(
            m.chat.id,
            f"✅ User added to {key.split('_')[-1].lower()}"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)

@Client.on_message(owner_only & filters.command(["awhitelistdel", "ablacklistdel"], ".") & filters.reply)
async def list_remove(client: Client, m):
    try:
        await m.delete()

        user_id = m.reply_to_message.from_user.id
        cmd = m.command[0]

        key = (
            "AUTOREPLY_WHITELIST"
            if cmd == "awhitelistdel"
            else "AUTOREPLY_BLACKLIST"
        )

        data = get_list(key)

        if user_id in data:
            data.remove(user_id)
            save_list(key, data)

        msg = await client.send_message(
            m.chat.id,
            f"🗑 User removed from {key.split('_')[-1].lower()}"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "autoreply.py", e)
