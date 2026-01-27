from pyrogram import Client, filters
from plugins.owner import owner_only

# =====================
# STYLE FUNCTIONS
# =====================

def bold(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    bold_ = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    return text.translate(str.maketrans(normal, bold_))


def italic(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    italic_ = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    return text.translate(str.maketrans(normal, italic_))


def square(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    square_ = (
        "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
        "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉"
    )
    return text.translate(str.maketrans(normal, square_))


# =====================
# COMMANDS
# =====================

@Client.on_message(owner_only & filters.command("bold", "."))
async def bold_cmd(_, m):
    if len(m.command) < 2:
        return
    await m.reply_text(bold(m.text.split(None, 1)[1]))


@Client.on_message(owner_only & filters.command("italic", "."))
async def italic_cmd(_, m):
    if len(m.command) < 2:
        return
    await m.reply_text(italic(m.text.split(None, 1)[1]))


@Client.on_message(owner_only & filters.command("square", "."))
async def square_cmd(_, m):
    if len(m.command) < 2:
        return
    await m.reply_text(square(m.text.split(None, 1)[1]))
