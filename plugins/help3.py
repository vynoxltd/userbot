from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, mark_plugin_loaded

mark_plugin_loaded("help3.py")

HELP3_TEXT = """
USERBOT HELP 3 (VARS + BOT MANAGER)

====================
VARIABLES (VARS)
====================

.setvar | exm: .setvar SPAM_BOT_TOKEN 123456:ABC
Save a variable (token / key / value)

.getvar | exm: .getvar SPAM_BOT_TOKEN
Get saved variable value

.delvar | exm: .delvar SPAM_BOT_TOKEN
Delete a saved variable

.vars | exm: .vars
List all saved variables


====================
BOT MANAGER (MULTI BOT)
====================

.startbot | exm: .startbot spam SPAM_BOT_TOKEN
Start a bot using saved token

.stopbot | exm: .stopbot spam
Stop a running bot

.bots | exm: .bots
Show all running bots


====================
NOTES
====================

• Tokens are stored safely in data/vars.json  
• Bot name is NOT the key  
• Key = variable name  
• Bot name = running bot label  

Example flow:
.setvar SPAM_BOT_TOKEN <token>
.startbot spam SPAM_BOT_TOKEN

All commands are owner-only
"""

@Client.on_message(owner_only & filters.command("help3", "."))
async def help3_cmd(_, m):
    try:
        await m.delete()
    except:
        pass

    msg = await m.reply(HELP3_TEXT)
    await auto_delete(msg, 40)
