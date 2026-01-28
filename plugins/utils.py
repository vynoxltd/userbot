# plugins/utils.py
import asyncio
import traceback
from datetime import datetime
from pyrogram import Client
import os

from pymongo import MongoClient
from pymongo.errors import PyMongoError

# 🔒 Error logs yahin jayenge (Saved Messages)
ERROR_CHAT = "me"

# =====================
# PLUGIN HEALTH STORAGE
# =====================
PLUGIN_STATUS = {}
DISABLED_PLUGINS = set()   # 🔥 auto-heal ke liye

# =====================
# HEALTH HELPERS
# =====================
def mark_plugin_loaded(plugin: str):
    PLUGIN_STATUS[plugin] = {
        "loaded": True,
        "last_error": None,
        "last_error_time": None
    }
    DISABLED_PLUGINS.discard(plugin)


def mark_plugin_error(plugin: str, error: Exception):
    if plugin not in PLUGIN_STATUS:
        PLUGIN_STATUS[plugin] = {"loaded": True}

    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

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
# VARS STORAGE (MongoDB)
# =====================
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment")

try:
    mongo = MongoClient(MONGO_URI)
    db = mongo["userbot"]
    vars_col = db["vars"]
except PyMongoError as e:
    raise RuntimeError(f"MongoDB connection failed: {e}")


def set_var(key: str, value: str):
    try:
        vars_col.update_one(
            {"_id": key},
            {"$set": {"value": value}},
            upsert=True
        )
    except PyMongoError as e:
        mark_plugin_error("vars", e)
        raise


def get_var(key: str, default=None):
    try:
        doc = vars_col.find_one({"_id": key})
        return doc["value"] if doc else default
    except PyMongoError as e:
        mark_plugin_error("vars", e)
        return default


def del_var(key: str):
    try:
        vars_col.delete_one({"_id": key})
    except PyMongoError as e:
        mark_plugin_error("vars", e)


def all_vars():
    try:
        return {doc["_id"]: doc["value"] for doc in vars_col.find()}
    except PyMongoError as e:
        mark_plugin_error("vars", e)
        return {}


# =====================
# HELP AUTO GENERATION (BASE)
# =====================
HELP_REGISTRY = {}

def register_help(plugin: str, text: str):
    HELP_REGISTRY[plugin] = text


def get_all_help():
    return HELP_REGISTRY

# =====================
# MONGO HEALTH CHECK
# =====================
def check_mongo_health():
    try:
        mongo.admin.command("ping")
        return {
            "ok": True,
            "db": db.name,
            "collection": vars_col.name,
            "time": datetime.now().strftime("%d %b %Y %I:%M %p")
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
}
