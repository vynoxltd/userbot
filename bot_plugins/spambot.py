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

.spambot count
Spam in same group

.spambot count chat_id
Spam in target group

.spambot count @username
Spam in target group

Reply based:
(reply) .spambot count
"""
)

# =====================
# CONFIG
# =====================
SPAM_TEXTS = [
    "Papa hu mai tera 😈",
    "Abe htt noob 😂",
    "Tujhse nahi hoga, rehne de 🤡",
    "Skill issue bro 😎",
    "Practice kar le beta 🔥",
]

SPAM_DELAY = 1.2
AUTO_DELETE_TIME = 50

SPAM_ENABLED = True
SPAM_RUNNING = False
STOP_FLAG = False


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
# SPAMBOT COMMAND
# =====================
@Client.on_message(filters.command("spambot", "."))
async def spambot_handler(client: Client, m):
    global SPAM_ENABLED, SPAM_RUNNING, STOP_FLAG

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
        txt = "ENABLED ✅" if SPAM_ENABLED else "DISABLED ❌"
        msg = await client.send_message(m.chat.id, f"🤖 SpamBot {txt}")
        await asyncio.sleep(4)
        await msg.delete()
        return

    # -----------------
    # STOP
    # -----------------
    if len(m.command) == 2 and m.command[1] == "stop":
        STOP_FLAG = True
        return

    if not SPAM_ENABLED or SPAM_RUNNING:
        return

    # -----------------
    # COUNT CHECK
    # -----------------
    if len(m.command) < 2 or not m.command[1].isdigit():
        return

    count = int(m.command[1])
    if count <= 0 or count > 200:
        return

    # -----------------
    # TARGET CHAT
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

    reply_msg = m.reply_to_message

    # =====================
    # START SPAM
    # =====================
    SPAM_RUNNING = True
    STOP_FLAG = False

    try:
        for i in range(count):
            if STOP_FLAG:
                break

            text = SPAM_TEXTS[i % len(SPAM_TEXTS)]

            if reply_msg:
                sent = await reply_msg.reply(text)
            else:
                sent = await client.send_message(target_chat, text)

            asyncio.create_task(auto_delete(sent))
            await asyncio.sleep(SPAM_DELAY)

    finally:
        SPAM_RUNNING = False
        STOP_FLAG = False
