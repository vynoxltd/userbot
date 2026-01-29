# plugins/scheduler.py

import asyncio
import re
from datetime import datetime, timedelta

from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.auto_delete import auto_delete
from utils.mongo import mongo

PLUGIN_NAME = "scheduler.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ scheduler.py loaded")

# =====================
# DB
# =====================
db = mongo["userbot"]
col = db["schedules"]

# =====================
# HELP REGISTER
# =====================
register_help(
    "scheduler",
    ".schedule TIME TEXT\n"
    ".schedules\n"
    ".cancelschedule ID\n\n"
    "• Schedule messages\n"
    "• Persistent (MongoDB)\n"
    "• Owner only"
)

# =====================
# EXPLANATION REGISTER
# =====================
register_explain(
    "scheduler",
    """
⏰ **SCHEDULER – Message Scheduler**

━━━━━━━━━━━━━━
📌 PURPOSE:
Future me messages automatically bhejne ke liye.

━━━━━━━━━━━━━━
📌 COMMANDS:

.schedule 10m Hello  
.schedule 2h Good night  
.schedule 2026-02-01 09:00 Happy Birthday  

.schedules  
.cancelschedule ID  

━━━━━━━━━━━━━━
📌 USE CASES:
• Birthday wishes
• Reminders
• Announcements
• Daily messages

━━━━━━━━━━━━━━
⚠️ NOTES:
• MongoDB required
• Bot restart ke baad bhi schedules safe rehte hain
"""
)

# =====================
# TIME PARSER
# =====================
def parse_time(text: str):
    if re.match(r"^\d+m$", text):
        return datetime.utcnow() + timedelta(minutes=int(text[:-1]))

    if re.match(r"^\d+h$", text):
        return datetime.utcnow() + timedelta(hours=int(text[:-1]))

    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M")
    except:
        return None

# =====================
# BACKGROUND WORKER
# =====================
async def scheduler_worker():
    await bot.wait_until_ready()

    while True:
        try:
            now = datetime.utcnow()
            tasks = col.find({"run_at": {"$lte": now}, "done": False})

            for task in tasks:
                await bot.send_message(task["chat_id"], task["text"])
                col.update_one(
                    {"_id": task["_id"]},
                    {"$set": {"done": True}}
                )

        except Exception as ex:
            mark_plugin_error(PLUGIN_NAME, ex)
            await log_error(bot, PLUGIN_NAME, ex)

        await asyncio.sleep(5)

bot.loop.create_task(scheduler_worker())

# =====================
# .schedule
# =====================
@bot.on(events.NewMessage(pattern=r"\.schedule(?:\s+([\s\S]+))?$"))
async def schedule_cmd(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        args = (e.pattern_match.group(1) or "").split(None, 1)
        if len(args) < 2:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.schedule TIME TEXT"
            )
            return await auto_delete(msg, 6)

        when = parse_time(args[0])
        if not when:
            msg = await bot.send_message(e.chat_id, "❌ Invalid time format")
            return await auto_delete(msg, 6)

        doc = {
            "chat_id": e.chat_id,
            "text": args[1],
            "run_at": when,
            "done": False
        }

        res = col.insert_one(doc)

        msg = await bot.send_message(
            e.chat_id,
            f"⏰ Scheduled\nID: `{res.inserted_id}`\nAt: `{when}`"
        )
        await auto_delete(msg, 8)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# .schedules
# =====================
@bot.on(events.NewMessage(pattern=r"\.schedules$"))
async def list_schedules(e):
    if not is_owner(e):
        return

    try:
        await e.delete()

        tasks = list(col.find({"done": False}))
        if not tasks:
            msg = await bot.send_message(e.chat_id, "📭 No pending schedules")
            return await auto_delete(msg, 6)

        text = "📅 **Scheduled Messages**\n\n"
        for t in tasks:
            text += f"• `{t['_id']}` → `{t['run_at']}`\n"

        msg = await bot.send_message(e.chat_id, text)
        await auto_delete(msg, 15)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# .cancelschedule
# =====================
@bot.on(events.NewMessage(pattern=r"\.cancelschedule(?: (.*))?$"))
async def cancel_schedule(e):
    if not is_owner(e):
        return

    try:
        await e.delete()
        sid = (e.pattern_match.group(1) or "").strip()

        if not sid:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.cancelschedule ID"
            )
            return await auto_delete(msg, 6)

        col.delete_one({"_id": sid})
        msg = await bot.send_message(e.chat_id, "❌ Schedule cancelled")
        await auto_delete(msg, 6)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)