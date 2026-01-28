from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    check_mongo_health,
    auto_delete,
    mark_plugin_loaded,
    mark_plugin_error,
    log_error,
    register_help
)

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded("mongo_health.py")

# =====================
# HELP AUTO REGISTER
# =====================
register_help(
    "mongo",
    """
.mongo
Check MongoDB connection health

Shows:
• Connection status
• Database name
• Collection name
• Last ping time
"""
)

# =====================
# MONGO HEALTH COMMAND
# =====================
@Client.on_message(owner_only & filters.command("mongo", "."))
async def mongo_health_cmd(client: Client, m):
    try:
        await m.delete()

        status = check_mongo_health()

        if status["ok"]:
            text = (
                "🟢 **MongoDB Status: CONNECTED**\n\n"
                f"📦 Database: `{status['db']}`\n"
                f"📂 Collection: `{status['collection']}`\n"
                f"⏱ Last Ping: `{status['time']}`"
            )
        else:
            text = (
                "🔴 **MongoDB Status: DISCONNECTED**\n\n"
                f"Error:\n`{status['error']}`"
            )

        msg = await m
