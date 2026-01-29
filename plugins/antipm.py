# plugins/antipm.py

import time
import asyncio
from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.mongo import mongo

PLUGIN_NAME = "antipm.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ antipm.py loaded")

# =====================
# CONFIG
# =====================
WARNING_LIMIT = 3
SPAM_LIMIT = 5          # messages
SPAM_WINDOW = 10        # seconds

# =====================
# MONGO
# =====================
if not mongo:
    print("⚠️ MongoDB not connected — antipm disabled")
    db = None
else:
    db = mongo["userbot"]
    col_users = db["antipm_users"]
    col_state = db["antipm_state"]

# =====================
# STATE HELPERS
# =====================
def get_state():
    d = col_state.find_one({"_id": "state"}) if col_state else None
    return d or {
        "enabled": True,
        "silent": False
    }

def set_state(key, value):
    col_state.update_one(
        {"_id": "state"},
        {"$set": {key: value}},
        upsert=True
    )

def get_user(uid):
    return col_users.find_one({"_id": uid}) if col_users else None

def save_user(uid, data):
    col_users.update_one(
        {"_id": uid},
        {"$set": data},
        upsert=True
    )

def reset_user(uid):
    col_users.delete_one({"_id": uid})

# =====================
# HELP
# =====================
register_help(
    "antipm",
    ".antipm on | off\n"
    ".antipm silent on | off\n"
    ".antipm status\n"
    ".approve (reply)\n"
    ".disapprove (reply)\n\n"
    "• New user → warn → block\n"
    "• Spam detection enabled\n"
    "• MongoDB based\n"
    "• DM only\n"
    "• Owner safe"
)

# =====================
# TOGGLE
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    if not is_owner(e):
        return

    set_state("enabled", e.pattern_match.group(1) == "on")
    await e.delete()
    await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if e.pattern_match.group(1)=='on' else 'DISABLED'}"
    )

# =====================
# SILENT MODE
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm silent (on|off)$"))
async def toggle_silent(e):
    if not is_owner(e):
        return

    set_state("silent", e.pattern_match.group(1) == "on")
    await e.delete()
    await bot.send_message(
        e.chat_id,
        f"🔇 Silent mode {'ON' if e.pattern_match.group(1)=='on' else 'OFF'}"
    )

# =====================
# STATUS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm status$"))
async def antipm_status(e):
    if not is_owner(e):
        return

    s = get_state()
    total = col_users.count_documents({}) if col_users else 0

    await e.delete()
    await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{s['enabled']}`\n"
        f"• Silent: `{s['silent']}`\n"
        f"• Tracked users: `{total}`"
    )

# =====================
# APPROVE
# =====================
@bot.on(events.NewMessage(pattern=r"\.approve$"))
async def approve_user(e):
    if not is_owner(e) or not e.is_reply:
        return

    r = await e.get_reply_message()
    save_user(r.sender_id, {
        "approved": True,
        "warnings": 0,
        "msgs": []
    })

    await e.delete()
    await bot.send_message(e.chat_id, "✅ User approved")

# =====================
# DISAPPROVE
# =====================
@bot.on(events.NewMessage(pattern=r"\.disapprove$"))
async def disapprove_user(e):
    if not is_owner(e) or not e.is_reply:
        return

    r = await e.get_reply_message()
    reset_user(r.sender_id)

    await e.delete()
    await bot.send_message(e.chat_id, "❌ User disapproved")

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or not mongo:
        return

    if is_owner(e):
        return

    try:
        s = get_state()
        if not s["enabled"]:
            return

        sender = await e.get_sender()
        uid = sender.id

        if sender.bot or sender.verified:
            return

        u = get_user(uid)

        # =====================
        # APPROVED USER → IGNORE
        # =====================
        if u and u.get("approved"):
            return

        now = time.time()

        if not u:
            # first message
            save_user(uid, {
                "approved": False,
                "warnings": 0,
                "msgs": [now]
            })

            if not s["silent"]:
                await bot.send_message(
                    uid,
                    "👋 Hi!\nThis account doesn’t accept DMs.\nPlease wait or get approved."
                )
            return

        # =====================
        # SPAM CHECK
        # =====================
        msgs = [t for t in u.get("msgs", []) if now - t < SPAM_WINDOW]
        msgs.append(now)

        if len(msgs) >= SPAM_LIMIT:
            if not s["silent"]:
                await bot.send_message(uid, "🚫 Spam detected. You are blocked.")
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        # =====================
        # WARNINGS
        # =====================
        warnings = u.get("warnings", 0) + 1

        if warnings >= WARNING_LIMIT:
            if not s["silent"]:
                await bot.send_message(uid, "🚫 Warning limit exceeded. Blocked.")
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return
        else:
            if not s["silent"]:
                await bot.send_message(
                    uid,
                    f"⚠️ Warning {warnings}/{WARNING_LIMIT}\nPlease stop messaging."
                )

        save_user(uid, {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs
        })

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
