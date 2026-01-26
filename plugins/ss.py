from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import log_error
from datetime import datetime
import os, uuid
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("ss.py")

TARGET_CHAT = "@testuserbotss"

SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)


@Client.on_message(
    owner_only &
    filters.command("ss", prefixes=".") &
    filters.reply
)
async def ss_handler(client: Client, m):
    try:
        reply = m.reply_to_message

        # delete command instantly
        try:
            await m.delete()
        except:
            pass

        if not reply:
            return

        media = (
            reply.photo or
            reply.video or
            reply.document or
            reply.animation or
            reply.audio
        )

        if not media:
            return

        # ONLY self-destruct / view-once
        if not getattr(media, "ttl_seconds", None):
            return

        # filename
        if getattr(media, "file_name", None):
            filename = media.file_name
        else:
            ext = (
                ".jpg" if reply.photo else
                ".mp4" if reply.video or reply.animation else
                ".mp3" if reply.audio else
                ".bin"
            )
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:5]}{ext}"

        path = os.path.join(SAVE_DIR, filename)

        # download
        await reply.download(file_name=path)

        # send to group/channel (NO parse_mode ❗)
        await client.send_document(
            TARGET_CHAT,
            path,
            caption=(
                "🔥 Self-destruct media saved\n\n"
                f"Chat ID: {reply.chat.id}\n"
                f"Message ID: {reply.id}\n"
                f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
            )
        )

    except Exception as e:
        await log_error(client, "ss.py", e)