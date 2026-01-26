from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete
from database import set_note, get_note, del_note

# ======================
# SET NOTE
# ======================

@Client.on_message(owner_only & filters.command("setnote", "."))
async def setnote(_, m):
    if len(m.command) < 3:
        await m.delete()
        msg = await m.reply("Usage: `.setnote name text`")
        return await auto_delete(msg, 6)

    name = m.command[1]
    text = m.text.split(None, 2)[2]

    await m.delete()
    set_note(name, text)
    msg = await m.reply("✅ Note saved")
    await auto_delete(msg, 5)

# ======================
# GET NOTE
# ======================

@Client.on_message(owner_only & filters.command("getnote", "."))
async def getnote(_, m):
    if len(m.command) < 2:
        await m.delete()
        msg = await m.reply("Usage: `.getnote name`")
        return await auto_delete(msg, 6)

    await m.delete()
    note = get_note(m.command[1])

    if not note:
        msg = await m.reply("❌ Note not found")
        return await auto_delete(msg, 5)

    msg = await m.reply(note)
    await auto_delete(msg, 15)

# ======================
# DELETE NOTE
# ======================

@Client.on_message(owner_only & filters.command("delnote", "."))
async def delnote(_, m):
    if len(m.command) < 2:
        await m.delete()
        msg = await m.reply("Usage: `.delnote name`")
        return await auto_delete(msg, 6)

    await m.delete()
    del_note(m.command[1])
    msg = await m.reply("🗑 Note deleted")
    await auto_delete(msg, 5)