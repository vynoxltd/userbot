from telethon import events
from telethon.tl.types import (
    InputBotInlineResultArticle,
    InputTextMessageContent
)

from userbot import bot

print("✔ help_inline.py loaded")

# =====================
# INLINE HELP HANDLER
# =====================
@bot.on(events.InlineQuery)
async def inline_help(event):
    query = (event.text or "").lower()

    # only trigger on "help"
    if query != "help":
        return

    result = InputBotInlineResultArticle(
        id="help_inline_1",
        title="Userbot Help",
        description="Inline help working",
        input_message_content=InputTextMessageContent(
            "Help working ✅"
        )
    )

    await event.answer(
        [result],
        cache_time=0,
        is_personal=True
    )