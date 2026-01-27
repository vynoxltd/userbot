from pyrogram import Client, filters
import asyncio
from plugins.utils import mark_plugin_loaded, register_help

mark_plugin_loaded("spambot.py")

# =====================
# HELP4 REGISTER
# =====================
register_help(
    "spambot",
    """
.spambot on
Enable spam bot

.spambot off
Disable spam bot

.spambot stop
Stop running spam

.spambot (count)
Spam in same group

.spambot (count) (chat_id or @username)
Spam in target group

Examples:
.spambot 10
.spambot 50 -1001234567890
.spambot 20 @mygroup
"""
)

# =====================
# CONFIG
# =====================
SPAM_TEXTS = [
    "Papa hu mai tera 😈",
    "htt lodu Lalit 🥱",
    "Abe jana Gendú",
    "Abe htt noob 😂",
    "Tujhse nahi hoga, rehne de 🤡",
    "Skill issue bro 😎",
    "Practice kar le beta 🔥",
]

SPAM_DELAY = 1.2        # seconds
AUTO_DELETE_TIME = 50  # seconds

SPAM_ENABLED = True
SPAM_TASK = None       # asyncio task holder

# =====================
# AUTO DELETE
# =====================
async def auto_delete(msg):
    try:
        await asyncio.sleep(AUTO_DELETE_TIME)
        await msg.delete()
    except:
        pass

# =====================
# SPAM LOOP
# =====================
async def spam_loop(client, count, target_chat):
    try:
        for i in range(count):
            text = SPAM_TEXTS[i % len(SPAM_TEXTS)]
            sent = await client.send_message(target_chat, text)
            asyncio.create_task(auto_delete(sent))
            await asyncio.sleep(SPAM_DELAY)
    except asyncio.CancelledError:
        pass

# =====================
# SPAMBOT COMMAND
# =====================
@Client.on_message(filters.command("spambot", "."))
async def spambot_handler(client: Client, m):
    global SPAM_ENABLED, SPAM_TASK

    # delete command
    try:
        await m.delete()
    except:
        pass

    # -----------------
    # ON / OFF
    # -----------------
    if len(m.command) == 2 and m.command[1] in ("on", "off"):
        SPAM_ENABLED = m.command[1] == "on"
        status = "ENABLED ✅" if SPAM_ENABLED else "DISABLED ❌"
        msg = await client.send_message(m.chat.id, f"🤖 SpamBot {status}")
        await asyncio.sleep(4)
        await msg.delete()
        return

    # -----------------
    # STOP
    # -----------------
    if len(m.command) == 2 and m.command[1] == "stop":
        if SPAM_TASK and not SPAM_TASK.done():
            SPAM_TASK.cancel()
            SPAM_TASK = None
            msg = await client.send_message(m.chat.id, "🛑 Spam stopped")
        else:
            msg = await client.send_message(m.chat.id, "ℹ️ No spam running")
        await asyncio.sleep(4)
        await msg.delete()
        return

    if not SPAM_ENABLED:
        return

    if SPAM_TASK and not SPAM_TASK.done():
        msg = await client.send_message(m.chat.id, "⚠️ Spam already running")
        await asyncio.sleep(4)
        await msg.delete()
        return

    # -----------------
    # COUNT
    # -----------------
    if len(m.command) < 2 or not m.command[1].isdigit():
        msg = await client.send_message(
            m.chat.id,
            "Usage:\n.spambot (count)\n.spambot (count) (chat_id or @username)"
        )
        await asyncio.sleep(5)
        await msg.delete()
        return

    count = int(m.command[1])
    if count <= 0 or count > 200:
        return

    # -----------------
    # TARGET
    # -----------------
    if len(m.command) >= 3:
        target = m.command[2]
        if target.startswith("@"):
            target_chat = target
        else:
            try:
                target_chat = int(target)
            except:
                return
    else:
        target_chat = m.chat.id

    # -----------------
    # START SPAM
    # -----------------
    SPAM_TASK = asyncio.create_task(
        spam_loop(client, count, target_chat)
)
