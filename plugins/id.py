# plugins/id.py
print("🔥 id.py LOADED 🔥")

import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

# =====================
# PLUGIN INIT
# =====================
print("✔ id.py loaded")

register_help(
    "info",
    ".id\n"
    "Get your ID, chat ID, replied user ID, or channel ID."
)

# =====================
# ID COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.id$"))
async def get_id(e):
    if not is_owner(e):
        return

    try:
        text = "🆔 ID INFO\n\n"

        # 👤 YOUR ID
        if e.sender_id:
            text += f"🙋 Your ID: {e.sender_id}\n"

        # 💬 CHAT INFO
        if e.chat_id:
            text += f"💬 Chat ID: {e.chat_id}\n"

        # 🔐 PRIVATE CHAT → OTHER USER
        if e.is_private and e.chat_id != e.sender_id:
            text += f"\n👤 Other User ID: {e.chat_id}"

        # ↩️ REPLY CASE
        if e.is_reply:
            reply = await e.get_reply_message()

            if reply.sender_id:
                text += f"\n↩️ Replied User ID: {reply.sender_id}"

            elif reply.sender_chat:
                text += f"\n↩️ Replied Channel ID: {reply.sender_chat.id}"

        result = await bot.send_message(e.chat_id, text)

        # ❌ delete command after 1 sec
        async def delete_cmd():
            await asyncio.sleep(1)
            try:
                await e.delete()
            except Exception:
                pass

        # ⏱ delete result after 15 sec
        async def delete_result():
            await asyncio.sleep(15)
            try:
                await result.delete()
            except Exception:
                pass

        asyncio.create_task(delete_cmd())
        asyncio.create_task(delete_result())

    except Exception:
        await log_error(bot, "id.py")