from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded

mark_plugin_loaded("styletext.py")

# =====================
# TEXT STYLES (HTML BASED)
# =====================
STYLES = {
    "bold": lambda t: f"<b>{t}</b>",
    "italic": lambda t: f"<i>{t}</i>",
    "mono": lambda t: f"<code>{t}</code>",
    "strike": lambda t: f"<s>{t}</s>",
    "underline": lambda t: f"<u>{t}</u>",
    "spoiler": lambda t: f"<tg-spoiler>{t}</tg-spoiler>",
    "space": lambda t: " ".join(list(t)),
}

# =====================
# STYLE HANDLER
# =====================
@Client.on_message(owner_only & filters.command(list(STYLES.keys()), "."))
async def style_handler(client: Client, m):
    try:
        await m.delete()

        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                (
                    "❌ Usage:\n"
                    ".bold text\n"
                    ".italic text\n"
                    ".mono text\n"
                    ".strike text\n"
                    ".underline text\n"
                    ".spoiler text\n"
                    ".space text"
                )
            )
            await auto_delete(msg, 6)
            return

        cmd = m.command[0].lower()
        text = m.text.split(None, 1)[1]

        styled_text = STYLES[cmd](text)

        sent = await client.send_message(
            m.chat.id,
            styled_text,
            parse_mode="HTML"
        )

        await auto_delete(sent, 40)

    except Exception as e:
        await log_error(client, "styletext.py", e)
