import random
import asyncio
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
# key = message_id, value = correct_number

# =====================
# START GUESS GAME
# =====================
@bot.on(events.NewMessage(pattern=r"\.guess$"))
async def start_guess(e):
    try:
        await e.delete()

        number = random.randint(1, 10)

        msg = await e.reply(
            "🎯 **GUESS THE NUMBER**\n\n"
            "I'm thinking of a number between **1 and 10** 🤔\n"
            "👉 Reply to this message with your guess"
        )

        # store game
        active_guess_games[msg.id] = number

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# HANDLE GUESSES
# =====================
@bot.on(events.NewMessage)
async def handle_guess(e):
    try:
        if not e.is_reply:
            return

        reply = await e.get_reply_message()
        if not reply or reply.id not in active_guess_games:
            return

        # user guess
        try:
            guess = int(e.raw_text.strip())
        except ValueError:
            return  # ignore non-numbers

        correct = active_guess_games[reply.id]

        if guess == correct:
            await e.reply(
                f"🎉 **Correct Guess!**\n\n"
                f"👤 {e.sender.first_name} guessed it right ✅\n"
                f"🎯 Number was: `{correct}`"
            )
            # end game
            del active_guess_games[reply.id]

        else:
            await e.reply(
                f"❌ Wrong Guess!\n"
                f"`{guess}` is not correct 😅"
            )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
