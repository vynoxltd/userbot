from pyrogram import Client, filters
from plugins.owner import owner_only

@Client.on_message(owner_only & filters.command("help", prefixes="."))
async def help_cmd(_, m):
    await m.reply("Help working ✅")