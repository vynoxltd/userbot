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
from datetime import datetime
import asyncio
import time

PLUGIN_NAME = "profilecopy.py"

# =====================
# HEALTH INIT
# =====================
try:
    mongo.admin.command("ping")
    mark_plugin_loaded(PLUGIN_NAME)
except Exception as e:
    mark_plugin_error(PLUGIN_NAME, e)

# =====================
# HELP (Help4 compatible)
# =====================
register_help(
    "profilecopy",
    """
.backupprofile
.backupprofile force
.backupprofile cloud

.restoreprofile
.restoreprofile cloud

.delbackupprofile
.delbackupprofile cloud

.backupinfo

.copybio   (reply)
.copyname  (reply)
.copydp    (reply)

.clone <seconds> (reply)
.clonestatus

.steal (reply)
"""
)

# =====================
# MONGO
# =====================
db = mongo["userbot"]
profile_col = db["profile_backup"]

# =====================
# CLONE STATE (HEALTH SAFE)
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
CLONE_TASK = None

# =====================
# BACKUP PROFILE
# =====================
async def backup_profile(client, force=False):
    if profile_col.find_one({"_id": "backup"}) and not force:
        return False

    me = await client.get_me()
    chat = await client.get_chat(me.id)

    dp_file_id = None
    async for p in client.get_chat_photos(me.id, limit=1):
        dp_file_id = p.file_id
        break

    profile_col.update_one(
        {"_id": "backup"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": chat.bio or "",
            "dp_file_id": dp_file_id,
            "backup_time": datetime.now().strftime("%d %b %Y %I:%M %p")
        }},
        upsert=True
    )
    return True

# =====================
# RESTORE PROFILE
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

    if data.get("dp_file_id"):
        await client.set_profile_photo(photo=data["dp_file_id"])

    return True

# =====================
# DELETE BACKUP
# =====================
async def delete_profile_backup():
    if not profile_col.find_one({"_id": "backup"}):
        return False
    profile_col.delete_one({"_id": "backup"})
    return True

# =====================
# COPY HELPERS
# =====================
async def copy_name(client, user):
    await client.update_profile(
        first_name=user.first_name,
        last_name=user.last_name
    )

async def copy_bio(client, user):
    chat = await client.get_chat(user.id)
    await client.update_profile(bio=chat.bio or "")

async def copy_dp(client, user):
    async for p in client.get_chat_photos(user.id, limit=1):
        await client.set_profile_photo(photo=p.file_id)
        return True
    return False

# =====================
# COPY COMMANDS
# =====================
@Client.on_message(owner_only & filters.command("copyname", ".") & filters.reply)
async def copyname_cmd(client, m):
    try:
        await m.delete()
        await copy_name(client, m.reply_to_message.from_user)
        msg = await client.send_message(m.chat.id, "✅ Name copied")
        await auto_delete(msg, 3)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

@Client.on_message(owner_only & filters.command("copybio", ".") & filters.reply)
async def copybio_cmd(client, m):
    try:
        await m.delete()
        await copy_bio(client, m.reply_to_message.from_user)
        msg = await client.send_message(m.chat.id, "✅ Bio copied")
        await auto_delete(msg, 3)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

@Client.on_message(owner_only & filters.command("copydp", ".") & filters.reply)
async def copydp_cmd(client, m):
    try:
        await m.delete()
        ok = await copy_dp(client, m.reply_to_message.from_user)
        msg = await client.send_message(
            m.chat.id,
            "✅ DP copied" if ok else "❌ User has no DP"
        )
        await auto_delete(msg, 3)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

# =====================
# STEAL
# =====================
@Client.on_message(owner_only & filters.command("steal", ".") & filters.reply)
async def steal_cmd(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        await copy_name(client, user)
        await copy_bio(client, user)
        await copy_dp(client, user)
        msg = await client.send_message(m.chat.id, "🧬 Profile stolen")
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

# =====================
# CLONE SYSTEM
# =====================
async def clone_worker(client, user, seconds):
    global CLONE_ACTIVE, CLONE_END_TIME
    CLONE_ACTIVE = True
    CLONE_END_TIME = int(time.time()) + seconds

    try:
        while time.time() < CLONE_END_TIME:
            await copy_name(client, user)
            await copy_bio(client, user)
            await copy_dp(client, user)
            await asyncio.sleep(10)
    finally:
        CLONE_ACTIVE = False

@Client.on_message(owner_only & filters.command("clone", ".") & filters.reply)
async def clone_cmd(client, m):
    global CLONE_TASK
    try:
        await m.delete()
        seconds = int(m.command[1])
        user = m.reply_to_message.from_user
        CLONE_TASK = asyncio.create_task(clone_worker(client, user, seconds))
        msg = await client.send_message(m.chat.id, f"🧬 Clone started for {seconds}s")
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

@Client.on_message(owner_only & filters.command("clonestatus", "."))
async def clonestatus_cmd(client, m):
    await m.delete()
    if CLONE_ACTIVE:
        left = CLONE_END_TIME - int(time.time())
        msg = await client.send_message(m.chat.id, f"🧬 Clone active ({left}s left)")
    else:
        msg = await client.send_message(m.chat.id, "❌ No active clone")
    await auto_delete(msg, 4)

# =====================
# BACKUP COMMANDS
# =====================
@Client.on_message(owner_only & filters.command("backupprofile", "."))
async def backup_cmd(client, m):
    try:
        await m.delete()
        ok = await backup_profile(client, "force" in m.command)
        msg = await client.send_message(
            m.chat.id,
            "☁️ Profile backup saved" if ok else "⚠️ Backup exists (use force)"
        )
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

@Client.on_message(owner_only & filters.command("restoreprofile", "."))
async def restore_cmd(client, m):
    try:
        await m.delete()
        ok = await restore_profile(client)
        msg = await client.send_message(
            m.chat.id,
            "♻️ Profile restored" if ok else "❌ No backup found"
        )
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)

@Client.on_message(owner_only & filters.command("delbackupprofile", "."))
async def delbackup_cmd(client, m):
    try:
        await m.delete()
        ok = await delete_profile_backup()
        msg = await client.send_message(
            m.chat.id,
            "🗑 Profile backup deleted" if ok else "❌ No backup found"
        )
        await auto_delete(msg, 4)
    except Exception as e:
        mark_plugin_error(PLUGIN_NAME, e)
        await log_error(client, PLUGIN_NAME, e)
