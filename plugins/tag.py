from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded
import asyncio

mark_plugin_loaded("tag.py")

@Client.on_message(owner_only & filters.command("tag", "."))
async def tag_user(client: Client, m):
    try:
        # 🧹 delete command safely
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 4:
            msg = await client.send_message(
                m.chat.id,
                "Usage: .tag <count> <text> <username>"
            )
            await auto_delete(msg, 4)
            return

        # 🔢 parse args
        count = int(m.command[1])
        text = m.command[2]
        username = m.command[3]

        if not username.startswith("@"):
            username = "@" + username

        # 🔁 tagging loop
        for _ in range(count):
            await client.send_message(
                m.chat.id,
                f"{text} {username}"
            )
            await asyncio.sleep(1.2)  # safe delay (no flood)

    except Exception as e:
        await log_error(client, "tag.py", e)