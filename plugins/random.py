# plugins/random.py

import random
from telethon import events
from telethon.tl.types import MessageEntityMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "random.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ random.py loaded")

# =====================
# HELP REGISTER
# =====================
register_help(
    "random",
    ".predict | .8ball | .quote | .joke\n"
    ".truth | .dare\n"
    ".insult USER\n"
    ".compliment USER\n"
    ".roast USER\n"
    ".rate USER\n"
    ".iq USER\n"
    ".simp USER\n"
    ".ship USER1 USER2\n\n"
    "• Reply / @mention / text based\n"
    "• Proper name mention\n"
    "• Auto delete enabled\n"
    "• Owner only"
)

# =====================
# DATA
# =====================
DATA = {
    "predict": [
        "Yes 👍", "No ❌", "Maybe 🤔", "Definitely 🔥",
        "Never 💀", "Future looks bright ✨", "Risk hai boss 😏"
    ],
    "8ball": [
        "Ask again later 🎱", "Sure thing 😎",
        "Impossible ❌", "100% confirmed ✅", "Highly doubtful 🤨"
    ],
    "quote": [
        "Stay hungry. Stay foolish.",
        "Code > Sleep.",
        "Discipline > Motivation.",
        "Silence is also an answer."
    ],
    "joke": [
        "Debugging is like being a detective in your own crime scene 😂",
        "Expectation: AI will take jobs. Reality: AI fixes typos 🤡"
    ],
    "truth": [
        "Last lie kya boli thi?",
        "Kisi pe secretly crush hai?"
    ],
    "dare": [
        "Next message ALL CAPS me bhejo 😈",
        "5 min tak online raho bina bole"
    ],
    "insult": [
        "{target}, small brain detected 🧠",
        "{target}, skill issue 😏",
        "{target}, Error 404: Intelligence not found"
    ],
    "compliment": [
        "{target} is a legend 🔥",
        "{target} has king energy 👑"
    ],
    "roast": [
        "{target}, tu update ke bina software jaisa hai 🤡",
        "{target}, tera confidence tera skill se zyada hai 😭"
    ],
    "simp": [
        "{target} ke liye simping level 💯",
        "{target} ke DM me already simp mode on 😌"
    ]
}

# =====================
# HELPER
# =====================
async def get_target(e, arg):
    reply_to = None
    target = None

    if e.is_reply:
        r = await e.get_reply_message()
        if r and r.sender_id:
            u = await bot.get_entity(r.sender_id)
            target = f"[{u.first_name or 'User'}](tg://user?id={u.id})"
            reply_to = r.id

    elif e.message.entities:
        for ent in e.message.entities:
            if isinstance(ent, MessageEntityMention):
                username = e.raw_text[ent.offset: ent.offset + ent.length]
                try:
                    u = await bot.get_entity(username)
                    target = f"[{u.first_name or 'User'}](tg://user?id={u.id})"
                    break
                except:
                    pass

    if not target and arg:
        target = arg

    return target, reply_to

# =====================
# MAIN HANDLER
# =====================
@bot.on(events.NewMessage(pattern=r"\.(\w+)(?:\s+(.*))?$"))
async def random_handler(e):
    if not is_owner(e):
        return

    try:
        cmd = e.pattern_match.group(1)
        arg = e.pattern_match.group(2)

        try:
            await e.delete()
        except:
            pass

        # SHIP
        if cmd == "ship" and arg:
            parts = arg.split(None, 1)
            if len(parts) == 2:
                percent = random.randint(10, 100)
                msg = await bot.send_message(
                    e.chat_id,
                    f"💖 **Ship Result** 💖\n{parts[0]} ❤️ {parts[1]}\nCompatibility: {percent}%"
                )
                return await auto_delete(msg, 8)

        # RATE
        if cmd == "rate":
            target, reply_to = await get_target(e, arg)
            rate = random.randint(1, 10)
            msg = await bot.send_message(
                e.chat_id,
                f"⭐ {target or 'You'} rating: {rate}/10",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

        # IQ
        if cmd == "iq":
            target, reply_to = await get_target(e, arg)
            iq = random.randint(50, 160)
            msg = await bot.send_message(
                e.chat_id,
                f"🧠 {target or 'You'} IQ: {iq}",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

        # OTHER RANDOM
        if cmd in DATA:
            target, reply_to = await get_target(e, arg)
            choice = random.choice(DATA[cmd])
            if "{target}" in choice:
                choice = choice.format(target=target or "You")

            msg = await bot.send_message(
                e.chat_id,
                f"🎲 {choice}",
                reply_to=reply_to
            )
            return await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
