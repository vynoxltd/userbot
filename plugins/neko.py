from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import os
import random
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("neko.py")

# 📁 neko media folder
NEKO_DIR = "assets/neko"

@Client.on_message(owner_only & filters.command("neko", "."))
async def neko_cmd(client: Client, m):
    try:
        # ❌ delete command immediately
        await m.delete()

        if not os.path.isdir(NEKO_DIR):
            msg = await client.send_message(
                m.chat.id,
                "❌ neko folder not found"
            )
            await auto_delete(msg, 4)
            return

        files = [
            f for f in os.listdir(NEKO_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
        ]

        if not files:
            msg = await client.send_message(
                m.chat.id,
                "❌ No neko files found"
            )
            await auto_delete(msg, 4)
            return

        file_path = os.path.join(NEKO_DIR, random.choice(files))

        sent = await client.send_document(
            chat_id=m.chat.id,
            document=file_path,
            caption="😺 neko~"
        )

        # ⏱ auto delete sent media
        await auto_delete(sent, 10)

    except Exception as e:
        await log_error(client, "neko.py", e)