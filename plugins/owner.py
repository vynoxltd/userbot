# plugins/owner.py
from pyrogram import filters
import os

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

def owner_check(_, __, m):
    try:
        # Allow outgoing messages from self
        if m.from_user and m.from_user.id == OWNER_ID:
            return True

        # Allow messages sent by you (filters.me equivalent)
        if m.outgoing:
            return True

        return False
    except Exception:
        return False

owner_only = filters.create(owner_check)
