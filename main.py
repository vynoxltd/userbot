import os
import asyncio
from userbot import bot
from loader import load_plugins
from utils.auto_delete import auto_delete

print("🚀 Starting userbot...")

# load all plugins
load_plugins()

async def startup():
    await bot.start()
    print("✅ Userbot started successfully")

    # 🔔 restart success message
    restart_chat = os.environ.pop("RESTART_CHAT", None)
    if restart_chat:
        try:
            msg = await bot.send_message(
                int(restart_chat),
                "✅ Restarted successfully"
            )
            asyncio.create_task(auto_delete(msg, 5))
        except Exception:
            pass

    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(startup())