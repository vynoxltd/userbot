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
# MAIN HELP (SHORT)
# =====================
HELP_MAIN = """
USERBOT HELP

Use:
.help (plugin)

Available plugins:
basic
cleanup
spam
forward
notes
media
games
fun
random
mention
info

Extra:
.help all
.help broken
.help2
.help3
"""

# =====================
# FULL HELP DATA
# =====================
HELP_PLUGINS = {

"basic": """
Basic Commands
.alive  | exm: .alive
.ping   | exm: .ping
.restart| exm: .restart
""",

"cleanup": """
Cleanup
.purge     | exm: .purge (reply)
.clean     | exm: .clean 10
.del       | exm: .del (reply)
.delall    | exm: .delall (reply user)
""",

"spam": """
Spam
.spam        | exm: .spam 5 hello
.delayspam  | exm: .delayspam 5 1.5 hi
.replyspam  | exm: .replyspam 10 (reply)
""",

"forward": """
Forward
.fwd        | exm: .fwd -100123456
.sfwd       | exm: .sfwd -100123456
.fwdhere    | exm: .fwdhere (reply)
.mfwd       | exm: .mfwd -100123456 5
""",

"notes": """
Notes
.setnote    | exm: .setnote test hello
.getnote    | exm: .getnote test
.delnote    | exm: .delnote test
""",

"media": """
Media
.ss     | exm: .ss (reply view-once)
.save   | exm: .save (reply)
""",

"games": """
Games
.dice   | Roll dice (1–6)
.coin   | Head / Tail
.luck   | Luck percentage
.rate   | Rate something
.roll   | exm: .roll 100
""",

"fun": """
Fun Actions
.slap   | Slap someone (reply / mention)
.hug    | Hug someone
.kiss   | Kiss someone
.poke   | Poke someone
.tickle| Tickle someone
""",

"random": """
Random Fun
.predict     | Yes / No prediction
.8ball       | Magic 8 ball
.truth       | Truth question
.dare        | Dare challenge
.joke        | Random joke
.quote       | Random quote
.insult      | Insult user
.compliment  | Compliment user
""",

"mention": """
Mention
.mention | exm: .mention Hello everyone

• Mentions recent chat users
• Admin = more mentions
""",

"info": """
Info
.id     | Get user / chat ID
.stats  | Profile stats
"""
}

# =====================
# HELP COMMAND
# =====================
@Client.on_message(owner_only & filters.command("help", "."))
async def help_cmd(client, m):
    try:
        try:
            await m.delete()
        except:
            pass

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
                msg = await m.reply("✅ All plugins are working fine")
            else:
                msg = await m.reply("🚨 BROKEN PLUGINS\n\n" + "\n".join(broken))

            await auto_delete(msg, 15)
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
