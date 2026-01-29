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
    print("⚠️ MongoDB not connected — antipm disabled")
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
    if col_state is None:
        return {"enabled": True, "silent": False}

    d = col_state.find_one({"_id": "state"})
    return d if d else {"enabled": True, "silent": False}


def set_state(key, value):
    if col_state is None:
        return
    col_state.update_one(
        {"_id": "state"},
        {"$set": {key: value}},
        upsert=True
    )


def get_user(uid):
    return col_users.find_one({"_id": uid}) if col_users else None


def save_user(uid, data):
    if col_users:
        col_users.update_one({"_id": uid}, {"$set": data}, upsert=True)


def reset_user(uid):
    if col_users:
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
    "• MongoDB based Anti-PM\n"
    "• Warning replace system\n"
    "• Spam detection\n"
    "• DM only"
)

# =====================
# COMMAND HANDLER (SINGLE)
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm(?:\s+(.*))?$"))
async def antipm_command(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
    except:
        pass

    arg = (e.pattern_match.group(1) or "").lower().strip()
    state = get_state()

    # ---------- STATUS ----------
    if arg == "status":
        total = col_users.count_documents({}) if col_users else 0
        msg = await bot.send_message(
            e.chat_id,
            "🛡 **Anti-PM Status**\n\n"
            f"• Enabled: `{state['enabled']}`\n"
            f"• Silent: `{state['silent']}`\n"
            f"• Tracked users: `{total}`"
        )
        await asyncio.sleep(8)
        return await msg.delete()

    # ---------- ON / OFF ----------
    if arg in ("on", "off"):
        enabled = arg == "on"
        set_state("enabled", enabled)
        msg = await bot.send_message(
            e.chat_id,
            f"🛡 Anti-PM {'ENABLED' if enabled else 'DISABLED'}"
        )
        await asyncio.sleep(5)
        return await msg.delete()

    # ---------- SILENT ----------
    if arg.startswith("silent"):
        silent = arg.endswith("on")
        set_state("silent", silent)
        msg = await bot.send_message(
            e.chat_id,
            f"🔇 Silent mode {'ON' if silent else 'OFF'}"
        )
        await asyncio.sleep(5)
        return await msg.delete()

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
@bot.on(events.NewMessage(pattern=r"\.disapprove$"))
async def disapprove_user(e):
    if not is_owner(e) or not e.is_reply:
        return

    r = await e.get_reply_message()
    reset_user(r.sender_id)

    await e.delete()
    msg = await bot.send_message(e.chat_id, "❌ User disapproved")
    await asyncio.sleep(5)
    await msg.delete()

# =====================
# MAIN DM HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    if not e.is_private or mongo is None or is_owner(e):
        return

    try:
        state = get_state()
        if not state["enabled"]:
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
            if not state["silent"]:
                await bot.send_message(
                    uid,
                    "👋 Hi!\nThis account doesn’t accept DMs.\nPlease wait or get approved."
                )
            return

        msgs = [t for t in u.get("msgs", []) if now - t < SPAM_WINDOW]
        msgs.append(now)

        if len(msgs) >= SPAM_LIMIT:
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warnings = u.get("warnings", 0) + 1

        if warnings >= WARNING_LIMIT:
            await bot(BlockRequest(uid))
            reset_user(uid)
            return

        warn_msg = None
        if not state["silent"]:
            warn_msg = await bot.send_message(
                uid,
                f"⚠️ Warning {warnings}/{WARNING_LIMIT}"
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
