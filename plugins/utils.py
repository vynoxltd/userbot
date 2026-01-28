# plugins/utils.py
import asyncio
import traceback
import os
from datetime import datetime, timedelta
from pyrogram import Client

# =====================
# PLUGIN HEALTH
# =====================
PLUGIN_STATUS = {}
DISABLED_PLUGINS = set()

def mark_plugin_loaded(plugin: str):
    PLUGIN_STATUS[plugin] = {
        "loaded": True,
        "last_error": None,
        "last_error_time": None
    }
    DISABLED_PLUGINS.discard(plugin)

def mark_plugin_error(plugin: str, error: Exception):
    PLUGIN_STATUS.setdefault(plugin, {})
    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )
    DISABLED_PLUGINS.add(plugin)

def is_plugin_disabled(plugin: str):
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

async def auto_delete(msg, seconds: int):
    try:
        await asyncio.sleep(seconds)
        await msg.delete()
    except:
        pass


# =====================
# ERROR LOGGER
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
        await client.send_message("me", text)
    except:
        pass


# =====================
# HELP REGISTRY (STRING BASED)
# =====================
HELP_REGISTRY = {}

def register_help(plugin: str, text: str):
    HELP_REGISTRY[plugin.lower()] = text.strip()

def get_all_help():
    return HELP_REGISTRY


# =====================
# OPTIONAL MONGO STORAGE
# =====================
mongo = None
vars_col = None

MONGO_URI = os.getenv("MONGO_URI")

if MONGO_URI:
    try:
        from pymongo import MongoClient
        mongo = MongoClient(MONGO_URI)
        db = mongo["userbot"]
        vars_col = db["vars"]
        print("✅ MongoDB connected")
    except Exception as e:
        print("⚠️ Mongo disabled:", e)

def set_var(key: str, value: str):
    if not vars_col:
        return
    vars_col.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )

def get_var(key: str, default=None):
    if not vars_col:
        return default
    doc = vars_col.find_one({"_id": key})
    return doc["value"] if doc else default

def del_var(key: str):
    if vars_col:
        vars_col.delete_one({"_id": key})

def all_vars():
    if not vars_col:
        return {}
    return {doc["_id"]: doc["value"] for doc in vars_col.find()}


# =====================
# 🔥 BOT MANAGER SUPPORT (FIX FOR ERROR)
# =====================
RUNNING_BOTS = {}

async def start_bot(name: str, token: str, api_id: int, api_hash: str):
    if name in RUNNING_BOTS:
        raise RuntimeError("Bot already running")

    bot = Client(
        name=f"bot_{name}",
        bot_token=token,
        api_id=api_id,
        api_hash=api_hash
    )

    await bot.start()
    RUNNING_BOTS[name] = bot


async def stop_bot(name: str):
    bot = RUNNING_BOTS.get(name)
    if not bot:
        raise RuntimeError("Bot not running")

    await bot.stop()
    del RUNNING_BOTS[name]


def list_running_bots():
    return list(RUNNING_BOTS.keys())
