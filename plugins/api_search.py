# plugins/api_search.py
# Generic API Search Plugin for Telethon Userbot

import asyncio
import requests
from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import register_help
from utils.logger import log_error

PLUGIN_NAME = "api_search.py"
print("✔ api_search.py loaded (API SEARCH MODE)")

# =====================
# CONFIG (CHANGE THESE)
# =====================
API_KEY = "17e800e335119171f811d8fea35781b3"
API_URL = "https://apilayer.net/api/validate"  # <-- change this

TIMEOUT = 15  # seconds

# =====================
# HELP
# =====================
register_help(
    "search",
    ".search <name/number>\n\n"
    "• Searches data using API key\n"
    "• Supports name / number lookup\n"
    "• External API powered"
)

# =====================
# SEARCH COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.search\s+(.+)"))
async def api_search(e):
    try:
        query = e.pattern_match.group(1).strip()
        if not query:
            return await e.reply("❌ Provide something to search")

        msg = await e.reply("🔍 Searching...")

        # ---------- API REQUEST ----------
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Telethon-Userbot"
        }

        params = {
            "query": query  # API ke hisaab se change kar sakte ho
        }

        r = requests.get(
            API_URL,
            headers=headers,
            params=params,
            timeout=TIMEOUT
        )

        if r.status_code != 200:
            await msg.edit("❌ API error or invalid response")
            return

        data = r.json()

        # ---------- SAMPLE RESPONSE HANDLING ----------
        # ⚠️ Ye part API ke response ke hisaab se change hoga

        if not data or data.get("status") is False:
            await msg.edit("❌ No data found")
            return

        result = data.get("result", {})

        name = result.get("name", "N/A")
        number = result.get("number", "N/A")
        email = result.get("email", "N/A")
        location = result.get("location", "N/A")

        text = (
            "📄 **SEARCH RESULT**\n\n"
            f"👤 Name: `{name}`\n"
            f"📞 Number: `{number}`\n"
            f"📧 Email: `{email}`\n"
            f"📍 Location: `{location}`\n\n"
            f"🔎 Query: `{query}`"
        )

        await msg.edit(text)

    except requests.exceptions.Timeout:
        await e.reply("⚠️ API timeout, try again later")
    except Exception as ex:
        await log_error(bot, PLUGIN_NAME, ex)
        await e.reply("❌ Unexpected error occurred")
