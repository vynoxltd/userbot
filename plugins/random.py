# plugins/random.py

import random
import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention, MessageEntityTextMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

PLUGIN_NAME = "random.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ random.py loaded")

# =====================
# AUTO HELP REGISTER
# =====================
register_help(
    "random",
    ".predict\n"
    ".8ball\n"
    ".quote\n"
    ".joke\n"
    ".truth\n"
    ".dare\n"
    ".insult USER / TEXT (reply / mention)\n"
    ".compliment USER / TEXT (reply / mention)\n\n"
    "• Reply / mention / text based\n"
    "• Auto delete enabled\n"
    "• Owner only"
)

# ======================
# RANDOM DATA
# ======================
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
        "No risk, no story.",
        "Discipline > Motivation.",
        "Silence is also an answer."
    ],
    "joke": [
        "Why do programmers hate nature? Too many bugs 🐛",
        "Debugging is like being a detective in your own crime scene 😂",
        "Expectation: AI will take jobs. Reality: AI fixes typos 🤡",
        "फोन 1% पर हो और charger दूर हो — असली डर 😭"
    ],
    "truth": [
        "Last lie kya boli thi?",
        "Kisi pe secretly crush hai?",
        "Apna biggest regret batao",
        "Sabse embarrassing moment?",
        "Kabhi kisi ka message ignore kiya hai?"
    ],
    "dare": [
        "Apna last screenshot describe karo 😈",
        "Next message ALL CAPS me bhejo",
        "Kisi ko random emoji bhejo 😂",
        "5 min tak online raho bina bole",
        "Apni bio change kar ke dikhao"
    ],
    "insult": [
        "{target}, small brain detected 🧠",
        "{target}, skill issue 😏",
        "{target}, Error 404: Intelligence not found",
        "{target}, इतना confidence गलत जवाब में भी 😭",
        "{target}, beta practice kar le 😌"
    ],
    "compliment": [
        "{target} is a legend 🔥",
        "{target} has king energy 👑",
        "{target} big brain moment 🧠",
        "Respect for {target} 💯",
        "{target} born to win 🏆"
    ],
}

# ======================
# HANDLER
# ======================
@bot.on(events.NewMessage(
    pattern=r"\.(predict|8ball|quote|joke|truth|dare|insult|compliment)(?:\s+(.*))?$"
))
async def random_handler(e):
    if not is_owner(e):
        return

    try:
        cmd = e.pattern_match.group(1)
        arg = e.pattern_match.group(2)

        reply_to = None
        target = None

        # delete command
        try:
            await e.delete()
        except:
            pass

        # =====================
        # REPLY BASED
        # =====================
        if e.is_reply:
            r = await e.get_reply_message()
            if r and r.sender_id:
                reply_to = r.id
                target = f"[User](tg://user?id={r.sender_id})"

        # =====================
        # MENTION BASED
        # =====================
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
                    except:
                        pass

        # =====================
        # TEXT BASED
        # =====================
        if not target and arg:
            target = arg

        choice = random.choice(DATA[cmd])

        # format insult / compliment
        if "{target}" in choice:
            choice = choice.format(target=target or "You")

        text = f"🎲 {choice}" if cmd in ["predict", "8ball", "quote", "joke", "truth", "dare"] \
            else f"🎲 {choice}"

        msg = await bot.send_message(
            e.chat_id,
            text,
            reply_to=reply_to
        )

        await asyncio.sleep(10)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
