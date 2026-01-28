import os
import uuid
import asyncio
from datetime import datetime
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help

print("✔ save_media.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "media",
    ".save (reply)\n\n"
    "• Saves replied media permanently\n"
    "• Works for photo / video / doc / audio / gif\n"
    "• Media sent to Saved Messages\n"
    "• Local disk auto-cleared"
)

# =====================
# CONFIG
# =====================
SAVE_DIR = "saved_media"
os.makedirs(SAVE_DIR, exist_ok=True)

# =====================
# SAVE MEDIA
# =====================
@bot.on(events.NewMessage(pattern=r"\.save$"))
async def manual_media_save(e):
    if not is_owner(e):
        return

    try:
        # ❌ delete command instantly
        try:
            await e.delete()
        except Exception:
            pass

        if not e.is_reply:
            msg = await bot.send_message(
                e.chat_id,
                "❌ Reply to a media message"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        reply = await e.get_reply_message()

        # media detection
        media = reply.media
        if not media:
            msg = await bot.send_message(
                e.chat_id,
                "❌ Reply to a media message"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        # 🔤 filename
        filename = None
        if reply.file and reply.file.name:
            filename = reply.file.name
        else:
            ext = (
                ".jpg" if reply.photo else
                ".mp4" if reply.video or reply.gif else
                ".mp3" if reply.audio else
                ".bin"
            )
            filename = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                f"{uuid.uuid4().hex[:6]}{ext}"
            )

        path = os.path.join(SAVE_DIR, filename)

        # ⬇️ download (temporary)
        await bot.download_media(reply, file=path)

        # 📤 send to Saved Messages (permanent)
        await bot.send_file(
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
        except Exception:
            pass

        msg = await bot.send_message(
            e.chat_id,
            "✅ Saved to Saved Messages"
        )
        await asyncio.sleep(4)
        await msg.delete()

    except Exception:
        await log_error(bot, "save_media.py")