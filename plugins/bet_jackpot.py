# plugins/bet_jackpot.py

import time
import random
import asyncio
from telethon import events

from userbot import bot
from utils.players_helper import get_player, save_players
from utils.help_registry import register_help
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "bet_jackpot.py"
mark_plugin_loaded(PLUGIN_NAME)
print("✔ bet_jackpot.py loaded")

# =====================
# HELP
# =====================
register_help(
    "bet",
    ".bet <amount>\n"
    ".jackpot\n\n"
    "• Bet unique coins to win double\n"
    "• Same bet = loss\n"
    "• Daily jackpot rewards"
)

# =====================
# CONFIG
# =====================
AUTO_DEL = 8
DAILY_COOLDOWN = 86400  # 24h

# active bet amounts per chat
ACTIVE_BETS = {}  # chat_id -> set(amounts)

# =====================
# TEMP MESSAGE
# =====================
async def temp_msg(chat, text, reply=None):
    m = await bot.send_message(chat, text, reply_to=reply)
    await asyncio.sleep(AUTO_DEL)
    await m.delete()

# =====================
# BET GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.bet (\d+)$"))
async def bet_game(e):
    try:
        amount = int(e.pattern_match.group(1))
        chat = e.chat_id

        data, p = get_player(e.sender_id, e.sender.first_name)

        if amount <= 0:
            return

        if p["coins"] < amount:
            await temp_msg(chat, "❌ Not enough coins", e.id)
            return

        bets = ACTIVE_BETS.setdefault(chat, set())

        # ❌ DUPLICATE BET
        if amount in bets:
            p["coins"] -= amount
            save_players(data)

            await temp_msg(
                chat,
                f"💥 **BET FAILED!**\n"
                f"Amount `{amount}` already used\n"
                f"💸 Lost `{amount}` coins",
                e.id
            )
            return

        # ✅ UNIQUE BET
        bets.add(amount)
        win = amount * 2
        p["coins"] += amount  # net +amount
        save_players(data)

        await temp_msg(
            chat,
            f"🎉 **BET WON!**\n"
            f"💰 Bet: `{amount}`\n"
            f"🏆 Won: `{win}` coins",
            e.id
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# JACKPOT (DAILY)
# =====================
@bot.on(events.NewMessage(pattern=r"\.jackpot$"))
async def jackpot(e):
    try:
        data, p = get_player(e.sender_id, e.sender.first_name)
        now = int(time.time())

        last = p.get("last_jackpot", 0)
        if now - last < DAILY_COOLDOWN:
            left = DAILY_COOLDOWN - (now - last)
            hrs = left // 3600
            await temp_msg(
                e.chat_id,
                f"⏳ Jackpot already claimed\nTry again in `{hrs}h`",
                e.id
            )
            return

        # 🎰 WEIGHTED REWARDS
        rewards = [50, 100, 200, 500]
        weights = [60, 30, 8, 2]  # 500 very rare

        reward = random.choices(rewards, weights)[0]

        p["coins"] += reward
        p["last_jackpot"] = now
        save_players(data)

        await temp_msg(
            e.chat_id,
            f"🎁 **DAILY JACKPOT!**\n"
            f"💰 You won `{reward}` coins",
            e.id
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
