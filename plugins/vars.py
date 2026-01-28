from pyrogram import Client, filters
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
# HELP REGISTER
# =====================
register_help(
    "vars",
    """
.setvar KEY VALUE
.getvar KEY
.delvar KEY
.vars

[Test Mode – owner_only disabled]
"""
)

# =====================
# SET VAR (TEST)
# =====================
@Client.on_message(filters.command("setvar", prefixes="."))
async def setvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 3:
            msg = await m.reply("Usage: .setvar KEY VALUE")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = m.text.split(None, 2)[2]

        set_var(key, value)

        msg = await m.reply(f"✅ SAVED\n{key} = {value}")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# GET VAR (TEST)
# =====================
@Client.on_message(filters.command("getvar", prefixes="."))
async def getvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await m.reply("Usage: .getvar KEY")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = get_var(key)

        if value is None:
            msg = await m.reply("❌ Variable not found")
        else:
            msg = await m.reply(f"{key} = {value}")

        await auto_delete(msg, 10)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# DELETE VAR (TEST)
# =====================
@Client.on_message(filters.command("delvar", prefixes="."))
async def delvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await m.reply("Usage: .delvar KEY")
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        del_var(key)

        msg = await m.reply(f"🗑 Deleted: {key}")
        await auto_delete(msg, 5)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)


# =====================
# LIST VARS (TEST)
# =====================
@Client.on_message(filters.command("vars", prefixes="."))
async def vars_cmd(client: Client, m):
    try:
        await m.delete()

        data = all_vars()

        if not data:
            msg = await m.reply("📭 No variables saved")
            return await auto_delete(msg, 5)

        text = "📦 VARIABLES\n\n"
        for k, v in data.items():
            text += f"{k} = {v}\n"

        msg = await m.reply(text)
        await auto_delete(msg, 15)

    except Exception as e:
        mark_plugin_error("vars.py", e)
        await log_error(client, "vars.py", e)
