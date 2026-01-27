from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    set_var,
    get_var,
    del_var,
    all_vars,
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("vars.py")

# =====================
# HELP4 AUTO REGISTER
# =====================
register_help(
    "vars",
    """
.setvar KEY VALUE
exm: .setvar AUTOREPLY_MORNING Good morning

.getvar KEY
exm: .getvar AUTOREPLY_MORNING

.delvar KEY
exm: .delvar AUTOREPLY_MORNING

.vars
List all saved variables

• Variables are saved in data/vars.json
• Used by autoreply, botmanager, etc.
"""
)

# =====================
# SET VAR
# =====================
@Client.on_message(owner_only & filters.command("setvar", prefixes="."))
async def setvar_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 3:
            msg = await m.reply("Usage:\n.setvar KEY VALUE")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = m.text.split(None, 2)[2]

        set_var(key, value)

        msg = await m.reply(f"✅ Variable saved\n`{key}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# GET VAR
# =====================
@Client.on_message(owner_only & filters.command("getvar", prefixes="."))
async def getvar_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.getvar KEY")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = get_var(key)

        if value is None:
            msg = await m.reply("❌ Variable not found")
        else:
            msg = await m.reply(f"`{key}` = `{value}`")

        await auto_delete(msg, 10)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# DELETE VAR
# =====================
@Client.on_message(owner_only & filters.command("delvar", prefixes="."))
async def delvar_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 2:
            msg = await m.reply("Usage:\n.delvar KEY")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        del_var(key)

        msg = await m.reply(f"🗑 Variable deleted: `{key}`")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# LIST VARS
# =====================
@Client.on_message(owner_only & filters.command("vars", prefixes="."))
async def vars_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        data = all_vars()

        if not data:
            msg = await m.reply("No variables saved")
            return await auto_delete(msg, 5)

        text = "📦 SAVED VARIABLES\n\n"
        for k in data:
            text += f"• `{k}`\n"

        msg = await m.reply(text)
        await auto_delete(msg, 15)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)
