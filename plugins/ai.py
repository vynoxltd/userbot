# plugins/ai.py

import os
import aiohttp
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.explain_registry import register_explain
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error
from utils.auto_delete import auto_delete

PLUGIN_NAME = "ai.py"

# =====================
# PLUGIN LOAD
# =====================
mark_plugin_loaded(PLUGIN_NAME)
print("✔ ai.py loaded")

# =====================
# CONFIG
# =====================
AI_API_KEY = os.getenv("AI_API_KEY")
AI_API_URL = "https://api.openai.com/v1/responses"

# =====================
# HELP
# =====================
register_help(
    "ai",
    ".ai QUESTION\n"
    "(reply) .ai\n\n"
    "• Ask AI anything\n"
    "• Owner only\n"
    "• Auto delete enabled"
)

# =====================
# EXPLAIN
# =====================
register_explain(
    "ai",
    """
🤖 **AI – Smart Assistant**

.ai How does async work in Python?
(reply) .ai

• Uses OpenAI Responses API
• Fast + stable
• Railway compatible
"""
)

# =====================
# AI REQUEST
# =====================
async def ask_ai(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-5-nano",
        "input": prompt
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            AI_API_URL,
            headers=headers,
            json=payload,
            timeout=90
        ) as resp:
            data = await resp.json()

            # ✅ SAFE PARSING (NEW API)
            try:
                return data["output"][0]["content"][0]["text"]
            except Exception:
                return "❌ AI response parse failed"

# =====================
# AI COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.ai(?:\s+([\s\S]+))?$"))
async def ai_cmd(e):
    if not is_owner(e):
        return

    if not AI_API_KEY:
        msg = await bot.send_message(
            e.chat_id,
            "❌ AI_API_KEY not set in environment"
        )
        return await auto_delete(msg, 6)

    try:
        try:
            await e.delete()
        except:
            pass

        text = e.pattern_match.group(1)

        # reply based
        if not text and e.is_reply:
            r = await e.get_reply_message()
            text = r.text if r else None

        if not text:
            msg = await bot.send_message(
                e.chat_id,
                "Usage:\n.ai QUESTION"
            )
            return await auto_delete(msg, 6)

        thinking = await bot.send_message(e.chat_id, "🤖 Thinking...")

        answer = await ask_ai(text)

        await thinking.delete()

        msg = await bot.send_message(
            e.chat_id,
            f"🤖 **AI Answer**\n\n{answer}"
        )

        await auto_delete(msg, 25)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
