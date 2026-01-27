from pyrogram import Client, filters
from plugins.owner import owner_only
from plugins.utils import (
    auto_delete,
    mark_plugin_loaded,
    mark_plugin_error,
    log_error,
    register_help
)

# =====================
# PLUGIN LOAD (HEALTH)
# =====================
mark_plugin_loaded("explain.py")

# =====================
# HELP4 AUTO REGISTER
# =====================
register_help(
    "explain",
    """
.explain <topic>

Examples:
.explain autoreply
.explain spam
.explain vars
.explain botmanager

• Simple explanation
• Beginner friendly
"""
)

# =====================
# EXPLANATION DATA
# =====================
EXPLAIN_DATA = {

    "autoreply": """
🤖 AUTO REPLY – SIMPLE EXPLANATION

Auto reply private messages ke liye hota hai.

MAIN COMMANDS
.autoreply on
→ Auto reply enable

.autoreply off
→ Auto reply disable

.autoreplydelay 5
→ Reply bhejne se pehle 5 sec wait

TIME BASED MESSAGES
.setmorning text
.setafternoon text
.setevening text
.setnight text
→ Time ke hisaab se reply change hota hai

WHITELIST / BLACKLIST
.awhitelist
→ Reply sirf is user ko (reply karke)

.awhitelistdel
→ User ko whitelist se hatao

.ablacklist
→ Is user ko kabhi reply nahi jayega

.ablacklistdel
→ Blacklist se remove

IMPORTANT RULES
• Whitelist active → reply sirf whitelist users ko
• Blacklist ka priority sabse zyada
• Messages vars.json me save hote hain
""",

    "whitelist": """
🟢 WHITELIST – KYA HAI?

Whitelist ka matlab:
→ Auto reply sirf selected users ko

Use tab hota hai jab:
• Sabko reply nahi chahiye
• Sirf important logon ko reply chahiye

Use:
Reply karke .awhitelist
Remove: .awhitelistdel
""",

    "blacklist": """
🔴 BLACKLIST – KYA HAI?

Blacklist ka matlab:
→ Is user ko kabhi auto reply nahi

Use:
Reply karke .ablacklist
Remove: .ablacklistdel

NOTE:
Agar user whitelist + blacklist dono me ho
→ ❌ Reply nahi jayega
""",

    "botmanager": """
🤖 BOT MANAGER – SIMPLE GUIDE

.addbot spam TOKEN
→ Bot token save karta hai

.startbot spam
→ Bot start karta hai

.stopbot spam
→ Bot band karta hai

.delbot spam
→ Bot remove

.bots
→ Running bots list

NOTE:
'name' sirf ek label hota hai
(token same reh sakta hai)
""",

    "vars": """
📦 VARS SYSTEM – KYA KAAM HAI?

Vars = permanent storage

.setvar KEY VALUE
→ Value save

.getvar KEY
→ Value dekho

.delvar KEY
→ Delete

.vars
→ Sab keys list

USE CASE:
• autoreply messages
• bot tokens
• settings save
""",

    "spam": """
📢 SPAM – KYA KARTA HAI?

Spam commands repeated messages bhejte hain.

.spam 5 hello
→ 5 baar hello

.delayspam 5 1.5 hi
→ 5 messages, har 1.5 sec baad

.replyspam 10
→ Replied message 10 baar

NOTE:
• Flood control ka dhyan rakho
• Zyada spam se account restrict ho sakta hai
""",

    "cleanup": """
🧹 CLEANUP – MESSAGES DELETE

.purge
→ Reply se neeche sab delete

.clean 10
→ Last 10 messages delete

.del
→ Replied message delete

.delall
→ Replied user ke sab messages delete

NOTE:
• Mostly groups ke liye useful
""",

    "notes": """
📝 NOTES – TEXT SAVE SYSTEM

.setnote name text
→ Note save

.getnote name
→ Note fetch

.delnote name
→ Note delete

USE CASE:
• Repeated replies
• Templates
• Info store
""",

    "media": """
📂 MEDIA TOOLS

.ss
→ View-once / self-destruct media save

.save
→ Normal media save (reply karke)

NOTE:
• Media Saved Messages me jata hai
• Disk clean se temp files delete ho sakti hain
""",

    "mention": """
📣 MENTION – MASS TAG

.mention Hello
→ Recent users ko tag karta hai

RULES:
• Admin ho → zyada mentions
• Normal user → limited mentions
""",

    "random": """
🎲 RANDOM – FUN COMMANDS

.predict
→ Yes / No type answer

.8ball
→ Magic 8 ball

.truth / .dare
→ Fun questions

.joke / .quote
→ Random joke / quote

.insult / .compliment
→ User ke sath fun
""",

    "games": """
🎮 GAMES – MINI FUN

.dice
→ Dice roll (1–6)

.coin
→ Head / Tail

.luck
→ Luck percentage

.rate
→ Random rating

.roll 100
→ 1 se 100 ke beech number
""",

    "basic": """
⚙️ BASIC COMMANDS

.alive
→ Bot zinda hai ya nahi

.ping
→ Response test

.restart
→ Userbot restart

.id
→ User / chat ID

.stats
→ Profile stats + uptime
"""
}

# =====================
# EXPLAIN COMMAND
# =====================
@Client.on_message(owner_only & filters.command("explain", "."))
async def explain_cmd(client: Client, m):
    try:
        try:
            await m.delete()
        except:
            pass

        if len(m.command) < 2:
            msg = await m.reply(
                "Usage:\n.explain autoreply\n.explain spam\n.explain vars\n.explain botmanager"
            )
            return await auto_delete(msg, 8)

        key = m.command[1].lower()
        text = EXPLAIN_DATA.get(key)

        if not text:
            msg = await m.reply("❌ No explanation found for this topic")
        else:
            msg = await m.reply(text)

        await auto_delete(msg, 30)

    except Exception as e:
        mark_plugin_error("explain.py", e)
        await log_error(client, "explain.py", e)
