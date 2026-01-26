from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded
import os
import random

mark_plugin_loaded("neko.py")

# =====================
# NEKO FOLDERS MAP
# =====================
NEKO_FOLDERS = {
    "neko": "assets/neko",
    "nekokiss": "assets/nekokiss",
    "nekohug": "assets/nekohug",
    "nekofuck": "assets/nekofuck",
    "nekoslap": "assets/nekoslap",
}

# =====================
# NEKO HANDLER
# =====================
@Client.on_message(
    owner_only & filters.command(list(NEKO_FOLDERS.keys()), ".")
)
async def neko_handler(client: Client, m):
    try:
        # ❌ delete command safely
        try:
            await m.delete()
        except:
            pass

        cmd = m.command[0].lower()
        folder = NEKO_FOLDERS.get(cmd)

        if not folder or not os.path.isdir(folder):
            msg = await client.send_message(
                m.chat.id,
                f"❌ Folder not found: {folder}"
            )
            await auto_delete(msg, 4)
            return

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith((
                ".jpg", ".jpeg", ".png",
                ".gif", ".webp",
                ".mp4"
            ))
        ]

        if not files:
            msg = await client.send_message(
                m.chat.id,
                f"❌ No media found in {cmd}"
            )
            await auto_delete(msg, 4)
            return

        file_path = os.path.join(folder, random.choice(files))

        # 👇 reply logic
        reply_to_id = (
            m.reply_to_message.id
            if m.reply_to_message
            else None
        )

        sent = await client.send_document(
            chat_id=m.chat.id,
            document=file_path,
            caption=f"😺 {cmd}~",
            reply_to_message_id=reply_to_id
        )

        # ⏱ auto delete after **30 seconds**
        await auto_delete(sent, 30)

    except Exception as e:
        await log_error(client, "neko.py", e)
