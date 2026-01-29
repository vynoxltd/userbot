# main.py
import os
import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

from loader import load_plugins
from utils.auto_delete import auto_delete

# =====================
# ENV VARIABLES (SAFE)
# =====================
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

if not API_ID or not API_HASH or not STRING_SESSION:
    raise RuntimeError(
        "❌ API_ID / API_HASH / STRING_SESSION missing in Railway env"
    )

API_ID = int(API_ID)

# =====================
# TELETHON CLIENT
# =====================
bot = TelegramClient(
    StringSession(STRING_SESSION),
    API_ID,
    API_HASH
)

# =====================
# MAIN STARTUP
# =====================
async def main():
    print("🚀 Starting userbot...")

    # ✅ LOGIN FIRST
    await bot.start()
    print("✅ Userbot logged in successfully")

    # ✅ LOAD PLUGINS AFTER LOGIN
    load_plugins()
    print("✅ Plugins loaded")

    # 🔔 restart success message (optional)
    restart_chat = os.environ.pop("RESTART_CHAT", None)
    if restart_chat:
        try:
            msg = await bot.send_message(
                int(restart_chat),
                "✅ Restarted successfully"
            )
            asyncio.create_task(auto_delete(msg, 5))
        except Exception as e:
            print("Restart msg failed:", e)

    # ✅ KEEP PROCESS ALIVE
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
