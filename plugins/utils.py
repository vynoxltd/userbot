# plugins/utils.py
import asyncio
import traceback
from datetime import datetime

# 🔒 Error logs yahin jayenge (Saved Messages)
ERROR_CHAT = "me"

# =====================
# PLUGIN HEALTH STORAGE
# =====================
PLUGIN_STATUS = {}
"""
Format:
{
  "plugin.py": {
      "loaded": True,
      "last_error": "error text or None",
      "last_error_time": "time or None"
  }
}
"""

# =====================
# HEALTH HELPERS
# =====================
def mark_plugin_loaded(plugin: str):
    PLUGIN_STATUS[plugin] = {
        "loaded": True,
        "last_error": None,
        "last_error_time": None
    }

def mark_plugin_error(plugin: str, error: Exception):
    if plugin not in PLUGIN_STATUS:
        PLUGIN_STATUS[plugin] = {"loaded": True}

    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

def get_plugin_health():
    return PLUGIN_STATUS


# =====================
# SAFE DELETE
# =====================
async def safe_delete(msg):
    try:
        await msg.delete()
    except:
        pass


# =====================
# AUTO DELETE MESSAGE
# =====================
async def auto_delete(msg, seconds: int):
    try:
        await asyncio.sleep(seconds)
        await msg.delete()
    except:
        pass


# =====================
# PLUGIN ERROR LOGGER
# =====================
async def log_error(client, plugin: str, error: Exception):
    """
    Send plugin error + traceback to Saved Messages
    + print in terminal
    + mark plugin unhealthy
    """

    # 🔥 terminal log
    print(f"[PLUGIN ERROR] {plugin}: {error}")

    # 🧠 mark plugin error
    mark_plugin_error(plugin, error)

    try:
        text = (
            "PLUGIN ERROR\n\n"
            f"Plugin: {plugin}\n"
            f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
            f"Error:\n{str(error)}\n\n"
            f"Traceback:\n{traceback.format_exc(limit=5)}"
        )

        await client.send_message(ERROR_CHAT, text)

    except Exception as e:
        print("[LOG_ERROR FAILED]", e)