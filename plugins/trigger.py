# Triggered Meme Plugin (FIXED)
# Async-safe Telethon Userbot Plugin

import os
import aiohttp
from urllib.parse import quote

from telethon import events
from telegraph import upload_file as uplu

from userbot import bot
from utils.help_registry import register_help
from utils.logger import log_error
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "ptrigger.py"
print("✔ ptrigger.py loaded (Triggered Meme – FIXED)")


@bot.on(events.NewMessage(pattern=r"\.ptrigger$"))
async def ptrigger(e):
    try:
        if not e.is_reply:
            return await e.edit("❌ Reply to a user's message")

        msg = await e.edit("⚙️ Processing...")

        reply = await e.get_reply_message()
        user = await reply.get_sender()

        # Download profile photo
        photo = await bot.download_profile_photo(user.id)
        if not photo:
            return await msg.edit("❌ User has no profile photo")

        # Upload to telegraph
        avatar = uplu(photo)
        img_url = f"https://telegra.ph{avatar[0]}"
        img_url = quote(img_url, safe="")  # URL encode

        api_url = f"https://api.popcat.xyz/triggered?image={img_url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    os.remove(photo)
                    return await msg.edit("❌ Trigger API failed")

                data = await resp.read()

        # Save GIF
        gif_file = "triggered.gif"
        with open(gif_file, "wb") as f:
            f.write(data)

        # Send result
        await bot.send_file(
            e.chat_id,
            gif_file,
            caption="**Triggered 😡**",
            reply_to=reply.id
        )

        await msg.delete()

        # Cleanup
        os.remove(photo)
        os.remove(gif_file)

    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        mark_plugin_error(PLUGIN_NAME)
        await e.edit("❌ Error while generating triggered meme")


mark_plugin_loaded(PLUGIN_NAME)

# =====================
# HELP
# =====================
register_help(
    "ptrigger",
    ".ptrigger (reply)\n\n"
    "• Creates a triggered meme using profile photo\n"
    "• Async-safe (no hang)\n"
    "• Auto cleanup\n"
    "• Uses Popcat API"
                    )
