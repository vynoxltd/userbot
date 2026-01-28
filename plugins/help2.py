from telethon import events

from userbot import bot
from utils.owner import is_owner
from utils.help_registry import get_all_help
from utils.plugin_status import get_broken_plugins
from utils.logger import log_error
from utils.auto_delete import auto_delete

# =====================
# PLUGIN LOAD MARK
# =====================
print("✔ help2.py loaded")

# =====================
# BUILD MAIN HELP (AUTO)
# =====================
def build_main_help():
    plugins = sorted(get_all_help().keys())

    text = (
        "USERBOT HELP (AUTO)\n\n"
        "Use:\n"
        ".help2 plugin\n\n"
        "Available plugins:\n"
    )

    for p in plugins:
        text += f"• {p}\n"

    text += (
        "\nExtra:\n"
        ".help2 all\n"
        ".help2 broken"
    )

    return text

# =====================
# HELP2 COMMAND
# =====================
@bot.on(events.NewMessage(pattern=r"\.help2(?: (.*))?"))
async def help2_cmd(e):
    if not is_owner(e):
        return

    try:
        try:
            await e.delete()
        except:
            pass

        help_data = get_all_help()
        arg = e.pattern_match.group(1)

        # -----------------
        # .help2
        # -----------------
        if not arg:
            msg = await e.reply(build_main_help())
            await auto_delete(msg, 40)
            return

        arg = arg.lower()

        # -----------------
        # .help2 all
        # -----------------
        if arg == "all":
            text = "ALL COMMANDS\n\n"

            for name, section in help_data.items():
                text += (
                    "====================\n"
                    f"{name.upper()}\n"
                    "====================\n"
                    f"{section.strip()}\n\n"
                )

            msg = await e.reply(text)
            await auto_delete(msg, 40)
            return

        # -----------------
        # .help2 broken
        # -----------------
        if arg == "broken":
            broken = get_broken_plugins()

            if not broken:
                msg = await e.reply("All plugins are working fine ✅")
            else:
                text = "BROKEN PLUGINS\n\n"
                for name, info in broken.items():
                    text += (
                        f"{name}\n"
                        f"Error: {info['error']}\n\n"
                    )
                msg = await e.reply(text)

            await auto_delete(msg, 15)
            return

        # -----------------
        # .help2 plugin
        # -----------------
        text = help_data.get(arg)
        if not text:
            msg = await e.reply("Unknown help section ❌")
        else:
            msg = await e.reply(text)

        await auto_delete(msg, 40)

    except Exception:
        await log_error(bot, "help2.py")