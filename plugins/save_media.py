from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete
from datetime import datetime
import os, uuid, asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("save_media.py")

SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)


@Client.on_message(
    owner_only &
    filters.command("save", prefixes=".") &
    filters.reply
)
async def manual_media_save(client: Client, m):
    reply = m.reply_to_message

    # ❌ delete command immediately
    await m.delete()

    media = (
        reply.photo or
        reply.video or
        reply.document or
        reply.audio or
        reply.animation
    )

    if not media:
        msg = await client.send_message(m.chat.id, "❌ Reply to a media message")
        await auto_delete(msg, 5)
        return

    try:
        # 🔥 filename + extension
        if hasattr(media, "file_name") and media.file_name:
            filename = media.file_name
        else:
            ext = (
                ".jpg" if reply.photo else
                ".mp4" if reply.video or reply.animation else
                ".bin"
            )
            filename = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                f"{uuid.uuid4().hex[:6]}{ext}"
            )

        path = os.path.join(SAVE_DIR, filename)

        await reply.download(file_name=path)

        # ✅ confirmation message
        msg = await client.send_message(
            m.chat.id,
            "✅ Media saved successfully"
        )

        # ⏱ auto delete confirmation
        await auto_delete(msg, 4)

    except Exception as e:
        err = await client.send_message(
            m.chat.id,
            f"❌ Save failed:\n`{e}`"
        )
        await auto_delete(err, 6)