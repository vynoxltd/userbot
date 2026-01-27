from pyrogram import filters
from config import OWNER_ID

def owner_check(_, __, m):
    return bool(
        m.from_user and
        m.from_user.id == OWNER_ID
    )

owner_only = filters.create(owner_check)
