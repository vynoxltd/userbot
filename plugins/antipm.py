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
from utils.local_store import load_json, save_json   # ✅ LOCAL STORAGE

PLUGIN_NAME = "antipm.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ antipm.py loaded (local storage mode)")

# =====================
# CONFIG
# =====================
WARNING_LIMIT = 3
SPAM_LIMIT = 5
SPAM_WINDOW = 10  # seconds

STATE_FILE = "data/antipm_state.json"
USERS_FILE = "data/antipm_users.json"

# =====================
# LOAD DATA
# =====================
STATE = load_json(STATE_FILE, {
    "enabled": True,
    "silent": False
})

USERS = load_json(USERS_FILE, {})

# =====================
# HELPERS
# =====================
def save_state():
    save_json(STATE_FILE, STATE)

def save_users():
    save_json(USERS_FILE, USERS)

def get_user(uid):
    return USERS.get(str(uid))

def reset_user(uid):
    USERS.pop(str(uid), None)
    save_users()

async def resolve_user(e):
    # reply
    if e.is_reply:
        r = await e.get_reply_message()
        return r.sender_id

    # username / id
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
    "• Local disk based (NO Mongo)\n"
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

    STATE["enabled"] = e.pattern_match.group(1) == "on"
    save_state()

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if STATE['enabled'] else 'DISABLED'}"
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

    STATE["enabled"] = True
    STATE["silent"] = e.pattern_match.group(1) == "on"
    save_state()

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM ENABLED\n🔇 Silent mode {'ON' if STATE['silent'] else 'OFF'}"
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

    await e.delete()
    msg = await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{STATE['enabled']}`\n"
        f"• Silent: `{STATE['silent']}`\n"
        f"• Tracked users: `{len(USERS)}`"
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

    USERS[str(uid)] = {
        "approved": True,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None
    }
    save_users()

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

    USERS[str(uid)] = {
        "approved": False,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None
    }
    save_users()

    await e.delete()
    msg = await bot.send_message(e.chat_id, "🔄 Warnings reset")
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or is_owner(e):
        return

    try:
        if not STATE["enabled"]:
            return

        sender = await e.get_sender()
        uid = sender.id

        if sender.bot or sender.verified:
            return

        u = USERS.get(str(uid))
        now = time.time()

        # approved
        if u and u.get("approved"):
            return

        # first message
        if not u:
            USERS[str(uid)] = {
                "approved": False,
                "warnings": 0,
                "msgs": [now],
                "last_warn_msg": None
            }
            save_users()

            if not STATE["silent"]:
                await bot.send_message(
                    uid,
                    "👋 Hi!\nDMs are restricted.\nPlease wait or get approved."
                )
            return

        # spam check
        msgs = [t for t in u["msgs"] if now - t < SPAM_WINDOW]
        msgs.append(now)

        if len(msgs) >= SPAM_LIMIT:
            if u.get("last_warn_msg"):
                await bot.delete_messages(uid, u["last_warn_msg"])

            if not STATE["silent"]:
                await bot.send_message(uid, "🚫 Spam detected. You are blocked.")

            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        # warnings
        warnings = u["warnings"] + 1

        if u.get("last_warn_msg"):
            await bot.delete_messages(uid, u["last_warn_msg"])

        if warnings >= WARNING_LIMIT:
            if not STATE["silent"]:
                await bot.send_message(uid, "🚫 Warning limit exceeded. Blocked.")

            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warn_msg = None
        if not STATE["silent"]:
            warn_msg = await bot.send_message(
                uid,
                f"⚠️ Warning {warnings}/{WARNING_LIMIT}\nPlease stop messaging."
            )

        USERS[str(uid)] = {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs,
            "last_warn_msg": warn_msg.id if warn_msg else None
        }
        save_users()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
