from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import log_error
import asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("spam.py")

# =====================
# 16️⃣ SPAM
# =====================
@Client.on_message(owner_only & filters.command("spam", "."))
async def spam(client: Client, m):
    try:
        if len(m.command) < 3 or not m.command[1].isdigit():
            err = await m.reply("Usage: `.spam <count> <text>`")
            await asyncio.sleep(3)
            await err.delete()
            return

        count = int(m.command[1])
        text = m.text.split(None, 2)[2]

        await m.delete()

        for _ in range(count):
            await client.send_message(m.chat.id, text)
            await asyncio.sleep(0.4)

    except Exception as e:
        await log_error(client, "spam.py", e)


# =====================
# 18️⃣ DELAYSPAM
# =====================
@Client.on_message(owner_only & filters.command("delayspam", "."))
async def delayspam(client: Client, m):
    try:
        if len(m.command) < 4 or not m.command[1].isdigit():
            err = await m.reply("Usage: `.delayspam <count> <delay> <text>`")
            await asyncio.sleep(3)
            await err.delete()
            return

        count = int(m.command[1])
        delay = float(m.command[2])
        text = m.text.split(None, 3)[3]

        await m.delete()

        for _ in range(count):
            await client.send_message(m.chat.id, text)
            await asyncio.sleep(delay)

    except Exception as e:
        await log_error(client, "spam.py", e)


# =====================
# 20️⃣ REPLYSPAM
# =====================
@Client.on_message(
    owner_only &
    filters.command("replyspam", ".") &
    filters.reply
)
async def replyspam(client: Client, m):
    try:
        if len(m.command) < 2 or not m.command[1].isdigit():
            err = await m.reply("Usage: `.replyspam <count>` (reply required)")
            await asyncio.sleep(3)
            await err.delete()
            return

        count = int(m.command[1])
        reply_to = m.reply_to_message

        await m.delete()

        for _ in range(count):
            await reply_to.reply(reply_to.text or "👀")
            await asyncio.sleep(0.4)

    except Exception as e:
        await log_error(client, "spam.py", e)