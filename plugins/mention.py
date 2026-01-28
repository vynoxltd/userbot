import asyncio
from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error

print("✔ mention.py loaded")

MAX_MENTIONS_ADMIN = 25
MAX_MENTIONS_USER = 10

# =====================
# HELPER: CHECK ADMIN
# =====================
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        p = await bot(GetParticipantRequest(chat_id, user_id))
        return isinstance(
            p.participant,
            (ChannelParticipantAdmin, ChannelParticipantCreator)
        )
    except Exception:
        return False

# =====================
# MENTION COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.mention(?: (.*))?$"))
async def mention_cmd(e):
    if not is_owner(e):
        return

    try:
        text = e.pattern_match.group(1)
        if not text:
            return

        chat_id = e.chat_id
        user_id = e.sender_id

        # delete command safely
        try:
            await e.delete()
        except Exception:
            pass

        admin = await is_admin(chat_id, user_id)
        limit = MAX_MENTIONS_ADMIN if admin else MAX_MENTIONS_USER

        users = []
        seen = set()

        async for msg in bot.iter_messages(chat_id, limit=300):
            uid = msg.sender_id
            if not uid or uid in seen:
                continue

            seen.add(uid)

            # markdown mention (NO < >)
            users.append(f"[User](tg://user?id={uid})")

            if len(users) >= limit:
                break

        if not users:
            return

        mention_text = f"{text}\n\n" + " ".join(users)

        await bot.send_message(
            chat_id,
            mention_text,
            link_preview=False
        )

    except Exception:
        await log_error(bot, "mention.py")