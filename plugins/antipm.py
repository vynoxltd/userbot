# plugins/antipm.py

import time
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.local_store import load_json, save_json

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
SPAM_WINDOW = 10

STATE_FILE = "data/antipm_state.json"
USERS_FILE = "data/antipm_users.json"

STATE = load_json(STATE_FILE, {
    "enabled": True,
    "silent": False,
    "last_blocked_user": None,
    "last_warning_time": None
})

USERS = load_json(USERS_FILE, {})

# =====================
# HELPERS
# =====================
def save_state():
    save_json(STATE_FILE, STATE)

def save_users():
    save_json(USERS_FILE, USERS)

def ts(t):
    if not t:
        return "N/A"
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")

def reset_user(uid):
    USERS.pop(str(uid), None)
    save_users()

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
    ".antipmlist\n"
    ".approve (reply / user / id)\n"
    ".disapprove (reply / user / id)\n"
    ".resetwarn (reply / user / id)\n\n"
    "• Local disk based Anti-PM\n"
    "• Warning replace system\n"
    "• Spam detection\n"
    "• DM only"
)

# =====================
# TOGGLES
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    if not is_owner(e):
        return

    STATE["enabled"] = e.pattern_match.group(1) == "on"
    save_state()

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if STATE['enabled'] else 'DISABLED'}"
    )
    await asyncio.sleep(5)
    await m.delete()

@bot.on(events.NewMessage(pattern=r"\.antipms (on|off)$"))
async def toggle_silent(e):
    if not is_owner(e):
        return

    STATE["enabled"] = True
    STATE["silent"] = e.pattern_match.group(1) == "on"
    save_state()

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        f"🔇 Silent mode {'ON' if STATE['silent'] else 'OFF'}"
    )
    await asyncio.sleep(5)
    await m.delete()

# =====================
# STATUS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmstatus$"))
async def antipm_status(e):
    if not is_owner(e):
        return

    await e.delete()
    m = await bot.send_message(
        e.chat_id,
        "🛡 **Anti-PM Status**\n\n"
        f"• Enabled: `{STATE['enabled']}`\n"
        f"• Silent: `{STATE['silent']}`\n"
        f"• Tracked users: `{len(USERS)}`\n"
        f"• Last blocked user: `{STATE['last_blocked_user'] or 'N/A'}`\n"
        f"• Last warning time: `{ts(STATE['last_warning_time'])}`"
    )
    await asyncio.sleep(10)
    await m.delete()

# =====================
# LIST USERS
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipmlist$"))
async def antipm_list(e):
    if not is_owner(e):
        return

    await e.delete()

    if not USERS:
        m = await bot.send_message(e.chat_id, "📭 No tracked users")
        await asyncio.sleep(5)
        return await m.delete()

    text = "🛡 **Anti-PM Users**\n\n"
    for uid, u in USERS.items():
        text += (
            f"• `{uid}` | "
            f"warn: `{u['warnings']}` | "
            f"approved: `{u['approved']}` | "
            f"last warn: `{ts(u.get('last_warning_time'))}`\n"
        )

    m = await bot.send_message(e.chat_id, text)
    await asyncio.sleep(15)
    await m.delete()

# =====================
# APPROVE / DISAPPROVE / RESET
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
        "last_warn_msg": None,
        "last_warning_time": None
    }
    save_users()

    await e.delete()
    m = await bot.send_message(e.chat_id, "✅ User approved")
    await asyncio.sleep(5)
    await m.delete()

@bot.on(events.NewMessage(pattern=r"\.disapprove(?:\s+(.+))?$"))
async def disapprove_user(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if uid:
        reset_user(uid)

    await e.delete()
    m = await bot.send_message(e.chat_id, "❌ User disapproved")
    await asyncio.sleep(5)
    await m.delete()

@bot.on(events.NewMessage(pattern=r"\.resetwarn(?:\s+(.+))?$"))
async def resetwarn(e):
    if not is_owner(e):
        return

    uid = await resolve_user(e)
    if not uid:
        return

    USERS[str(uid)] = {
        "approved": False,
        "warnings": 0,
        "msgs": [],
        "last_warn_msg": None,
        "last_warning_time": None
    }
    save_users()
    await e.delete()

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or is_owner(e) or not STATE["enabled"]:
        return

    try:
        sender = await e.get_sender()
        uid = sender.id

        if sender.bot or sender.verified:
            return

        u = USERS.get(str(uid))
        now = time.time()

        # approved user
        if u and u.get("approved"):
            return

        # first message
        if not u:
            USERS[str(uid)] = {
                "approved": False,
                "warnings": 0,
                "msgs": [now],
                "last_warn_msg": None,
                "last_warning_time": None
            }
            save_users()

            if not STATE["silent"]:
                await bot.send_message(
                    uid,
                    "👋 Hello!\n\nThis account doesn’t accept direct messages.\n"
                    "Please wait for approval before messaging again."
                )
            return

        msgs = [t for t in u["msgs"] if now - t < SPAM_WINDOW] + [now]

        # spam block
        if len(msgs) >= SPAM_LIMIT:
            STATE["last_blocked_user"] = uid
            save_state()

            if not STATE["silent"]:
                await bot.send_message(uid, "🚫 Spam detected. You have been blocked.")

            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        # delete previous warning
        if u.get("last_warn_msg"):
            try:
                await bot.delete_messages(uid, u["last_warn_msg"])
            except:
                pass

        warnings = u["warnings"] + 1
        STATE["last_warning_time"] = now
        save_state()

        # final warning → block
        if warnings >= WARNING_LIMIT:
            STATE["last_blocked_user"] = uid
            save_state()

            if not STATE["silent"]:
                await bot.send_message(
                    uid,
                    "🚫 You have exceeded the warning limit and are now blocked."
                )

            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        # normal warning
        warn_msg = None
        if not STATE["silent"]:
            warn_msg = await bot.send_message(
                uid,
                f"⚠️ Warning {warnings}/{WARNING_LIMIT}\n"
                "Please stop messaging without approval."
            )

        USERS[str(uid)] = {
            "approved": False,
            "warnings": warnings,
            "msgs": msgs,
            "last_warn_msg": warn_msg.id if warn_msg else None,
            "last_warning_time": now
        }
        save_users()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
