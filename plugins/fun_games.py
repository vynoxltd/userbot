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
    ".snake\n"
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

LEADERBOARD_DB = "utils/leaderboard.json"

def load_snake_db():
    if not os.path.exists(LEADERBOARD_DB):
        return {
            "date": "",
            "players": {}
        }
    with open(LEADERBOARD_DB, "r") as f:
        data = json.load(f)
        data.setdefault("players", {})
        return data

def save_snake_db(db):
    with open(LEADERBOARD_DB, "w") as f:
        json.dump(db, f, indent=2)

def today():
    return str(date.today())

def hp_bar(hp):
    blocks = max(0, min(10, hp // 10))
    return "█" * blocks + "░" * (10 - blocks)

@bot.on(events.NewMessage(pattern=r"\.snake$"))
async def snake_game(e):
    try:
        await e.delete()
        db = load_snake_db()

        # ===== DAILY RESET =====
        if db["date"] != today():
            db["date"] = today()
            db["players"] = {}

        # ===== OPPONENT DETECT =====
        if e.is_reply:
            r = await e.get_reply_message()
            u = await r.get_sender()
            opp_id = str(u.id)
            opp_name = u.first_name or "User"
        else:
            opp_id = "anaconda"
            opp_name = "Anaconda 🐍"

        # ===== INIT ANIMATION =====
        m = await e.reply("🐍 **SNAKE BATTLE INITIALIZING...**")
        init_frames = [
            "🐍 Loading venom modules...",
            "🐍 Preparing arena...",
            "🐍 Calculating abilities...",
            "🐍 **BATTLE STARTING** ⚔️"
        ]

        for f in init_frames:
            await m.edit(f)
            await asyncio.sleep(0.6)

        wins_cobra = 0
        wins_opp = 0

        # ===== BEST OF 3 =====
        for round_no in range(1, 4):
            hp_cobra, hp_opp = 100, 100
            poison_opp = 0

            await m.edit(
                f"🎮 **ROUND {round_no}**\n\n"
                f"🐍 **King Cobra 🐍**\n"
                f"`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                f"🐍 **{opp_name}**\n"
                f"`[{hp_bar(hp_opp)}]` {hp_opp}%"
            )
            await asyncio.sleep(1)

            while hp_cobra > 0 and hp_opp > 0:
                attacker = random.choice(["cobra", "opp"])

                crit = random.random() < 0.25
                poison = random.random() < 0.20
                regen = random.random() < 0.15

                dmg = random.randint(10, 20)
                if crit:
                    dmg *= 2

                if attacker == "cobra":
                    hp_opp -= dmg
                    if poison:
                        poison_opp = 2
                    text = f"🐍 King Cobra attacks `{opp_name}`"
                else:
                    hp_cobra -= dmg
                    text = f"🐍 {opp_name} attacks King Cobra"

                if poison_opp > 0:
                    hp_opp -= 5
                    poison_opp -= 1
                    text += " ☠️ POISON"

                if regen:
                    hp_cobra = min(100, hp_cobra + 5)
                    text += " 💚 REGEN"

                hp_cobra = max(0, hp_cobra)
                hp_opp = max(0, hp_opp)

                await m.edit(
                    f"{text}{' 💥 CRIT' if crit else ''}\n\n"
                    f"🐍 **King Cobra 🐍**\n"
                    f"`[{hp_bar(hp_cobra)}]` {hp_cobra}%\n\n"
                    f"🐍 **{opp_name}**\n"
                    f"`[{hp_bar(hp_opp)}]` {hp_opp}%"
                )
                await asyncio.sleep(1.2)

            if hp_cobra > hp_opp:
                wins_cobra += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** King Cobra 🐍")
            else:
                wins_opp += 1
                await m.edit(f"🏆 **ROUND {round_no} WINNER:** {opp_name}")

            await asyncio.sleep(1.5)

        # ===== SAVE STATS =====
        def ensure_player(pid, name):
            db["players"].setdefault(pid, {
                "name": name,
                "wins": 0,
                "losses": 0,
                "battles": 0
            })

        ensure_player("cobra", "King Cobra 🐍")
        ensure_player(opp_id, opp_name)

        db["players"]["cobra"]["battles"] += 1
        db["players"][opp_id]["battles"] += 1

        if wins_opp > wins_cobra:
            db["players"][opp_id]["wins"] += 1
            db["players"]["cobra"]["losses"] += 1
            winner = opp_name
        else:
            db["players"]["cobra"]["wins"] += 1
            db["players"][opp_id]["losses"] += 1
            winner = "King Cobra 🐍"

        save_snake_db(db)

        await m.edit(
            f"🏁 **MATCH OVER**\n\n"
            f"🐍 King Cobra Wins: `{wins_cobra}`\n"
            f"🐍 {opp_name} Wins: `{wins_opp}`\n\n"
            f"🥇 **FINAL WINNER:** `{winner}`\n\n"
            f"📅 Stats Saved ✔"
        )

        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BATTLE STATS
# =====================
@bot.on(events.NewMessage(pattern=r"\.battlestats$"))
async def battlestats(e):
    try:
        await e.delete()
        db = load_snake_db()

        if not db["players"]:
            m = await e.reply("📊 No battles recorded yet")
            await asyncio.sleep(10)
            await m.delete()
            return

        text = "🐍 **SNAKE LEADERBOARD** 🏆\n\n"

        sorted_players = sorted(
            db["players"].values(),
            key=lambda x: x["wins"],
            reverse=True
        )

        for i, p in enumerate(sorted_players[:10], start=1):
            text += (
                f"**{i}. {p['name']}**\n"
                f"🏆 Wins: `{p['wins']}` | ❌ Losses: `{p['losses']}`\n"
                f"⚔ Battles: `{p['battles']}`\n\n"
            )

        m = await e.reply(text)
        await asyncio.sleep(15)
        await m.delete()

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
