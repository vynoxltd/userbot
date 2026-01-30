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
SPAM_LIMIT = 5
SPAM_WINDOW = 10  # seconds

# =====================
# MONGO INIT (SAFE)
# =====================
if mongo is None:
    col_users = None
    col_state = None
else:
    db = mongo["userbot"]
    col_users = db["antipm_users"]
    col_state = db["antipm_state"]

# =====================
# STATE HELPERS
# =====================
def get_state():
    base = {"enabled": True, "silent": False}

    if col_state is None:
        return base

    data = col_state.find_one({"_id": "state"}) or {}
    base.update(data)

    col_state.update_one(
        {"_id": "state"},
        {"$set": base},
        upsert=True
    )
    return base


def set_state(key, value):
    if col_state is not None:
        col_state.update_one(
            {"_id": "state"},
            {"$set": {key: value}},
            upsert=True
        )


def get_user(uid):
    return col_users.find_one({"_id": uid}) if col_users is not None else None


def save_user(uid, data):
    if col_users is not None:
        col_users.update_one(
            {"_id": uid},
            {"$set": data},
            upsert=True
        )


def reset_user(uid):
    if col_users is not None:
        col_users.delete_one({"_id": uid})


async def resolve_user(e):
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    arg = e.pattern_match.group(1)
    if not arg:
        return None

    try:
        if arg.isdigit():
            return int(arg)
        user = await bot.get_entity(arg)
        return user.id
    except:
        return None

# =====================
# HELP
# =====================
register_help(
    "antipm",
    ".antipm on | off\n"
    ".antipms on | off\n"
    ".antipmstatus\n"
    ".approve (reply / user / id)\n"
    ".disapprove (reply / user / id)\n"
    ".resetwarn (reply / user / id)\n\n"
    "• MongoDB based Anti-PM\n"
    "• Warning replace system\n"
    "• Spam detection\n"
    "• DM only"
)

# =====================
# TOGGLE ANTIPM
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    if not is_owner(e):
        return

    state = e.pattern_match.group(1) == "on"
    set_state("enabled", state)

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if state else 'DISABLED'}"
    )
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# SILENT MODE
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipms (on|off)$"))
async def toggle_silent(e):
    if not is_owner(e):
        return

    silent = e.pattern_match.group(1) == "on"
    set_state("enabled", True)
    set_state("silent", silent)

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM ENABLED\n🔇 Silent mode {'ON' if silent else 'OFF'}"
    )
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# STATUS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmstatus$"))
async def antipm_status(e):
    if not is_owner(e):
        return

    s = get_state()
    total = col_users.count_documents({}) if col_users is not None else 0

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{s['enabled']}`\n"
        f"• Silent: `{s['silent']}`\n"
        f"• Tracked users: `{total}`"
    )
    await asyncio.sleep(8)
    await msg.delete()

# =====================
# APPROVE
# =====================
@bot.on(events.NewMessage(pattern=r"\.approve(?:\s+(.+))?$"))
async def approve_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": True,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None
    })

    await e.delete()
    msg = await bot.send_message(e.chat_id, "✅ User approved")
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# DISAPPROVE
# =====================
@bot.on(events.NewMessage(pattern=r"\.disapprove(?:\s+(.+))?$"))
async def disapprove_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    reset_user(uid)

    await e.delete()
    msg = await bot.send_message(e.chat_id, "❌ User disapproved")
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# RESET WARNINGS
# =====================
@bot.on(events.NewMessage(pattern=r"\.resetwarn(?:\s+(.+))?$"))
async def reset_warning(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    save_user(uid, {
        "approved": False,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None
    })

    await e.delete()
    msg = await bot.send_message(e.chat_id, "🔄 Warnings reset")
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or mongo is None:
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
        now = time.time()

        if u and u.get("approved"):
            return

        if not u:
            save_user(uid, {
                "approved": False,
                "warnings": 0,
                "msgs": [now],
                "last_warn_msg": None
            })
            if not s["silent"]:
                await bot.send_message(
                    uid,
                    "👋 Hi!\nDMs are restricted.\nPlease wait or get approved."
                )
            return

        msgs = [t for t in u.get("msgs", []) if now - t < SPAM_WINDOW]
        msgs.append(now)

        if len(msgs) >= SPAM_LIMIT:
            if u.get("last_warn_msg"):
                await bot.delete_messages(uid, u["last_warn_msg"])
            if not s["silent"]:
                await bot.send_message(uid, "🚫 Spam detected. You are blocked.")
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warnings = u.get("warnings", 0) + 1

        if u.get("last_warn_msg"):
            await bot.delete_messages(uid, u["last_warn_msg"])

        if warnings >= WARNING_LIMIT:
            if not s["silent"]:
                await bot.send_message(uid, "🚫 Warning limit exceeded. Blocked.")
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warn_msg = None
        if not s["silent"]:
            warn_msg = await bot.send_message(
                uid,
                f"⚠️ Warning {warnings}/{WARNING_LIMIT}\nPlease stop messaging."
            )

        save_user(uid, {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs,
            "last_warn_msg": warn_msg.id if warn_msg else None
        })

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
