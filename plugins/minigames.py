import random
import asyncio
import time
from telethon import events

from userbot import bot
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "minigames.py"
mark_plugin_loaded(PLUGIN_NAME)

# =====================
# GAME STORAGE
# =====================
active_guess_games = {}
# key = message_id
# value = {"number": int, "end": timestamp}

# =====================
# START GUESS GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.guess$"))
async def start_guess(e):
    try:
        await e.delete()

        number = random.randint(1, 10)
        end_time = time.time() + 30  # 30 sec

        msg = await e.reply(
            "🎯 **GUESS THE NUMBER**\n\n"
            "I'm thinking of a number between **1 and 10** 🤔\n"
            "⏱ You have **30 seconds**\n\n"
            "👉 Reply to this message with your guess"
        )

        active_guess_games[msg.id] = {
            "number": number,
            "end": end_time
        }

        # auto timeout
        await asyncio.sleep(30)

        if msg.id in active_guess_games:
            correct = active_guess_games[msg.id]["number"]
            await msg.reply(
                f"⏰ **TIME UP!**\n\n"
                f"No one guessed it 😅\n"
                f"🎯 Correct number was: `{correct}`"
            )
            del active_guess_games[msg.id]

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# HANDLE GUESSES (MULTIPLAYER)
# =====================
@bot.on(events.NewMessage)
async def handle_guess(e):
    try:
        if not e.is_reply:
            return

        reply = await e.get_reply_message()
        if not reply or reply.id not in active_guess_games:
            return

        game = active_guess_games[reply.id]

        # time over check
        if time.time() > game["end"]:
            if reply.id in active_guess_games:
                del active_guess_games[reply.id]
            return

        # number check
        try:
            guess = int(e.raw_text.strip())
        except ValueError:
            return  # ignore non-numbers

        correct = game["number"]

        if guess == correct:
            await e.reply(
                f"🎉 **CORRECT GUESS!**\n\n"
                f"👑 Winner: **{e.sender.first_name}**\n"
                f"🎯 Number was: `{correct}`"
            )
            del active_guess_games[reply.id]
        else:
            await e.reply(f"❌ `{guess}` is wrong!")

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
