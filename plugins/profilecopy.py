from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import asyncio
import time
import os
import json

mark_plugin_loaded("profilecopy.py")

# 🔥 auto help (help4.py)
register_help(
    "profilecopy",
    """
.backupprofile
.backupprofile force
.restoreprofile

.copybio   (reply)
.copyname  (reply)
.copydp    (reply)

.clone <seconds> (reply)
.clonestatus

.steal (reply)

.silentclone on/off

• Profile backup is permanent
• Clone auto-restores after time
• Silent mode hides messages
"""
)

# =====================
# FILE STORAGE
# =====================
DATA_DIR = "data"
BACKUP_FILE = os.path.join(DATA_DIR, "profile_backup.json")
DP_FILE = os.path.join(DATA_DIR, "profile_dp.jpg")

os.makedirs(DATA_DIR, exist_ok=True)

# =====================
# GLOBAL STATE
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
SILENT_MODE = False


# =====================
# HELPERS
# =====================
async def get_user_bio(client, user_id):
    try:
        chat = await client.get_chat(user_id)
        return chat.bio or ""
    except:
        return ""


async def backup_profile(client, force=False):
    if not os.path.exists(BACKUP_FILE):
        force = True

    if os.path.exists(BACKUP_FILE) and not force:
        return False

    me = await client.get_me()
    bio = await get_user_bio(client, me.id)

    data = {
        "first_name": me.first_name,
        "last_name": me.last_name,
        "bio": bio
    }

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    try:
        photos = await client.get_profile_photos("me", limit=1)
        if photos.total_count > 0:
            file = await client.download_media(photos.photos[0].file_id)
            if file:
                os.replace(file, DP_FILE)
    except:
        pass

    return True


async def restore_profile(client):
    if not os.path.exists(BACKUP_FILE):
        return False

    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    await client.update_profile(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        bio=data.get("bio")
    )

    if os.path.exists(DP_FILE):
        try:
            await client.set_profile_photo(photo=DP_FILE)
        except:
            pass

    return True


async def set_dp_from_user(client, user):
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos.total_count == 0:
            return False

        file = await client.download_media(photos.photos[0].file_id)
        await client.set_profile_photo(photo=file)
        return True
    except:
        return False


# =====================
# BACKUP / RESTORE
# =====================
@Client.on_message(owner_only & filters.command("backupprofile", "."))
async def backup_cmd(client, m):
    try:
        await m.delete()

        force = len(m.command) > 1 and m.command[1].lower() == "force"
        ok = await backup_profile(client, force)

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "Profile backup saved permanently"
                if ok else "Backup already exists (use .backupprofile force)"
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

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "Profile restored successfully" if ok else "No backup found"
            )
            await auto_delete(msg, 4)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


# =====================
# COPY BIO / NAME / DP
# =====================
@Client.on_message(owner_only & filters.command("copybio", ".") & filters.reply)
async def copy_bio(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        bio = await get_user_bio(client, user.id)
        await client.update_profile(bio=bio)

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "Bio copied")
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


@Client.on_message(owner_only & filters.command("copyname", ".") & filters.reply)
async def copy_name(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        await client.update_profile(
            first_name=user.first_name,
            last_name=user.last_name
        )

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "Name copied")
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)


@Client.on_message(owner_only & filters.command("copydp", ".") & filters.reply)
async def copy_dp(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        ok = await set_dp_from_user(client, user)

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                "DP copied" if ok else "DP not accessible"
            )
            await auto_delete(msg, 3)

    except Exception as e:
        mark_plugin_error("profilecopy.py", e)
        await log_error(client, "profilecopy.py", e)
