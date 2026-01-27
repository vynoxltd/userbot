from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    mark_plugin_loaded,
    register_help
)
import random
import time

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("spambot.py")

# =====================
# HELP4 REGISTER
# =====================
register_help(
    "spambot",
    """
.spambot
Fun spam bot reply (safe)

• Random funny replies
• Command auto delete
• Message auto delete (50s)
• Spam protection enabled
"""
)

# =====================
# CONFIG
# =====================
COOLDOWN = 10  # seconds
LAST_USED = {}  # user_id -> timestamp

SPAM_TEXTS = [
    "😎 Papa hu mai tera papa bol",
    "🤡 Abe hatt noob",
    "😂 Tujhse nahi hoga rehne de noob",
    "💀 Skill issue detected",
    "🔥 Practice kar beta",
    "🧠 Dimag use kar thoda",
    "🚨 Noob alert! Noob alert!",
    "😏 Beta tumse na ho payega"
]

# =====================
# SPAMBOT COMMAND
# =====================
@Client.on_message(owner_only & filters.command("spambot", "."))
async def spambot_cmd(client: Client, m):
    try:
        user_id = m.from_user.id
        now = time.time()

        # 🧹 delete command
        try:
            await m.delete()
        except:
            pass

        # ⏳ spam protection
        last = LAST_USED.get(user_id, 0)
        if now - last < COOLDOWN:
            warn = await client.send_message(
                m.chat.id,
                "⏳ Thoda ruk ja noob 😏"
            )
            await auto_delete(warn, 5)
            return

        LAST_USED[user_id] = now

        # 🎲 random text
        text = random.choice(SPAM_TEXTS)

        msg = await client.send_message(m.chat.id, text)

        # ⏱ auto delete spam text
        await auto_delete(msg, 50)

    except:
        pass
