from userbot import bot
from loader import load_plugins

load_plugins()

bot.start()
bot.run_until_disconnected()