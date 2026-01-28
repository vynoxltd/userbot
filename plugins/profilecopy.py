from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help,
    mongo
)
import asyncio
import time
import os
from datetime import datetime

mark_plugin_loaded("profilecopy.py")

# =====================
# HELP
# =====================
register_help(
    "profilecopy",
    """
.backupprofile
.backupprofile force
.restoreprofile
.backupinfo

.copybio   (reply)
.copyname  (reply)
.copydp    (reply)

.clone <seconds> (reply)
.clonestatus

.steal (reply)

.silentclone on/off
"""
)

# =====================
# MONGO
# =====================
db = mongo["userbot"]
profile_col = db["profile_backup"]

# =====================
# GLOBAL STATE
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
SILENT_MODE = False
CLONE_TASK = None

# =====================
# HELPERS
# =====================
async def _apply_name(client, user):
    await client.update_profile(
        first_name=user.first_name,
        last_name=user.last_name
    )

async def _apply_bio(client, user):
    chat = await client.get_chat(user.id)
    await client.update_profile(bio=chat.bio or "")

async def _apply_dp(client, user):
    photos = []
    async for p in client.get_chat_photos(user.id, limit=1):
        photos.append(p)

    if not photos:
        return False

    file = await client.download_media(photos[0].file_id)
    await client.set_profile_photo(photo=file)
    os.remove(file)
    return True

# =====================
# BACKUP PROFILE (WITH DP)
# =====================
async def backup_profile(client, force=False):
    if profile_col.find_one({"_id": "backup"}) and not force:
        return False

    me = await client.get_me()
    chat = await client.get_chat(me.id)

    dp_msg_id = None
    photos = []
    async for p in client.get_chat_photos(me.id, limit=1):
        photos.append(p)

    if photos:
        file = await client.download_media(photos[0].file_id)
        sent = await client.send_photo("me", photo=file)
        dp_msg_id = sent.id
        os.remove(file)

    profile_col.update_one(
        {"_id": "backup"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": chat.bio or "",
            "dp_msg_id": dp_msg_id,
            "backup_time": datetime.now().strftime("%d %b %Y %I:%M %p")
        }},
        upsert=True
    )
    return True

# =====================
# RESTORE PROFILE (WITH DP)
# =====================
async def restore_profile(client):
    data = profile_col.find_one({"_id": "backup"})
    if not data:
        return False

    await client.update_profile(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        bio=data.get("bio")
    )

    dp_msg_id = data.get("dp_msg_id")
    if dp_msg_id:
        msg = await client.get_messages("me", dp_msg_id)
        file = await msg.download()
        await client.set_profile_photo(photo=file)
        os.remove(file)

    return True

# =====================
# BACKUP / RESTORE CMDS
# =====================
@Client.on_message(owner_only & filters.command("backupprofile", "."))
async def backup_cmd(client, m):
    try:
        await m.delete()
        force = len(m.command) > 1 and m.command[1] == "force"
        ok = await backup_profile(client, force)
        msg = await client.send_message(
            m.chat.id,
            "✅ Profile backup saved" if ok else "⚠️ Backup exists (use force)"
        )
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)

@Client.on_message(owner_only & filters.command("restoreprofile", "."))
async def restore_cmd(client, m):
    try:
        await m.delete()
        ok = await restore_profile(client)
        msg = await client.send_message(
            m.chat.id,
            "♻️ Profile restored (Name + Bio + DP)" if ok else "❌ No backup found"
        )
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)

# =====================
# BACKUP INFO
# =====================
@Client.on_message(owner_only & filters.command("backupinfo", "."))
async def backupinfo_cmd(client, m):
    try:
        await m.delete()
        data = profile_col.find_one({"_id": "backup"})
        if not data:
            msg = await client.send_message(m.chat.id, "❌ No profile backup found")
        else:
            msg = await client.send_message(
                m.chat.id,
                f"📦 PROFILE BACKUP INFO\n\n"
                f"Name: {data.get('first_name','')}\n"
                f"Bio: {'Yes' if data.get('bio') else 'No'}\n"
                f"DP: {'Yes' if data.get('dp_msg_id') else 'No'}\n"
                f"Time: {data.get('backup_time')}"
            )
        await auto_delete(msg, 6)
    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)
