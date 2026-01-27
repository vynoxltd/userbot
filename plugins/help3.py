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
exm: .setvar API_KEY 12345

.getvar <KEY>
exm: .getvar API_KEY

.delvar <KEY>
exm: .delvar API_KEY

.vars
exm: .vars

• Vars are stored in data/vars.json
• Used by plugins (not botmanager)


====================
BOT MANAGER (MULTI BOT)
====================

.addbot <name> <token>
exm: .addbot spam 123456:ABCDEF

.startbot <name>
exm: .startbot spam

.stopbot <name>
exm: .stopbot spam

.delbot <name>
exm: .delbot spam

.bots
exm: .bots

• Tokens are saved automatically
• No VAR_KEY required
• BOT_<NAME> handled internally


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
• Files picked randomly


====================
PLUGIN HEALTH
====================

.help broken

• Shows failed plugins
• Error + time shown
• Useful if botmanager / neko fails


====================
NOTES
====================

• All commands are owner-only
• Botmanager ≠ Vars system
• Bot name = runtime label
• Restart heals disabled plugins

"""

@Client.on_message(owner_only & filters.command("help3", "."))
async def help3_cmd(_, m):
    try:
        await m.delete()
    except:
        pass

    msg = await m.reply(HELP3_TEXT)
    await auto_delete(msg, 40)
