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
.explain (topic)

Examples:
.explain autoreply
.explain spam
.explain spambot
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

    "spambot": """
🤖 SPAMBOT – FULL EXPLANATION

SpamBot ek **separate bot** hota hai
jo groups me automatic spam karta hai.

BASIC CONTROL
.spambot on
→ Spam bot enable

.spambot off
→ Spam bot disable

.spambot stop
→ Chal raha spam turant band

NORMAL SPAM
.spambot 10
→ Isi group me 10 messages spam

TARGET GROUP SPAM
.spambot 20 -1001234567890
→ Specific group ID me spam

.spambot 15 @groupusername
→ Username wale group me spam

REPLY BASED SPAM
(reply) .spambot 10
→ Jis message par reply kiya hai
usi user ko spam replies

IMPORTANT POINTS
• Ek time par ek spam run hota hai
• Flood limit ka dhyan rakho
• Bot spam karta hai, user ID safe rehti hai
• Messages auto delete hote hain (50 sec)
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
📢 USERBOT SPAM – BASIC SPAM

.spam 5 hello
→ 5 baar message

.delayspam 5 1.5 hi
→ Delay ke sath spam

.replyspam 10
→ Replied message spam

NOTE:
• Ye userbot spam hai
• Account restriction ka risk hota hai
""",

    "cleanup": """
🧹 CLEANUP – MESSAGE DELETE

.purge
→ Reply se neeche sab delete

.clean 10
→ Last 10 messages delete

.del
→ Replied message delete

.delall
→ Replied user ke sab messages delete
""",

    "notes": """
📝 NOTES – TEXT SAVE SYSTEM

.setnote name text
→ Note save

.getnote name
→ Note fetch

.delnote name
→ Note delete
""",

    "media": """
📂 MEDIA TOOLS

.ss
→ View-once media save

.save
→ Normal media save

NOTE:
Saved Messages me jata hai
""",

    "mention": """
📣 MENTION – MASS TAG

.mention Hello
→ Recent users ko tag

Admin = zyada mentions
""",

    "random": """
🎲 RANDOM – FUN COMMANDS

.predict
.8ball
.truth / .dare
.joke / .quote
.insult / .compliment
""",

    "games": """
🎮 GAMES – MINI FUN

.dice
.coin
.luck
.rate
.roll 100
""",

    "basic": """
⚙️ BASIC COMMANDS

.alive
.ping
.restart
.id
.stats
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
                "Usage:\n.explain autoreply\n.explain spambot\n.explain vars"
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
