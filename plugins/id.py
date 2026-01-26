from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
import asyncio


@Client.on_message(owner_only & filters.command("id", prefixes="."))
async def get_id(client: Client, m):
    try:
        text = "🆔 **ID INFO**\n\n"

        # 👤 YOUR ID
        if m.from_user:
            text += f"🙋‍♂️ Your ID: `{m.from_user.id}`\n"

        # 💬 CHAT INFO
        if m.chat:
            text += f"💬 Chat ID: `{m.chat.id}`\n"
            text += f"📌 Chat Type: `{m.chat.type}`\n"

        # 🔐 PRIVATE CHAT → OTHER USER
        if m.chat.type == "private" and m.chat.id != m.from_user.id:
            text += f"\n👤 Other User ID: `{m.chat.id}`"

        # ↩️ REPLY CASE
        if m.reply_to_message:
            if m.reply_to_message.from_user:
                text += f"\n↩️ Replied User ID: `{m.reply_to_message.from_user.id}`"
            elif m.reply_to_message.sender_chat:
                text += f"\n↩️ Replied Channel ID: `{m.reply_to_message.sender_chat.id}`"

        # 📤 send result
        result = await m.reply(text)

        # ❌ delete command after 1 sec
        async def delete_cmd():
            await asyncio.sleep(1)
            try:
                await m.delete()
            except:
                pass

        # ⏱ delete result after 15 sec
        async def delete_result():
            await asyncio.sleep(15)
            try:
                await result.delete()
            except:
                pass

        asyncio.create_task(delete_cmd())
        asyncio.create_task(delete_result())

    except Exception as e:
        await log_error(client, "id.py", e)