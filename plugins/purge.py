from plugins.utils import log_error
from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import asyncio


# =====================
# PURGE (reply based)
# =====================
@Client.on_message(owner_only & filters.command("purge", ".") & filters.reply)
async def purge_handler(client: Client, m):
    try:
        chat_id = m.chat.id
        start_id = m.reply_to_message.id
        end_id = m.id

        # delete command
        await m.delete()

        msg_ids = list(range(start_id, end_id + 1))
        await client.delete_messages(chat_id, msg_ids)

        done = await client.send_message(chat_id, "✅ Purged complete")
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "cleanup.py", e)


# =====================
# CLEAN (count based)
# =====================
@Client.on_message(owner_only & filters.command("clean", "."))
async def clean_handler(client: Client, m):
    try:
        if len(m.command) < 2 or not m.command[1].isdigit():
            err = await m.reply("Usage: `.clean <count>`")
            await auto_delete(err, 4)
            return

        count = int(m.command[1])

        # delete command
        await m.delete()

        msg_ids = []
        async for msg in client.get_chat_history(m.chat.id, limit=count):
            msg_ids.append(msg.id)

        if msg_ids:
            await client.delete_messages(m.chat.id, msg_ids)

        done = await client.send_message(
            m.chat.id,
            f"✅ Cleaned {len(msg_ids)} messages"
        )
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "cleanup.py", e)


# =====================
# DEL (single message)
# =====================
@Client.on_message(owner_only & filters.command("del", ".") & filters.reply)
async def del_single(client: Client, m):
    try:
        await m.delete()
        await client.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id
        )

    except Exception as e:
        await log_error(client, "cleanup.py", e)


# =====================
# DELALL (user based)
# =====================
@Client.on_message(owner_only & filters.command("delall", ".") & filters.reply)
async def del_all(client: Client, m):
    try:
        chat_id = m.chat.id
        target = m.reply_to_message.from_user

        if not target:
            return

        await m.delete()

        msg_ids = []
        async for msg in client.get_chat_history(chat_id, limit=1000):
            if msg.from_user and msg.from_user.id == target.id:
                msg_ids.append(msg.id)

        if msg_ids:
            await client.delete_messages(chat_id, msg_ids)

            done = await client.send_message(
                chat_id,
                f"✅ Deleted {len(msg_ids)} messages from {target.first_name}"
            )
            await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "cleanup.py", e)