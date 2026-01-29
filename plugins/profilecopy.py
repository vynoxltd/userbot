import os
import time
import asyncio
from datetime import datetime
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.mongo import mongo, db
PLUGIN_NAME = "profilecopy.py"
print(f"✔ {PLUGIN_NAME} loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "profilecopy",
    "PROFILE COPY & CLONE\n\n"
    "Backup (MongoDB)\n"
    ".backupprofile\n"
    ".backupprofile force\n"
    ".restoreprofile\n"
    ".delbackupprofile\n"
    ".backupinfo\n\n"
    "Copy (reply required)\n"
    ".copyname\n"
    ".copybio\n"
    ".copydp\n"
    ".steal\n\n"
    "Clone\n"
    ".clone SECONDS (reply)\n"
    ".clonestatus\n\n"
    "Silent Clone\n"
    ".silentclone on\n"
    ".silentclone off"
)

# =====================
# MONGO
# =====================
db = mongo["userbot"]
profile_col = db["profile_backup"]

# =====================
# CLONE STATE
# =====================
CLONE_ACTIVE = False
CLONE_END_TIME = 0
CLONE_TASK = None
SILENT_CLONE = False

# =====================
# BACKUP PROFILE
# =====================
async def backup_profile(force=False):
    if profile_col.find_one({"_id": "backup"}) and not force:
        return False

    me = await bot.get_me()
    bio = (await bot.get_entity(me.id)).about or ""

    dp_file = None
    async for photo in bot.iter_profile_photos(me.id, limit=1):
        dp_file = photo
        break

    profile_col.update_one(
        {"_id": "backup"},
        {"$set": {
            "first_name": me.first_name,
            "last_name": me.last_name,
            "bio": bio,
            "dp": dp_file.id if dp_file else None,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }},
        upsert=True
    )
    return True

# =====================
# RESTORE PROFILE
# =====================
async def restore_profile():
    data = profile_col.find_one({"_id": "backup"})
    if not data:
        return False

    await bot(functions.account.UpdateProfileRequest(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        about=data.get("bio")
    ))

    if data.get("dp"):
        file = await bot.download_media(data["dp"])
        await bot.upload_profile_photo(file)
        os.remove(file)

    return True

# =====================
# COPY HELPERS
# =====================
async def copy_name(user):
    await bot(functions.account.UpdateProfileRequest(
        first_name=user.first_name,
        last_name=user.last_name
    ))

async def copy_bio(user):
    bio = (await bot.get_entity(user.id)).about or ""
    await bot(functions.account.UpdateProfileRequest(about=bio))

async def copy_dp(user):
    async for p in bot.iter_profile_photos(user.id, limit=1):
        file = await bot.download_media(p)
        await bot.upload_profile_photo(file)
        os.remove(file)
        return True
    return False

# =====================
# COPY COMMANDS
# =====================
@bot.on(events.NewMessage(pattern=r"\.(copyname|copybio|copydp|steal)$"))
async def copy_cmd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()
        user = (await e.get_reply_message()).sender

        if e.raw_text.startswith(".copyname"):
            await copy_name(user)
            msg = "✅ Name copied"

        elif e.raw_text.startswith(".copybio"):
            await copy_bio(user)
            msg = "✅ Bio copied"

        elif e.raw_text.startswith(".copydp"):
            ok = await copy_dp(user)
            msg = "✅ DP copied" if ok else "❌ No DP"

        else:  # steal
            await copy_name(user)
            await copy_bio(user)
            await copy_dp(user)
            msg = "🧬 Profile stolen"

        if not SILENT_CLONE:
            m = await bot.send_message(e.chat_id, msg)
            await asyncio.sleep(4)
            await m.delete()

    except Exception:
        await log_error(bot, PLUGIN_NAME)

# =====================
# CLONE SYSTEM
# =====================
async def clone_worker(user, seconds):
    global CLONE_ACTIVE, CLONE_END_TIME
    CLONE_ACTIVE = True
    CLONE_END_TIME = int(time.time()) + seconds

    try:
        while time.time() < CLONE_END_TIME:
            await copy_name(user)
            await copy_bio(user)
            await copy_dp(user)
            await asyncio.sleep(10)
    finally:
        CLONE_ACTIVE = False

@bot.on(events.NewMessage(pattern=r"\.clone (\d+)"))
async def clone_cmd(e):
    global CLONE_TASK
    if not is_owner(e) or not e.is_reply:
        return

    await e.delete()
    seconds = int(e.pattern_match.group(1))
    user = (await e.get_reply_message()).sender

    CLONE_TASK = asyncio.create_task(clone_worker(user, seconds))

    if not SILENT_CLONE:
        m = await bot.send_message(e.chat_id, f"🧬 Clone started for {seconds}s")
        await asyncio.sleep(4)
        await m.delete()

@bot.on(events.NewMessage(pattern=r"\.clonestatus$"))
async def clone_status(e):
    if not is_owner(e):
        return

    await e.delete()
    if CLONE_ACTIVE:
        left = CLONE_END_TIME - int(time.time())
        msg = f"🧬 Clone active ({left}s left)"
    else:
        msg = "❌ No active clone"

    m = await bot.send_message(e.chat_id, msg)
    await asyncio.sleep(4)
    await m.delete()

# =====================
# SILENT CLONE
# =====================
@bot.on(events.NewMessage(pattern=r"\.silentclone (on|off)$"))
async def silent_clone(e):
    global SILENT_CLONE
    if not is_owner(e):
        return

    await e.delete()
    SILENT_CLONE = e.pattern_match.group(1) == "on"

    m = await bot.send_message(
        e.chat_id,
        "🤫 Silent clone enabled" if SILENT_CLONE else "🔊 Silent clone disabled"
    )
    await asyncio.sleep(4)
    await m.delete()
