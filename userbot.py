from pyrogram import Client, idle
import os, asyncio
from config import API_ID, API_HASH
from plugins.utils import auto_delete

print("🚀 Starting userbot...")

# ✅ STRING SESSION FROM ENV
STRING_SESSION = os.environ.get("SESSION_STRING")

if not STRING_SESSION:
    raise RuntimeError("SESSION_STRING is missing in environment variables")

app = Client(
    name="userbot",                 # 🔥 THIS WAS MISSING
    session_string=STRING_SESSION,  # ✅ correct
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
