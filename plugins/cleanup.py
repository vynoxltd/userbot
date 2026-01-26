from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import asyncio


# =====================
# HELPER: CHECK ADMIN
# =====================
async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


# =====================
# PURGE (reply based)
# =====================
@Client.on_message(owner_only & filters.command("purge", ".") & filters.reply)
async def purge_handler(client: Client, m):
    try:
        chat_id = m.chat.id
        user_id = m.from_user.id
        start_id = m.reply_to_message.id
        end_id = m.id - 1  # command ke niche tak

        # delete command first
        await m.delete()

        if start_id > end_id:
            return

        admin = await is_admin(client, chat_id, user_id)

        msg_ids = []

        async for msg in client.get_chat_history(
            chat_id,
            offset_id=end_id + 1,
            limit=(end_id - start_id + 1)
        ):
            if msg.id < start_id:
                break

            # non-admin → sirf apne msg
            if not admin:
                if msg.from_user and msg.from_user.id == user_id:
                    msg_ids.append(msg.id)
            else:
                msg_ids.append(msg.id)

        # batch delete (flood safe)
        for i in range(0, len(msg_ids), 100):
            await client.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await client.send_message(chat_id, "✅ Purge complete")
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
        chat_id = m.chat.id
        user_id = m.from_user.id

        await m.delete()

        admin = await is_admin(client, chat_id, user_id)
        msg_ids = []

        async for msg in client.get_chat_history(chat_id, limit=count):
            if not admin:
                if msg.from_user and msg.from_user.id == user_id:
                    msg_ids.append(msg.id)
            else:
                msg_ids.append(msg.id)

        for i in range(0, len(msg_ids), 100):
            await client.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await client.send_message(
            chat_id,
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
        chat_id = m.chat.id
        user_id = m.from_user.id
        target_msg = m.reply_to_message

        await m.delete()

        admin = await is_admin(client, chat_id, user_id)

        # non-admin → sirf apna msg
        if not admin:
            if not target_msg.from_user or target_msg.from_user.id != user_id:
                return

        await client.delete_messages(chat_id, target_msg.id)

    except Exception as e:
        await log_error(client, "cleanup.py", e)


# =====================
# DELALL (user based)
# =====================
@Client.on_message(owner_only & filters.command("delall", ".") & filters.reply)
async def del_all(client: Client, m):
    try:
        chat_id = m.chat.id
        user_id = m.from_user.id
        target = m.reply_to_message.from_user

        if not target:
            return

        await m.delete()

        admin = await is_admin(client, chat_id, user_id)

        # non-admin → sirf apne liye allowed
        if not admin and target.id != user_id:
            return

        msg_ids = []

        async for msg in client.get_chat_history(chat_id, limit=1000):
            if msg.from_user and msg.from_user.id == target.id:
                msg_ids.append(msg.id)

        for i in range(0, len(msg_ids), 100):
            await client.delete_messages(chat_id, msg_ids[i:i + 100])
            await asyncio.sleep(0.5)

        done = await client.send_message(
            chat_id,
            f"✅ Deleted {len(msg_ids)} messages from {target.first_name}"
        )
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "cleanup.py", e)
