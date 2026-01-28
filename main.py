# main.py
import os
import asyncio
from userbot import bot
from loader import load_plugins
from utils.auto_delete import auto_delete

async def main():
    print("🚀 Starting userbot...")

    load_plugins()

    await bot.start()
    print("✅ Userbot started successfully")

    # restart message
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

    # 👇 IMPORTANT PART
    await asyncio.Event().wait()   # keeps loop alive FOREVER


if __name__ == "__main__":
    asyncio.run(main())
