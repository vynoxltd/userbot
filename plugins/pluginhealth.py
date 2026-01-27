from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    get_plugin_health,
    auto_delete,
    mark_plugin_loaded,
    mark_plugin_error,
    log_error,
    register_help
)

# 🔥 mark this plugin as loaded
mark_plugin_loaded("pluginhealth.py")

# 🔥 auto help registration (help4.py)
register_help(
    "pluginhealth",
    """
.plugins
exm: .plugins

• Shows health status of all plugins
• ❌ = plugin has error
• ✅ = plugin working fine
• Shows last error + time if failed
"""
)


@Client.on_message(owner_only & filters.command("plugins", "."))
async def plugin_health_cmd(client: Client, m):
    try:
        data = get_plugin_health()

        if not data:
            msg = await m.reply("No plugin health data available")
            await auto_delete(msg, 5)
            return

        text = "🩺 PLUGIN HEALTH STATUS\n\n"

        for plugin, info in data.items():
            if info.get("last_error"):
                text += (
                    f"❌ {plugin}\n"
                    f"   Error: {info['last_error']}\n"
                    f"   Time: {info['last_error_time']}\n\n"
                )
            else:
                text += f"✅ {plugin}\n"

        msg = await m.reply(text)
        await auto_delete(msg, 25)

        # delete command LAST
        try:
            await m.delete()
        except:
            pass

    except Exception as e:
        mark_plugin_error("pluginhealth.py", e)
        await log_error(client, "pluginhealth.py", e)
