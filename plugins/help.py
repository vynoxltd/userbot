from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    get_plugin_health,
    mark_plugin_loaded,
    log_error
)

mark_plugin_loaded("help.py")

# =====================
# HELP MAIN
# =====================

HELP_MAIN = """
USERBOT HELP

Use:
.help <plugin>

Available plugins:
basic
cleanup
style
spam
forward
notes
media
games
fun
random
auto
dev
info

Extra:
.help all
.help broken
.help2
.help3
"""

# =====================
# PLUGIN WISE HELP
# =====================

HELP_PLUGINS = {

"basic": """
.alive | exm: .alive
.ping | exm: .ping
.restart | exm: .restart
""",

"cleanup": """
.purge | exm: (reply) .purge
.clean <count> | exm: .clean 10
.del | exm: (reply) .del
.delall | exm: (reply user) .delall
""",

"style": """
.bold <text> | exm: .bold hello
.italic <text> | exm: .italic hello
.mono <text> | exm: .mono hello
.emoji <text> | exm: .emoji hello
.space <text> | exm: .space hello
""",

"spam": """
.spam <count> <text> | exm: .spam 5 hi
.delayspam <count> <delay> <text> | exm: .delayspam 5 1.5 hi
.replyspam <count> | exm: (reply) .replyspam 10
.tag <count> <text> <user> | exm: .tag 5 hi @user
""",

"forward": """
.fwd <chat_id> | exm: .fwd -100123456
.sfwd <chat_id> | exm: .sfwd -100123456
.fwdhere | exm: (reply) .fwdhere
.mfwd <chat_id> <count> | exm: .mfwd -100123456 5
""",

"notes": """
.setnote <name> <text> | exm: .setnote test hello
.getnote <name> | exm: .getnote test
.delnote <name> | exm: .delnote test
""",

"media": """
.ss | exm: (reply view-once media) .ss
.save | exm: (reply) .save
""",

"games": """
.dice | exm: .dice
.coin | exm: .coin
.luck | exm: .luck
""",

"fun": """
.neko | exm: .neko
.nekokiss | exm: .nekokiss
.nekohug | exm: .nekohug
.nekoslap | exm: .nekoslap
.nekofuck | exm: .nekofuck
""",

"random": """
.predict | exm: .predict
.8ball | exm: .8ball
.truth | exm: .truth
.dare | exm: .dare
.joke | exm: .joke
.quote | exm: .quote
.insult <user> | exm: .insult @user
.compliment <user> | exm: .compliment @user
""",

"auto": """
.autoreply on | exm: .autoreply on
.autoreply off | exm: .autoreply off

.autoreplydelay <sec> | exm: .autoreplydelay 5

.setmorning <text>
.setafternoon <text>
.setevening <text>
.setnight <text>

.awhitelist | exm: (reply) .awhitelist
.ablacklist | exm: (reply) .ablacklist
.awhitelistdel | exm: (reply) .awhitelistdel
.ablacklistdel | exm: (reply) .ablacklistdel
""",

"dev": """
.eval <code> | exm: .eval print("hi")
.exec <cmd> | exm: .exec ls
""",

"info": """
.id | exm: .id
.stats | exm: .stats
"""
}

# =====================
# HELP COMMAND
# =====================

@Client.on_message(owner_only & filters.command("help", "."))
async def help_cmd(client, m):
    try:
        await m.delete()
    except:
        pass

    try:
        # .help
        if len(m.command) == 1:
            msg = await m.reply(HELP_MAIN)
            await auto_delete(msg, 40)
            return

        arg = m.command[1].lower()

        # .help all
        if arg == "all":
            text = "ALL COMMANDS\n\n"

            for name, section in HELP_PLUGINS.items():
                text += (
                    "====================\n"
                    f"{name.upper()}\n"
                    "====================\n"
                    f"{section.strip()}\n\n"
                )

            msg = await m.reply(text)
            await auto_delete(msg, 40)
            return

        # .help broken
        if arg == "broken":
            health = get_plugin_health()
            broken = []

            for plugin, info in health.items():
                if info.get("last_error"):
                    broken.append(
                        f"{plugin}\n"
                        f"Error: {info['last_error']}\n"
                        f"Time: {info['last_error_time']}\n"
                    )

            if not broken:
                msg = await m.reply("All plugins are working fine ✅")
            else:
                msg = await m.reply(
                    "BROKEN PLUGINS\n\n" + "\n".join(broken)
                )

            await auto_delete(msg, 10)
            return

        # .help <plugin>
        text = HELP_PLUGINS.get(arg)
        if not text:
            msg = await m.reply("Unknown help section ❌")
        else:
            msg = await m.reply(text)

        await auto_delete(msg, 40)

    except Exception as e:
        await log_error(client, "help.py", e)
