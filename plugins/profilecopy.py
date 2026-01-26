from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import asyncio
import time
import os
import json
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("profilecopy.py")

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
    # 🔥 IMPORTANT FIX: first time backup kabhi skip nahi hoga
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

    # 🔥 DP BACKUP
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
        await log_error(client, "profilecopy.py", e)


# =====================
# FULL CLONE (TEMP)
# =====================
@Client.on_message(owner_only & filters.command("clone", ".") & filters.reply)
async def clone_temp(client, m):
    global CLONE_ACTIVE, CLONE_END_TIME

    try:
        await m.delete()

        if len(m.command) < 2 or not m.command[1].isdigit():
            msg = await client.send_message(m.chat.id, "Usage: .clone <seconds>")
            await auto_delete(msg, 4)
            return

        seconds = int(m.command[1])
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        bio = await get_user_bio(client, user.id)

        await client.update_profile(
            first_name=user.first_name,
            last_name=user.last_name,
            bio=bio
        )

        await set_dp_from_user(client, user)

        CLONE_ACTIVE = True
        CLONE_END_TIME = time.time() + seconds

        if not SILENT_MODE:
            msg = await client.send_message(
                m.chat.id,
                f"Cloned for {seconds} seconds"
            )
            await auto_delete(msg, 3)

        await asyncio.sleep(seconds)
        await restore_profile(client)
        CLONE_ACTIVE = False

    except Exception as e:
        await log_error(client, "profilecopy.py", e)


# =====================
# STEAL (FUN)
# =====================
@Client.on_message(owner_only & filters.command("steal", ".") & filters.reply)
async def steal_fun(client, m):
    try:
        await m.delete()
        user = m.reply_to_message.from_user
        if not user:
            return

        await backup_profile(client)
        await set_dp_from_user(client, user)

        await client.update_profile(
            first_name=user.first_name,
            last_name=user.last_name,
            bio=f"Owned by {m.from_user.first_name} 😈"
        )

        if not SILENT_MODE:
            msg = await client.send_message(m.chat.id, "Profile stolen 😈")
            await auto_delete(msg, 3)

    except Exception as e:
        await log_error(client, "profilecopy.py", e)


# =====================
# CLONE STATUS
# =====================
@Client.on_message(owner_only & filters.command("clonestatus", "."))
async def clone_status(client, m):
    try:
        await m.delete()

        if not CLONE_ACTIVE:
            msg = await client.send_message(m.chat.id, "No active clone")
        else:
            remaining = int(CLONE_END_TIME - time.time())
            msg = await client.send_message(
                m.chat.id,
                f"Clone active, remaining {remaining}s"
            )

        await auto_delete(msg, 3)

    except Exception as e:
        await log_error(client, "profilecopy.py", e)


# =====================
# SILENT MODE
# =====================
@Client.on_message(owner_only & filters.command("silentclone", "."))
async def silent_clone(client, m):
    global SILENT_MODE

    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                f"Silent mode is {'ON' if SILENT_MODE else 'OFF'}"
            )
            await auto_delete(msg, 3)
            return

        if m.command[1].lower() == "on":
            SILENT_MODE = True
        elif m.command[1].lower() == "off":
            SILENT_MODE = False

        msg = await client.send_message(
            m.chat.id,
            f"Silent mode {'ON' if SILENT_MODE else 'OFF'}"
        )
        await auto_delete(msg, 3)

    except Exception as e:
        await log_error(client, "profilecopy.py", e)