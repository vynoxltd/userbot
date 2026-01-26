from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import auto_delete, log_error
import asyncio
from plugins.utils import mark_plugin_loaded
mark_plugin_loaded("profilefun.py")

@Client.on_message(owner_only & filters.command(["whoami", "status", "hack"], "."))
async def profile_fun(client, m):
    try:
        # delete command safely
        try:
            await m.delete()
        except:
            pass

        text = None  # ✅ VERY IMPORTANT (default)

        cmd = m.command[0].lower()

        # =====================
        # WHOAMI
        # =====================
        if cmd == "whoami":
            text = (
                f"👤 You are {m.from_user.first_name}\n"
                f"🆔 ID: {m.from_user.id}"
            )

        # =====================
        # STATUS
        # =====================
        elif cmd == "status":
            text = "🟢 Status: Online\n⚡ Power: Unlimited"

        # =====================
        # HACK (reply based)
        # =====================
        elif cmd == "hack":
            if not m.reply_to_message or not m.reply_to_message.from_user:
                warn = await client.send_message(
                    m.chat.id,
                    "Reply to a user to hack 😈"
                )
                await auto_delete(warn, 3)
                return

            user = m.reply_to_message.from_user

            msg = await client.send_message(
                m.chat.id,
                f"💻 Hacking {user.mention}..."
            )
            await asyncio.sleep(1)

            await msg.edit("📂 Accessing files...")
            await asyncio.sleep(1)

            await msg.edit("🔓 Bypassing security...")
            await asyncio.sleep(1)

            await msg.edit("✅ Hack completed 😈")
            await auto_delete(msg, 5)
            return  # 🔥 VERY IMPORTANT

        # =====================
        # SEND RESULT
        # =====================
        if not text:
            return

        msg = await client.send_message(m.chat.id, text)
        await auto_delete(msg, 6)

    except Exception as e:
        await log_error(client, "profilefun.py", e)