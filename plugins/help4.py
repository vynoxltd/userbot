from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    get_plugin_health,
    get_all_help,          # 🔥 AUTO HELP REGISTRY
    mark_plugin_loaded,
    log_error
)

# 🔥 mark plugin loaded
mark_plugin_loaded("help4.py")


# =====================
# BUILD MAIN HELP (AUTO)
# =====================
def build_main_help():
    plugins = sorted(get_all_help().keys())

    text = (
        "USERBOT HELP\n\n"
        "Use:\n"
        ".help <plugin>\n\n"
        "Available plugins:\n"
    )

    for p in plugins:
        text += f"• {p}\n"

    text += (
        "\nExtra:\n"
        ".help all\n"
        ".help broken\n"
    )

    return text


# =====================
# HELP COMMAND
# =====================
@Client.on_message(owner_only & filters.command("help", "."))
async def help_cmd(client: Client, m):
    try:
        await m.delete()
    except:
        pass

    try:
        help_data = get_all_help()

        # -----------------
        # .help
        # -----------------
        if len(m.command) == 1:
            msg = await m.reply(build_main_help())
            await auto_delete(msg, 40)
            return

        arg = m.command[1].lower()

        # -----------------
        # .help all
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

            msg = await m.reply(text)
            await auto_delete(msg, 40)
            return

        # -----------------
        # .help broken
        # -----------------
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

            await auto_delete(msg, 15)
            return

        # -----------------
        # .help <plugin>
        # -----------------
        text = help_data.get(arg)
        if not text:
            msg = await m.reply("Unknown help section ❌")
        else:
            msg = await m.reply(text)

        await auto_delete(msg, 40)

    except Exception as e:
        await log_error(client, "help4.py", e)
