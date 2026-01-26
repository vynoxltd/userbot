from pyrogram import Client, idle
from config import API_ID, API_HASH
import os, asyncio
from plugins.utils import auto_delete

print("🚀 Starting userbot...")

app = Client(
    "my_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=dict(root="plugins")
)

app.start()
print("✅ Userbot started successfully")

# 🔔 restart success
if "RESTART_CHAT" in os.environ:
    chat_id = int(os.environ.pop("RESTART_CHAT"))
    try:
        msg = app.send_message(chat_id, "✅ Restarted successfully")
        app.loop.create_task(auto_delete(msg, 5))
    except:
        pass

idle()
app.stop()