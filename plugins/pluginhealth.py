from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    get_plugin_health,
    auto_delete,
    mark_plugin_loaded
)

# 🔥 mark this plugin as loaded
mark_plugin_loaded("pluginhealth.py")


@Client.on_message(owner_only & filters.command("plugins", "."))
async def plugin_health_cmd(client, m):
    try:
        await m.delete()
    except:
        pass

    data = get_plugin_health()

    if not data:
        msg = await client.send_message(
            m.chat.id,
            "No plugin health data available"
        )
        await auto_delete(msg, 5)
        return

    text = "PLUGIN HEALTH STATUS\n\n"

    for plugin, info in data.items():
        if info.get("last_error"):
            text += (
                f"❌ {plugin}\n"
                f"   Error: {info['last_error']}\n"
                f"   Time: {info['last_error_time']}\n\n"
            )
        else:
            text += f"✅ {plugin}\n"

    msg = await client.send_message(m.chat.id, text)
    await auto_delete(msg, 25)