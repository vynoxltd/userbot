import random
import asyncio
from telethon import events
from telethon.tl.types import MessageEntityMention

from userbot import bot
from utils.owner import is_owner
from utils.logger import log_error
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("random.py")
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
    ".insult USER / TEXT\n"
    ".compliment USER / TEXT\n\n"
    "• Reply / mention / text based\n"
    "• Random responses"
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
        "Small brain detected 🧠",
        "Skill issue 😏",
        "Error 404: Intelligence not found",
        "इतना confidence गलत जवाब में भी 😭",
        "Beta practice kar le 😌"
    ],
    "compliment": [
        "Legend 🔥",
        "King energy 👑",
        "Big brain moment 🧠",
        "Respect 💯",
        "Born to win 🏆"
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

        try:
            await e.delete()
        except:
            pass

        target = None

        # reply based
        if e.is_reply:
            r = await e.get_reply_message()
            if r and r.sender_id:
                target = f"[User](tg://user?id={r.sender_id})"

        # mention based (@username)
        elif e.message.entities:
            for ent in e.message.entities:
                if isinstance(ent, MessageEntityMention):
                    username = e.raw_text[ent.offset: ent.offset + ent.length]
                    try:
                        user = await bot.get_entity(username)
                        target = f"[User](tg://user?id={user.id})"
                        break
                    except:
                        pass

        # plain text target
        if not target and arg:
            target = arg

        choice = random.choice(DATA[cmd])

        text = f"🎲 {target} → {choice}" if target else f"🎲 {choice}"

        msg = await bot.send_message(e.chat_id, text)
        await asyncio.sleep(6)
        await msg.delete()

    except Exception as ex:
        mark_plugin_error("random.py", ex)
        await log_error(bot, "random.py", ex)
