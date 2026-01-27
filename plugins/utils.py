# plugins/utils.py
import asyncio
import traceback
from datetime import datetime
from pyrogram import Client
import json
import os

# 🔒 Error logs yahin jayenge (Saved Messages)
ERROR_CHAT = "me"

# =====================
# PLUGIN HEALTH STORAGE
# =====================
PLUGIN_STATUS = {}
DISABLED_PLUGINS = set()   # 🔥 auto-heal ke liye

"""
PLUGIN_STATUS format:
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
    # agar plugin dobara load hua → auto heal
    DISABLED_PLUGINS.discard(plugin)


def mark_plugin_error(plugin: str, error: Exception):
    if plugin not in PLUGIN_STATUS:
        PLUGIN_STATUS[plugin] = {"loaded": True}

    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

    # 🔥 AUTO HEAL (disable faulty plugin)
    DISABLED_PLUGINS.add(plugin)


def is_plugin_disabled(plugin: str) -> bool:
    return plugin in DISABLED_PLUGINS


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
    print(f"[PLUGIN ERROR] {plugin}: {error}")
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


# =====================
# BOT MANAGER (MULTI-BOT)
# =====================
RUNNING_BOTS = {}   # name -> Client instance

async def start_bot(name: str, token: str, api_id: int, api_hash: str):
    if name in RUNNING_BOTS:
        raise RuntimeError("Bot already running")

    try:
        bot = Client(
            name=f"bot_{name}",
            bot_token=token,
            api_id=api_id,
            api_hash=api_hash,
            plugins=dict(root="bot_plugins")
        )

        await bot.start()
        RUNNING_BOTS[name] = bot

    except Exception as e:
        mark_plugin_error("bot_manager", e)
        raise


async def stop_bot(name: str):
    bot = RUNNING_BOTS.get(name)
    if not bot:
        raise RuntimeError("Bot not running")

    await bot.stop()
    del RUNNING_BOTS[name]


def list_running_bots():
    return list(RUNNING_BOTS.keys())


# =====================
# VARS STORAGE (JSON)
# =====================
VARS_FILE = "data/vars.json"
os.makedirs("data", exist_ok=True)

if os.path.exists(VARS_FILE):
    with open(VARS_FILE, "r") as f:
        _VARS = json.load(f)
else:
    _VARS = {}

def save_vars():
    with open(VARS_FILE, "w") as f:
        json.dump(_VARS, f, indent=2)

def set_var(key: str, value: str):
    _VARS[key] = value
    save_vars()

def get_var(key: str, default=None):
    return _VARS.get(key, default)

def del_var(key: str):
    if key in _VARS:
        del _VARS[key]
        save_vars()

def all_vars():
    return _VARS


# =====================
# HELP AUTO GENERATION (BASE)
# =====================
HELP_REGISTRY = {}

def register_help(plugin: str, text: str):
    """
    Plugin ke andar call karo:
    register_help("mention", "...commands...")
    """
    HELP_REGISTRY[plugin] = text

def get_all_help():
    return HELP_REGISTRY
