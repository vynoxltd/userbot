from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import time, asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("stats.py")

START_TIME = time.time()
MSG_COUNT = 0


def uptime():
    s = int(time.time() - START_TIME)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}h {m}m {s}s"


# 📊 STATS COMMAND
@Client.on_message(owner_only & filters.command("stats", "."))
async def stats_handler(client: Client, m):
    global MSG_COUNT
    try:
        await m.delete()

        me = await client.get_me()

        groups = channels = 0
        g_admin = g_owner = 0
        c_admin = c_owner = 0

        async for d in client.get_dialogs():
            chat = d.chat

            # GROUPS
            if chat.type in ("group", "supergroup"):
                groups += 1
                try:
                    member = await client.get_chat_member(chat.id, me.id)
                    if member.status == "administrator":
                        g_admin += 1
                    elif member.status == "creator":
                        g_owner += 1
                except:
                    pass

            # CHANNELS
            elif chat.type == "channel":
                channels += 1
                try:
                    member = await client.get_chat_member(chat.id, me.id)
                    if member.status == "administrator":
                        c_admin += 1
                    elif member.status == "creator":
                        c_owner += 1
                except:
                    pass

        text = (
            "📊 **Telegram Profile Stats**\n\n"
            f"👤 **User:** {me.first_name}\n"
            f"🆔 **Your ID:** `{me.id}`\n\n"
            f"👥 **Groups:** `{groups}`\n"
            f"🛡 Admin in Groups: `{g_admin}`\n"
            f"👑 Owner of Groups: `{g_owner}`\n\n"
            f"📢 **Channels:** `{channels}`\n"
            f"🛡 Admin in Channels: `{c_admin}`\n"
            f"👑 Owner of Channels: `{c_owner}`\n\n"
            f"💬 **Messages Sent (session):** `{MSG_COUNT}`\n"
            f"⏱ **Uptime:** `{uptime()}`"
        )

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 20)

    except Exception as e:
        await log_error(client, "stats.py", e)


# 💬 MESSAGE COUNTER (session based)
@Client.on_message(filters.me & ~filters.command("stats", "."))
async def count_my_messages(_, __):
    global MSG_COUNT
    MSG_COUNT += 1