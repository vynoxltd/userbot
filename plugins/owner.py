# plugins/owner.py
from pyrogram import filters
from config import OWNER_ID

"""
OWNER FILTER
Compatible with:
@Client.on_message(owner_only & filters.command("cmd", "."))

Design goals:
- No plugin changes required
- Works with incoming commands
- Works in private, groups, saved messages
- Safe with Pyrogram 2.x
"""

def owner_check(_, __, m):
    try:
        # 1️⃣ Incoming message from owner
        if m.from_user and m.from_user.id == OWNER_ID:
            return True

        # 2️⃣ Outgoing message sent by you (Saved Messages etc.)
        if m.outgoing:
            return True

        return False
    except Exception:
        return False


# 🔥 ORDER-SAFE, PLUGIN-SAFE OWNER FILTER
owner_only = filters.create(owner_check)
