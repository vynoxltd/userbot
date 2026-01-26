from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import random

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
@Client.on_message(
    owner_only & filters.command(list(ACTIONS.keys()), ".")
)
async def fun_handler(client: Client, m):
    try:
        cmd = m.command[0].lower()
        data = ACTIONS.get(cmd)
        if not data:
            return

        # delete command safely
        try:
            await m.delete()
        except:
            pass

        actor = m.from_user.mention
        target = actor
        reply_to = None

        # 🔁 reply based
        if m.reply_to_message and m.reply_to_message.from_user:
            target_user = m.reply_to_message.from_user
            target = target_user.mention
            reply_to = m.reply_to_message.id

        # 🔖 mention based
        elif m.entities:
            for ent in m.entities:
                if ent.type in ("mention", "text_mention"):
                    if ent.type == "text_mention":
                        target = ent.user.mention
                    else:
                        username = m.text[ent.offset: ent.offset + ent.length]
                        user = await client.get_users(username)
                        target = user.mention
                    break

        # 🎲 pick text
        text = random.choice(data["texts"]).format(
            actor=actor,
            target=target
        )

        # 🎬 gif or text randomly
        if data["gifs"] and random.choice([True, False]):
            sent = await client.send_animation(
                m.chat.id,
                random.choice(data["gifs"]),
                caption=text,
                reply_to_message_id=reply_to
            )
        else:
            sent = await client.send_message(
                m.chat.id,
                text,
                reply_to_message_id=reply_to
            )

        await auto_delete(sent, 6)

    except Exception as e:
        await log_error(client, "fun.py", e)