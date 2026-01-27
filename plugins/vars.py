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
    register_help
)

mark_plugin_loaded("vars.py")

# 🔥 help4 register
register_help(
    "vars",
    """
.setvar KEY VALUE
Example: .setvar TEST hello

.getvar KEY
Example: .getvar TEST

.delvar KEY
Example: .delvar TEST

.vars
List all variables

• Stored in data/vars.json
"""
)

# =====================
# SET VAR
# =====================
@Client.on_message(owner_only & filters.command("setvar", "."))
async def setvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 3:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.setvar KEY VALUE"
            )
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = m.text.split(None, 2)[2]

        set_var(key, value)

        msg = await client.send_message(
            m.chat.id,
            f"✅ Saved `{key}`"
        )
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# GET VAR
# =====================
@Client.on_message(owner_only & filters.command("getvar", "."))
async def getvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.getvar KEY"
            )
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        value = get_var(key)

        if value is None:
            msg = await client.send_message(
                m.chat.id,
                "❌ Variable not found"
            )
        else:
            msg = await client.send_message(
                m.chat.id,
                f"`{key}` = `{value}`"
            )

        await auto_delete(msg, 10)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# DELETE VAR
# =====================
@Client.on_message(owner_only & filters.command("delvar", "."))
async def delvar_cmd(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                "Usage:\n.delvar KEY"
            )
            return await auto_delete(msg, 5)

        key = m.command[1].upper()
        del_var(key)

        msg = await client.send_message(
            m.chat.id,
            f"🗑 Deleted `{key}`"
        )
        await auto_delete(msg, 5)

    except Exception as e:
        await log_error(client, "vars.py", e)


# =====================
# LIST VARS
# =====================
@Client.on_message(owner_only & filters.command("vars", "."))
async def vars_cmd(client: Client, m):
    try:
        await m.delete()

        data = all_vars()
        if not data:
            msg = await client.send_message(
                m.chat.id,
                "No variables saved"
            )
            return await auto_delete(msg, 5)

        text = "📦 VARIABLES\n\n"
        for k in data:
            text += f"• `{k}`\n"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 15)

    except Exception as e:
        await log_error(client, "vars.py", e)
