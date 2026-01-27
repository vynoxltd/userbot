from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import log_error, mark_plugin_loaded

mark_plugin_loaded("styletext.py")

# =====================
# STYLE MAP (UNICODE)
# =====================

def bold(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bold_ = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    return text.translate(str.maketrans(normal, bold_))


def italic(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    italic_ = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘐𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    return text.translate(str.maketrans(normal, italic_))


def square(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    square_ = (
        "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
        "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
    )
    return text.translate(str.maketrans(normal, square_))


def space(text):
    return " ".join(list(text))


STYLES = {
    "bold": bold,
    "italic": italic,
    "square": square,
    "space": space,
}

# =====================
# STYLE HANDLER
# =====================
@Client.on_message(owner_only & filters.command(list(STYLES.keys()), "."))
async def style_handler(client: Client, m):
    try:
        if len(m.command) < 2:
            await m.reply_text(
                "Usage:\n"
                ".bold text\n"
                ".italic text\n"
                ".square text\n"
                ".space text"
            )
            return

        cmd = m.command[0].lower()
        text = m.text.split(None, 1)[1]

        styled = STYLES[cmd](text)

        await m.reply_text(styled)

    except Exception as e:
        await log_error(client, "styletext.py", e)
