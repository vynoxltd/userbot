from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("forward.py")

# =====================
# FWD
# =====================
@Client.on_message(owner_only & filters.command("fwd", ".") & filters.reply)
async def fwd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage: `.fwd <chat_id | @username>`"
            )
            await auto_delete(msg, 4)
            return

        target = m.command[1]
        await m.reply_to_message.forward(target)

        done = await client.send_message(m.chat.id, "✅ Forwarded")
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "forward.py", e)


# =====================
# SILENT FWD
# =====================
@Client.on_message(owner_only & filters.command("sfwd", ".") & filters.reply)
async def silent_fwd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            return

        target = m.command[1]
        await m.reply_to_message.forward(target)

    except Exception as e:
        await log_error(client, "forward.py", e)


# =====================
# FWD HERE
# =====================
@Client.on_message(owner_only & filters.command("fwdhere", ".") & filters.reply)
async def fwd_here(client: Client, m):
    try:
        await m.delete()

        await m.reply_to_message.forward(m.chat.id)

        done = await client.send_message(m.chat.id, "✅ Forwarded here")
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "forward.py", e)


# =====================
# MULTI FWD
# =====================
@Client.on_message(owner_only & filters.command("mfwd", ".") & filters.reply)
async def multi_fwd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 3:
            msg = await client.send_message(
                m.chat.id,
                "Usage: `.mfwd <chat_id | @username> <count>`"
            )
            await auto_delete(msg, 4)
            return

        target = m.command[1]
        count = int(m.command[2])

        start_id = m.reply_to_message.id
        msg_ids = list(range(start_id, start_id + count))

        for msg_id in msg_ids:
            try:
                await client.forward_messages(
                    chat_id=target,
                    from_chat_id=m.chat.id,
                    message_ids=msg_id
                )
                await asyncio.sleep(0.3)
            except:
                pass

        done = await client.send_message(
            m.chat.id,
            f"✅ Forwarded {len(msg_ids)} messages"
        )
        await auto_delete(done, 3)

    except Exception as e:
        await log_error(client, "forward.py", e)