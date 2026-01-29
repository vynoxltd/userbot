# plugins/antipm.py

import asyncio
from telethon import events
from telethon.tl.functions.contacts import BlockRequest

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "antipm.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ antipm.py loaded")

# =====================
# CONFIG
# =====================
ANTI_PM_ENABLED = True
WARNING_LIMIT = 3

approved_users = set()
warnings = {}

# =====================
# HELP REGISTER
# =====================
register_help(
    "antipm",
    ".antipm on | off\n"
    ".approve (reply)\n"
    ".disapprove (reply)\n\n"
    "• New user → instant block\n"
    "• Approved user → 3 warnings then block\n"
    "• DM only\n"
    "• Owner safe"
)

# =====================
# TOGGLE ANTIPM
# =====================
@bot.on(events.NewMessage(pattern=r"\.antipm (on|off)$"))
async def toggle_antipm(e):
    global ANTI_PM_ENABLED
    if not is_owner(e):
        return

    ANTI_PM_ENABLED = e.pattern_match.group(1) == "on"
    await e.delete()

    await bot.send_message(
        e.chat_id,
        f"🛡 Anti-PM {'ENABLED' if ANTI_PM_ENABLED else 'DISABLED'}"
    )

# =====================
# APPROVE USER
# =====================
@bot.on(events.NewMessage(pattern=r"\.approve$"))
async def approve_user(e):
    if not is_owner(e) or not e.is_reply:
        return

    r = await e.get_reply_message()
    approved_users.add(r.sender_id)
    warnings.pop(r.sender_id, None)

    await e.delete()
    await bot.send_message(
        e.chat_id,
        f"✅ User approved"
    )

# =====================
# DISAPPROVE USER
# =====================
@bot.on(events.NewMessage(pattern=r"\.disapprove$"))
async def disapprove_user(e):
    if not is_owner(e) or not e.is_reply:
        return

    r = await e.get_reply_message()
    approved_users.discard(r.sender_id)
    warnings.pop(r.sender_id, None)

    await e.delete()
    await bot.send_message(
        e.chat_id,
        f"❌ User disapproved"
    )

# =====================
# ANTI PM HANDLER
# =====================
@bot.on(events.NewMessage(incoming=True))
async def antipm_handler(e):
    try:
        if not ANTI_PM_ENABLED:
            return

        if not e.is_private:
            return

        if is_owner(e):
            return

        sender = await e.get_sender()
        uid = sender.id

        # Ignore bots & verified
        if sender.bot or sender.verified:
            return

        # =====================
        # NEW USER → INSTANT BLOCK
        # =====================
        if uid not in approved_users:
            await bot.send_message(
                uid,
                "🚫 DM not allowed.\nYou are blocked."
            )
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            return

        # =====================
        # APPROVED USER → WARNINGS
        # =====================
        count = warnings.get(uid, 0) + 1
        warnings[uid] = count

        if count < WARNING_LIMIT:
            await bot.send_message(
                uid,
                f"⚠️ Warning {count}/{WARNING_LIMIT}\nStop spamming."
            )
        else:
            await bot.send_message(
                uid,
                "🚫 Limit exceeded. You are blocked."
            )
            await asyncio.sleep(1)
            await bot(BlockRequest(uid))
            warnings.pop(uid, None)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)