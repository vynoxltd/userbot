from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import log_error, mark_plugin_loaded
from datetime import datetime
import os

# =====================
# PLUGIN HEALTH CHECK
# =====================
mark_plugin_loaded("self_destruct_saver.py")

# =====================
# SAVE DIRECTORY
# =====================
SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)

# =====================
# AUTO SAVE SELF-DESTRUCT MEDIA
# =====================
@Client.on_message(
    owner_only &
    (
        filters.photo |
        filters.video |
        filters.document |
        filters.audio |
        filters.animation
    )
)
async def auto_save_self_destruct(client: Client, m):
    try:
        media = (
            m.photo or
            m.video or
            m.document or
            m.audio or
            m.animation
        )

        if not media:
            return

        # ✅ only self-destruct / view-once media
        ttl = getattr(media, "ttl_seconds", None)
        if not ttl:
            return

        # 🔥 download media
        file_path = await m.download(
            file_name=f"{SAVE_DIR}/"
                      f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{m.id}"
        )

        if not file_path:
            return

        caption = (
            "🔥 Self-destruct media saved\n\n"
            f"Chat ID: {m.chat.id}\n"
            f"Message ID: {m.id}\n"
            f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
        )

        # 🔥 send to Saved Messages
        await client.send_document(
            "me",
            file_path,
            caption=caption
        )

    except Exception as e:
        await log_error(client, "self_destruct_saver.py", e)