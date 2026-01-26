from pyrogram import filters
from config import OWNER_ID

owner_only = filters.create(
    lambda _, __, m: m.from_user and m.from_user.id == OWNER_ID
)