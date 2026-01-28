import random
import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityTextMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error

# ======================
# PLUGIN LOAD
# ======================
print("✔ fun.py loaded")

# ======================
# ACTION DATA
# ======================
ACTIONS = {
    "slap": {
        "gifs": [
            "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"
        ],
        "texts": [
            "👋 {actor} ne {target} ko zor se thappad mara 😈",
            "💢 {target} ko {actor} se slap pad gaya 😂",
            "🤚 Oops! {actor} ne {target} ko slap kar diya"
        ]
    },
    "hug": {
        "gifs": [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif"
        ],
        "texts": [
            "🤗 {actor} ne {target} ko tight hug diya 💕",
            "🫂 {target} ko {actor} ka hug mila",
            "❤️ {actor} hugged {target}"
        ]
    },
    "kiss": {
        "gifs": [
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif"
        ],
        "texts": [
            "😘 {actor} ne {target} ko kiss diya",
            "💋 {target} got kissed by {actor}",
            "😳 {actor} kissed {target}"
        ]
    },
    "poke": {
        "gifs": [
            "https://media.giphy.com/media/3o6Zt8MgUuvSbkZYWc/giphy.gif",
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
        ],
        "texts": [
            "👉 {actor} ne {target} ko poke kiya 😆",
            "👀 {actor} is poking {target}",
            "😂 {target} ko {actor} ne ched diya"
        ]
    },
    "tickle": {
        "gifs": [
            "https://media.giphy.com/media/11sBLVxNs7v6WA/giphy.gif",
            "https://media.giphy.com/media/l0Exk8EUzSLsrErEQ/giphy.gif"
        ],
        "texts": [
            "🤣 {actor} ne {target} ko gudgudi kar di",
            "😂 {target} control nahi kar pa raha",
            "😹 {actor} ka tickle attack on {target}"
        ]
    }
}

# ======================
# FUN HANDLER
# ======================
@bot.on(events.NewMessage(pattern=r"\.(slap|hug|kiss|poke|tickle)$"))
async def fun_handler(e):
    if not is_owner(e):
        return

    try:
        cmd = e.pattern_match.group(1)
        data = ACTIONS.get(cmd)
        if not data:
            return

        try:
            await e.delete()
        except Exception:
            pass

        actor = f"[You](tg://user?id={e.sender_id})"
        target = actor
        reply_to = None

        # reply based target
        if e.is_reply:
            r = await e.get_reply_message()
            if r and r.sender_id:
                target = f"[User](tg://user?id={r.sender_id})"
                reply_to = r.id

        # mention based target
        elif e.message.entities:
            for ent in e.message.entities:
                if isinstance(ent, MessageEntityTextMention):
                    target = f"[User](tg://user?id={ent.user_id})"
                    break
                if isinstance(ent, MessageEntityMention):
                    username = e.raw_text[ent.offset: ent.offset + ent.length]
                    try:
                        user = await bot.get_entity(username)
                        target = f"[User](tg://user?id={user.id})"
                        break
                    except Exception:
                        pass

        text = random.choice(data["texts"]).format(
            actor=actor,
            target=target
        )

        if data["gifs"] and random.choice([True, False]):
            sent = await bot.send_file(
                e.chat_id,
                random.choice(data["gifs"]),
                caption=text,
                reply_to=reply_to
            )
        else:
            sent = await bot.send_message(
                e.chat_id,
                text,
                reply_to=reply_to
            )

        await asyncio.sleep(6)
        await sent.delete()

    except Exception:
        await log_error(bot, "fun.py")