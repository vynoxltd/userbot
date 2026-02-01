import asyncio
import random
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "fun_games.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ fun_games.py loaded (GAMES MODE)")

# =====================
# HELP
# =====================
register_help(
    "fungames",
    ".tictactoe (reply)\n"
    ".battle @user\n"
    ".emojiwar\n"
    ".casino\n"
    ".virus\n\n"
    "• Reply based games\n"
    "• Fake animations\n"
    "• Auto delete commands 😄"
)

# =====================
# COMMON ANIMATION HELPER
# =====================
async def reply_animate(e, frames, delay=0.7):
    if e.is_reply:
        r = await e.get_reply_message()
        m = await r.reply(frames[0])
    else:
        m = await e.reply(frames[0])

    await e.delete()

    for f in frames[1:]:
        await asyncio.sleep(delay)
        await m.edit(f)

# =====================
# TIC TAC TOE (REPLY VS USER)
# =====================
@bot.on(events.NewMessage(pattern=r"\.tictactoe$"))
async def tictactoe(e):
    try:
        frames = [
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n⬜ ⭕ ❌",
            "❌ ⭕ ❌\n⭕ ❌ ⭕\n❌ ⭕ ❌",
            "🏁 **GAME OVER**\nYou Wins 😎"
        ]
        await reply_animate(e, frames, 0.9)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BATTLE GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.battle(?: (.*))?$"))
async def battle(e):
    try:
        target = e.pattern_match.group(1) or "Enemy"
        frames = [
            f"⚔️ Battle started vs {target}",
            "⚔️ Attacking...",
            "🛡 Enemy defending...",
            "💥 Critical hit!",
            "🏆 **YOU WON THE BATTLE**"
        ]
        await reply_animate(e, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# EMOJI WAR
# =====================
@bot.on(events.NewMessage(pattern=r"\.emojiwar$"))
async def emojiwar(e):
    try:
        frames = [
            "😀 😃 😄",
            "😡 😠 🤬",
            "💥 💣 💥",
            "😂 🤣 😂",
            "🏁 **EMOJI WAR OVER**"
        ]
        await reply_animate(e, frames, 0.6)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# CASINO GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.casino$"))
async def casino(e):
    try:
        slots = ["🍒", "🍋", "🍉", "⭐", "💎"]
        result = [random.choice(slots) for _ in range(3)]

        frames = [
            "🎰 Spinning...",
            f"🎰 {' '.join(result)}",
            "🎉 **JACKPOT!**" if len(set(result)) == 1 else "😢 You lost"
        ]
        await reply_animate(e, frames, 1.0)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# FAKE VIRUS PRANK
# =====================
@bot.on(events.NewMessage(pattern=r"\.virus$"))
async def fake_virus(e):
    try:
        frames = [
            "🦠 Virus detected...",
            "🦠 Infecting system...",
            "📂 Deleting files...",
            "⚠️ System unstable...",
            "💥 System crashed...",
            "😈 Just kidding!\n❌ No virus detected"
        ]
        await reply_animate(e, frames, 0.8)
    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)

# =====================
# ADVANCED SNAKE GAME
# =====================
import json
import os
from datetime import date

SNAKE_DB = "utils/snake_leaderboard.json"

def load_snake_db():
    if not os.path.exists(SNAKE_DB):
        return {"date": "", "wins": {}}
    with open(SNAKE_DB, "r") as f:
        return json.load(f)

def save_snake_db(db):
    with open(SNAKE_DB, "w") as f:
        json.dump(db, f, indent=2)

def today():
    return str(date.today())

def hp_bar(hp):
    blocks = max(0, min(10, int(hp / 10)))
    return "█" * blocks + "░" * (10 - blocks)

@bot.on(events.NewMessage(pattern=r"\.snake$"))
async def snake_game(e):
    try:
        await e.delete()
        db = load_snake_db()

        # reset daily stats
        if db["date"] != today():
            db["date"] = today()
            db["wins"] = {}

        # detect players
        players = []

        if e.is_reply:
            r = await e.get_reply_message()
            u = await r.get_sender()
            players.append((str(u.id), u.first_name or "User"))

        if not players:
            players = [("snakeB", "Snake B")]

        m = await e.reply("🐍 **SNAKE BATTLE INITIALIZING...**")

        wins_a = 0
        wins_b = 0

        # ===== BEST OF 3 =====
        for round_no in range(1, 4):
            hp_a = 100
            hp_b = 100
            poison_b = 0

            await m.edit(
                f"🎮 **ROUND {round_no}**\n\n"
                f"🐍 Snake A: `{hp_bar(hp_a)}` {hp_a}%\n"
                f"🐍 {players[0][1]}: `{hp_bar(hp_b)}` {hp_b}%"
            )
            await asyncio.sleep(1)

            while hp_a > 0 and hp_b > 0:
                attacker = random.choice(["A", "B"])

                # abilities
                crit = random.random() < 0.25
                poison = random.random() < 0.2
                regen = random.random() < 0.15

                dmg = random.randint(10, 20)
                if crit:
                    dmg *= 2

                if attacker == "A":
                    hp_b -= dmg
                    if poison:
                        poison_b = 2
                    text = f"🐍 Snake A attacks `{players[0][1]}`"
                else:
                    hp_a -= dmg
                    text = f"🐍 {players[0][1]} attacks Snake A"

                # poison tick
                if poison_b > 0:
                    hp_b -= 5
                    poison_b -= 1
                    text += " ☠️ POISON"

                # regen
                if regen:
                    hp_a = min(100, hp_a + 5)
                    text += " 💚 REGEN"

                hp_a = max(0, hp_a)
                hp_b = max(0, hp_b)

                await m.edit(
                    f"{text}{' 💥 CRIT' if crit else ''}\n\n"
                    f"🐍 Snake A: `{hp_bar(hp_a)}` {hp_a}%\n"
                    f"🐍 {players[0][1]}: `{hp_bar(hp_b)}` {hp_b}%"
                )
                await asyncio.sleep(0.9)

            if hp_a > hp_b:
                wins_a += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** Snake A")
            else:
                wins_b += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {players[0][1]}")

            await asyncio.sleep(1)

        # ===== FINAL =====
        if wins_b > wins_a:
            key = players[0][0]
            db["wins"][key] = db["wins"].get(key, 0) + 1
            save_snake_db(db)
            winner = players[0][1]
        else:
            winner = "Snake A"

        await m.edit(
            f"🏁 **MATCH OVER**\n\n"
            f"Snake A Wins: `{wins_a}`\n"
            f"{players[0][1]} Wins: `{wins_b}`\n\n"
            f"🥇 **FINAL WINNER:** `{winner}`\n\n"
            f"📅 Daily Wins Tracked ✔"
        )

        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
