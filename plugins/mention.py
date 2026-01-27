from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from plugins.owner import owner_only
from plugins.utils import (
    log_error,
    mark_plugin_loaded,
    mark_plugin_error
)

mark_plugin_loaded("mention.py")

MAX_MENTIONS_ADMIN = 25
MAX_MENTIONS_USER = 10


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


@Client.on_message(owner_only & filters.command("mention", "."))
async def mention_cmd(client: Client, m):
    try:
        if len(m.command) < 2:
            return

        chat_id = m.chat.id
        user_id = m.from_user.id
        text = m.text.split(None, 1)[1]

        # delete command safely
        try:
            await m.delete()
        except:
            pass

        admin = await is_admin(client, chat_id, user_id)
        limit = MAX_MENTIONS_ADMIN if admin else MAX_MENTIONS_USER

        users = []
        seen = set()

        async for msg in client.get_chat_history(chat_id, limit=300):
            u = msg.from_user
            if not u or u.is_bot or u.id in seen:
                continue

            seen.add(u.id)

            if u.username:
                users.append(f"@{u.username}")
            else:
                users.append(
                    f'<a href="tg://user?id={u.id}">{u.first_name}</a>'
                )

            if len(users) >= limit:
                break

        if not users:
            return

        mention_text = f"{text}\n\n" + " ".join(users)

        await client.send_message(
            chat_id,
            mention_text,
            parse_mode=ParseMode.HTML,   # ✅ ONLY CORRECT WAY
            disable_web_page_preview=True
        )

    except Exception as e:
        # 🔥 update health + log
        mark_plugin_error("mention.py", e)
        await log_error(client, "mention.py", e)
