from telethon import events
from userbot import bot

@bot.on(events.NewMessage(pattern=r"\.pingg"))
async def ping(e):
    await e.reply("🏓 pong")
