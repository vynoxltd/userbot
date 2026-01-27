from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error, mark_plugin_loaded

mark_plugin_loaded("styletext.py")

# =====================
# STYLE FUNCTIONS
# =====================

def fancy(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fancy_ = "𝒶𝒷𝒸𝒹𝑒𝒻𝓰𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    table = str.maketrans(normal, fancy_)
    return text.translate(table)

def bubble(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bubble_ = "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
    table = str.maketrans(normal, bubble_)
    return text.translate(table)

def square(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    square_ = "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉" * 2
    table = dict(zip(normal, square_))
    return "".join(table.get(c, c) for c in text)

def flip(text):
    normal = "abcdefghijklmnopqrstuvwxyz"
    flipped = "ɐqɔpǝɟɓɥᴉɾʞʃɯuodbɹsʇnʌʍxʎz"
    table = str.maketrans(normal, flipped)
    return text.lower().translate(table)[::-1]

def emoji(text):
    return " ".join(f"{c}️⃣" for c in text if c.isalnum())

def space(text):
    return " ".join(list(text))


# =====================
# COMMAND → FUNCTION MAP
# =====================
STYLES = {
    "fancy": fancy,
    "bubble": bubble,
    "square": square,
    "flip": flip,
    "emoji": emoji,
    "space": space,
}

# =====================
# STYLE HANDLER
# =====================
@Client.on_message(owner_only & filters.command(list(STYLES.keys()), "."))
async def style_handler(client: Client, m):
    try:
        if len(m.command) < 2:
            msg = await client.send_message(
                m.chat.id,
                (
                    "❌ Usage:\n\n"
                    ".fancy text\n"
                    ".bubble text\n"
                    ".square text\n"
                    ".flip text\n"
                    ".emoji text\n"
                    ".space text"
                )
            )
            await auto_delete(msg, 6)
            return

        cmd = m.command[0].lower()
        text = m.text.split(None, 1)[1]

        result = STYLES[cmd](text)

        sent = await client.send_message(m.chat.id, result)

        try:
            await m.delete()
        except:
            pass

        await auto_delete(sent, 40)

    except Exception as e:
        await log_error(client, "styletext.py", e)
