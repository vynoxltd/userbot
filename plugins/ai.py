# plugins/ai.py

import os
import aiohttp
import asyncio
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
AI_API_URL = "https://api.openai.com/v1/chat/completions"

# =====================
# HELP REGISTER
# =====================
register_help(
    "ai",
    ".ai QUESTION\n\n"
    "• Ask AI anything\n"
    "• Reply supported\n"
    "• Owner only\n"
    "• Auto delete enabled"
)

# =====================
# EXPLANATION REGISTER
# =====================
register_explain(
    "ai",
    """
🤖 **AI – Smart Assistant**

━━━━━━━━━━━━━━
📌 PURPOSE:
AI plugin tumhe live questions ka answer deta hai.

━━━━━━━━━━━━━━
📌 COMMAND:
.ai QUESTION  
(reply) .ai  

━━━━━━━━━━━━━━
📌 USE CASES:
• Coding help
• Debugging logic
• Explanations
• Idea generation

━━━━━━━━━━━━━━
⚠️ NOTES:
• API key required
• Internet needed
• Heavy queries slow ho sakte hain
"""
)

# =====================
# AI REQUEST
# =====================
async def ask_ai(prompt: str):
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        " shows_typing": False,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            AI_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        ) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

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
            "❌ AI_API_KEY not set"
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

        await auto_delete(msg, 20)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)