# plugins/utils.py
# ==========================================================
# CENTRAL UTILS LAYER (CRASH-PROOF)
# Used by 30+ plugins
# ==========================================================

import asyncio
import traceback
import os
from datetime import datetime, timedelta

# ==========================================================
# PLUGIN HEALTH SYSTEM
# ==========================================================

PLUGIN_STATUS = {}        # plugin_name -> info
DISABLED_PLUGINS = set() # auto-disable on error


def mark_plugin_loaded(plugin: str):
    PLUGIN_STATUS[plugin] = {
        "loaded": True,
        "last_error": None,
        "last_error_time": None,
    }
    DISABLED_PLUGINS.discard(plugin)


def mark_plugin_error(plugin: str, error: Exception):
    PLUGIN_STATUS.setdefault(plugin, {})
    PLUGIN_STATUS[plugin]["last_error"] = str(error)
    PLUGIN_STATUS[plugin]["last_error_time"] = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )
    DISABLED_PLUGINS.add(plugin)


def is_plugin_disabled(plugin: str) -> bool:
    return plugin in DISABLED_PLUGINS


def get_plugin_health():
    return PLUGIN_STATUS


# ==========================================================
# SAFE MESSAGE HELPERS
# ==========================================================

async def safe_delete(msg):
    try:
        if msg:
            await msg.delete()
    except:
        pass


async def auto_delete(msg, seconds: int):
    try:
        if not msg:
            return
        await asyncio.sleep(seconds)
        await msg.delete()
    except:
        pass


# ==========================================================
# GLOBAL ERROR LOGGER (NEVER CRASHES)
# ==========================================================

async def log_error(client, plugin: str, error: Exception):
    print(f"[PLUGIN ERROR] {plugin}: {error}")
    mark_plugin_error(plugin, error)

    try:
        text = (
            "🚨 PLUGIN ERROR\n\n"
            f"Plugin: {plugin}\n"
            f"Time: {datetime.now().strftime('%d %b %Y %I:%M %p')}\n\n"
            f"Error:\n{str(error)}\n\n"
            f"Traceback:\n{traceback.format_exc(limit=5)}"
        )
        if client is not None:
            await client.send_message("me", text)
    except Exception as e:
        print("[ERROR LOGGER FAILED]", e)


# ==========================================================
# MONGO (OPTIONAL / SAFE)
# ==========================================================

mongo = None
db = None
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
        mongo = None
        db = None
        vars_col = None
        print("⚠️ MongoDB disabled:", e)


def set_var(key: str, value: str):
    if vars_col is None:
        return
    try:
        vars_col.update_one(
            {"_id": key},
            {"$set": {"value": value}},
            upsert=True,
        )
    except Exception as e:
        mark_plugin_error("vars", e)


def get_var(key: str, default=None):
    if vars_col is None:
        return default
    try:
        doc = vars_col.find_one({"_id": key})
        return doc["value"] if doc else default
    except Exception as e:
        mark_plugin_error("vars", e)
        return default


def del_var(key: str):
    if vars_col is None:
        return
    try:
        vars_col.delete_one({"_id": key})
    except Exception as e:
        mark_plugin_error("vars", e)


def all_vars():
    if vars_col is None:
        return {}
    try:
        return {doc["_id"]: doc["value"] for doc in vars_col.find()}
    except Exception as e:
        mark_plugin_error("vars", e)
        return {}


def check_mongo_health():
    if mongo is None:
        return {"ok": False, "error": "Mongo disabled"}
    try:
        mongo.admin.command("ping")
        ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
        return {
            "ok": True,
            "time": ist.strftime("%d %b %Y %I:%M %p"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ==========================================================
# BOT MANAGER SUPPORT (REQUIRED BY botmanager.py)
# ==========================================================

from pyrogram import Client

RUNNING_BOTS = {}  # name -> Client instance


async def start_bot(name: str, token: str, api_id: int, api_hash: str):
    if name in RUNNING_BOTS:
        raise RuntimeError("Bot already running")

    bot = Client(
        name=f"bot_{name}",
        bot_token=token,
        api_id=api_id,
        api_hash=api_hash,
        plugins=dict(root="bot_plugins"),
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

# =====================
# BOT MANAGER SUPPORT
# =====================

from pyrogram import Client

RUNNING_BOTS = {}  # name -> Client instance


async def start_bot(name: str, token: str, api_id: int, api_hash: str):
    if name in RUNNING_BOTS:
        raise RuntimeError("Bot already running")

    bot = Client(
        name=f"bot_{name}",
        bot_token=token,
        api_id=api_id,
        api_hash=api_hash,
        plugins=dict(root="bot_plugins")
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
# ==========================================================
# HELP REGISTRY (SECONDARY SYSTEM)
# ==========================================================

HELP_REGISTRY = {}  # plugin -> text


def register_help(plugin: str, text: str):
    HELP_REGISTRY[plugin] = text


def get_all_help():
    return HELP_REGISTRY
