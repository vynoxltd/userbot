# plugins/utils.py
import asyncio
import traceback
import os
from datetime import datetime, timedelta

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
# 🔥 EXACT MATCH with alive.py, help4.py, pluginhealth.py
HELP_REGISTRY = {}

def register_help(plugin: str, text: str):
    """
    plugin : help section name (basic, autoreply, pluginhealth, etc.)
    text   : multiline help string
    """
    HELP_REGISTRY[plugin.lower()] = text.strip()

def get_all_help():
    return HELP_REGISTRY


# =====================
# OPTIONAL MONGO (SAFE)
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

def check_mongo_health():
    if not mongo:
        return {"ok": False, "error": "Mongo disabled"}
    try:
        mongo.admin.command("ping")
        ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
        return {
            "ok": True,
            "time": ist.strftime("%d %b %Y %I:%M %p")
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
