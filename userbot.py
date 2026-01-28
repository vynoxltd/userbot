from telethon import TelegramClient
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION

bot = TelegramClient(
    StringSession(SESSION),
    API_ID,
    API_HASH
)