# plugins/owner.py
from pyrogram import filters
from config import OWNER_ID

def owner_check(_, __, m):
    try:
        # outgoing (self)
        if m.outgoing:
            return True

        # incoming from owner
        if m.from_user and m.from_user.id == OWNER_ID:
            return True

        return False
    except Exception:
        return False

owner_only = filters.create(owner_check)
