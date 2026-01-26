from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import random, asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("games.py")

@Client.on_message(owner_only & filters.command(["dice","coin","luck","rate","roll"], "."))
async def games(client, m):
    try:
        cmd = m.command[0]
        await m.delete()

        if cmd == "dice":
            text = f"🎲 Dice: {random.randint(1,6)}"

        elif cmd == "coin":
            text = f"🪙 Coin: {random.choice(['Head','Tail'])}"

        elif cmd == "luck":
            text = f"🍀 Luck: {random.randint(0,100)}%"

        elif cmd == "rate":
            text = f"⭐ Rating: {random.randint(0,10)}/10"

        elif cmd == "roll":
            num = int(m.command[1]) if len(m.command)>1 else 100
            text = f"🎯 Rolled: {random.randint(1,num)}"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 6)

    except Exception as e:
        await log_error(client, "games.py", e)