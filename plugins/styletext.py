from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("styletext.py")
# ======================
# UNICODE MAPS
# ======================

NORMAL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

BOLD = (
    "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
    "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
    "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
)

ITALIC = (
    "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
    "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
    "0123456789"
)

MONO = (
    "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"
    "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
)

# ======================
# HELPERS
# ======================

def safe_convert(text: str, target: str) -> str:
    table = {NORMAL[i]: target[i] for i in range(min(len(NORMAL), len(target)))}
    return "".join(table.get(c, c) for c in text)

def emoji(text):
    return "".join(f"{c}✨" if c.isalpha() else c for c in text)

def spaced(text):
    return " ".join(text)

def get_text(m):
    return " ".join(m.command[1:]).strip()

# ======================
# COMMANDS (USERBOT SAFE)
# ======================

@Client.on_message(filters.me & owner_only & filters.command("bold", "."))
async def bold(client, m):
    try:
        await m.delete()
        text = get_text(m)
        if not text:
            return
        msg = await m.reply(safe_convert(text, BOLD))
        await auto_delete(msg, 8)
    except Exception as e:
        await log_error(client, "styletext.py", e)


@Client.on_message(filters.me & owner_only & filters.command("italic", "."))
async def italic(client, m):
    try:
        await m.delete()
        text = get_text(m)
        if not text:
            return
        msg = await m.reply(safe_convert(text, ITALIC))
        await auto_delete(msg, 8)
    except Exception as e:
        await log_error(client, "styletext.py", e)


@Client.on_message(filters.me & owner_only & filters.command("mono", "."))
async def mono(client, m):
    try:
        await m.delete()
        text = get_text(m)
        if not text:
            return
        msg = await m.reply(safe_convert(text, MONO))
        await auto_delete(msg, 8)
    except Exception as e:
        await log_error(client, "styletext.py", e)


@Client.on_message(filters.me & owner_only & filters.command("emoji", "."))
async def emoji_cmd(client, m):
    try:
        await m.delete()
        text = get_text(m)
        if not text:
            return
        msg = await m.reply(emoji(text))
        await auto_delete(msg, 10)
    except Exception as e:
        await log_error(client, "styletext.py", e)


@Client.on_message(filters.me & owner_only & filters.command("space", "."))
async def space_cmd(client, m):
    try:
        await m.delete()
        text = get_text(m)
        if not text:
            return
        msg = await m.reply(spaced(text))
        await auto_delete(msg, 10)
    except Exception as e:
        await log_error(client, "styletext.py", e)