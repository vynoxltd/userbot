from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded
from datetime import datetime
import os, uuid

mark_plugin_loaded("save_media.py")

SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)

@Client.on_message(
    owner_only &
    filters.command("save", prefixes=".") &
    filters.reply
)
async def manual_media_save(client: Client, m):
    try:
        reply = m.reply_to_message

        # ❌ delete command instantly
        try:
            await m.delete()
        except:
            pass

        media = (
            reply.photo or
            reply.video or
            reply.document or
            reply.audio or
            reply.animation
        )

        if not media:
            msg = await client.send_message(
                m.chat.id,
                "❌ Reply to a media message"
            )
            await auto_delete(msg, 5)
            return

        # 🔤 filename
        if getattr(media, "file_name", None):
            filename = media.file_name
        else:
            ext = (
                ".jpg" if reply.photo else
                ".mp4" if reply.video or reply.animation else
                ".mp3" if reply.audio else
                ".bin"
            )
            filename = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                f"{uuid.uuid4().hex[:6]}{ext}"
            )

        path = os.path.join(SAVE_DIR, filename)

        # ⬇️ download (disk temporary)
        await reply.download(file_name=path)

        # 📤 send to Saved Messages (permanent)
        await client.send_document(
            "me",
            path,
            caption=(
                "✅ Media saved\n\n"
                f"📁 File: {filename}\n"
                f"⏰ Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
            )
        )

        # 🧹 AUTO CLEAR DISK
        try:
            os.remove(path)
        except:
            pass

        msg = await client.send_message(
            m.chat.id,
            "✅ Saved to Saved Messages"
        )
        await auto_delete(msg, 4)

    except Exception as e:
        await log_error(client, "save_media.py", e)
