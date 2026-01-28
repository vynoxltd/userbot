import asyncio
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error

# =====================
# PLUGIN LOAD
# =====================
print("✔ forward.py loaded")

# =====================
# FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.fwd(?: (.*))?$"))
async def fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        target = e.pattern_match.group(1)
        if not target:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.fwd CHAT_ID or @username"
            )
            await asyncio.sleep(4)
            await msg.delete()
            return

        reply = await e.get_reply_message()
        await reply.forward_to(target)

        done = await bot.send_message(e.chat_id, "✅ Forwarded")
        await asyncio.sleep(3)
        await done.delete()

    except Exception:
        await log_error(bot, "forward.py")

# =====================
# SILENT FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.sfwd(?: (.*))?$"))
async def silent_fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        target = e.pattern_match.group(1)
        if not target:
            return

        reply = await e.get_reply_message()
        await reply.forward_to(target)

    except Exception:
        await log_error(bot, "forward.py")

# =====================
# FWD HERE
# =====================
@bot.on(events.NewMessage(pattern=r"\.fwdhere$"))
async def fwd_here(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        reply = await e.get_reply_message()
        await reply.forward_to(e.chat_id)

        done = await bot.send_message(e.chat_id, "✅ Forwarded here")
        await asyncio.sleep(3)
        await done.delete()

    except Exception:
        await log_error(bot, "forward.py")

# =====================
# MULTI FWD
# =====================
@bot.on(events.NewMessage(pattern=r"\.mfwd(?: (.*))?$"))
async def multi_fwd(e):
    if not is_owner(e) or not e.is_reply:
        return

    try:
        await e.delete()

        args = (e.pattern_match.group(1) or "").split()
        if len(args) < 2 or not args[1].isdigit():
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.mfwd CHAT_ID or @username COUNT"
            )
            await asyncio.sleep(4)
            await msg.delete()
            return

        target = args[0]
        count = int(args[1])

        reply = await e.get_reply_message()
        start_id = reply.id

        success = 0

        for msg_id in range(start_id, start_id + count):
            try:
                await bot.forward_messages(
                    target,
                    e.chat_id,
                    msg_id
                )
                success += 1
                await asyncio.sleep(0.4)
            except Exception:
                pass

        done = await bot.send_message(
            e.chat_id,
            f"✅ Forwarded {success} messages"
        )
        await asyncio.sleep(3)
        await done.delete()

    except Exception:
        await log_error(bot, "forward.py")