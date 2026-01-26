from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, mark_plugin_loaded

# ✅ mark plugin loaded (health system)
mark_plugin_loaded("help3.py")

HELP3_TEXT = """
USERBOT HELP 3 (VARS • BOT MANAGER • NEKO)

====================
VARIABLES (VARS)
====================

.setvar <KEY> <VALUE>
exm: .setvar SPAM_BOT_TOKEN 123456:ABC

.getvar <KEY>
exm: .getvar SPAM_BOT_TOKEN

.delvar <KEY>
exm: .delvar SPAM_BOT_TOKEN

.vars
exm: .vars


====================
BOT MANAGER (MULTI BOT)
====================

.startbot <name> <VAR_KEY>
exm: .startbot spam SPAM_BOT_TOKEN

.stopbot <name>
exm: .stopbot spam

.bots
exm: .bots


====================
NEKO FUN COMMANDS
====================

.neko
.nekokiss
.nekohug
.nekoslap
.nekofuck

• Reply / without reply — both work
• Media auto deletes after 30 seconds
• Files picked randomly from assets folder


====================
NOTES
====================

• All commands are owner-only
• Vars are stored in data/vars.json
• Key ≠ Bot name
• Bot name = running bot label

Example flow:
.setvar SPAM_BOT_TOKEN <token>
.startbot spam SPAM_BOT_TOKEN
"""

@Client.on_message(owner_only & filters.command("help3", "."))
async def help3_cmd(_, m):
    try:
        await m.delete()
    except:
        pass

    msg = await m.reply(HELP3_TEXT)
    await auto_delete(msg, 40)
