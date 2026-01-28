# plugins/owner.py
from pyrogram import filters
from config import OWNER_ID

# 🔥 USER FILTER (PYROGRAM NATIVE)
owner_only = filters.user(OWNER_ID)
