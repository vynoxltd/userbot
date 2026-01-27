from pyrogram import filters
from config import OWNER_ID

def owner_check(_, __, m):
    if not m.from_user:
        return False
    return int(m.from_user.id) == int(OWNER_ID)

owner_only = filters.create(owner_check)
