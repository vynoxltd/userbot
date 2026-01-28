# main.py
import os
import asyncio

from userbot import bot
from loader import load_plugins
from utils.auto_delete import auto_delete

async def main():
    print("🚀 Starting userbot...")

    # ✅ FIRST start bot
    await bot.start()
    print("✅ Userbot started")

    # ✅ THEN load plugins (VERY IMPORTANT)
    load_plugins()

    # 🔔 restart success msg
    restart_chat = os.environ.pop("RESTART_CHAT", None)
    if restart_chat:
        try:
            msg = await bot.send_message(
                int(restart_chat),
                "✅ Restarted successfully"
            )
            asyncio.create_task(auto_delete(msg, 5))
        except:
            pass

    # keep alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
