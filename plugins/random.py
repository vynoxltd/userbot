from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    log_error,
    mark_plugin_loaded,
    mark_plugin_error,
    register_help
)
import random

mark_plugin_loaded("random.py")

# 🔥 auto help for help4.py
register_help(
    "random",
    """
.predict
.8ball
.quote
.joke
.truth
.dare
.insult <user/text>
.compliment <user/text>

• Reply / mention / text based
• Random responses
"""
)

# ======================
# RANDOM DATA (FULL)
# ======================
DATA = {
    "predict": [
        "Yes 👍",
        "No ❌",
        "Maybe 🤔",
        "Definitely 🔥",
        "Never 💀",
        "Future looks bright ✨",
        "Risk hai boss 😏"
    ],

    "8ball": [
        "Ask again later 🎱",
        "Sure thing 😎",
        "Impossible ❌",
        "100% confirmed ✅",
        "Highly doubtful 🤨"
    ],

    "quote": [
        "Stay hungry. Stay foolish.",
        "Code > Sleep.",
        "No risk, no story.",
        "Discipline > Motivation.",
        "Silence is also an answer."
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

    "joke": [
        "Why do programmers hate nature? Too many bugs 🐛",
        "Debugging is like being a detective in your own crime scene 😂",
        "मैं इतना lazy हूँ कि आलस भी मुझसे डरता है 😴",
        "Expectation: AI will take jobs. Reality: AI fixes typos 🤡",
        "फोन 1% पर हो और charger दूर हो — असली डर 😭"
    ]
}

# ======================
# HANDLER (MENTION + REPLY)
# ======================
@Client.on_message(owner_only & filters.command(list(DATA.keys()), "."))
async def random_fun(client, m):
    try:
        # 🧹 safe delete command
        try:
            await m.delete()
        except:
            pass

        if not m.command:
            return

        cmd = m.command[0].lower()
        if cmd not in DATA:
            return

        # 🎯 TARGET DETECTION
        target = None

        # reply based
        if m.reply_to_message and m.reply_to_message.from_user:
            target = m.reply_to_message.from_user.mention

        # mention / text based
        elif len(m.command) > 1:
            target = " ".join(m.command[1:])

        # 🎲 random pick
        choice = random.choice(DATA[cmd])

        # 🧾 final output
        if target:
            text = f"🎲 {target} → {choice}"
        else:
            text = f"🎲 {choice}"

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 6)

    except Exception as e:
        # 🔥 auto-heal + health update
        mark_plugin_error("random.py", e)
        await log_error(client, "random.py", e)
