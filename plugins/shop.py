import asyncio
from telethon import events

from userbot import bot
from utils.help_registry import register_help
from utils.coins_helper import get_coins, spend
from utils.shop_helper import ITEMS
from utils.players_helper import get_player, save_players
from utils.plugin_status import mark_plugin_loaded, mark_plugin_error
from utils.logger import log_error

PLUGIN_NAME = "shop.py"
mark_plugin_loaded(PLUGIN_NAME)

AUTO_DEL = 30  # seconds

# =====================
# AUTO DELETE HELPER
# =====================
async def auto_reply(e, text):
    try:
        await e.delete()  # delete command instantly
    except:
        pass

    m = await e.reply(text)
    await asyncio.sleep(AUTO_DEL)
    await m.delete()

# =====================
# HELP
# =====================
register_help(
    "shop",
    ".coins\n"
    ".shop\n"
    ".buy <item_id>\n"
    ".inventory\n"
    ".use <item_id>\n\n"
    "• One global shop\n"
    "• Minigames + Battle items\n"
)

# =====================
# COINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.coins$"))
async def coins(e):
    c = get_coins(e.sender_id)
    await auto_reply(e, f"💰 **Your Coins:** `{c}`")

# =====================
# SHOP
# =====================
@bot.on(events.NewMessage(pattern=r"\.shop$"))
async def shop(e):
    try:
        text = "🛒 **GLOBAL SHOP** 🛒\n"

        for cat in ["minigame", "battle"]:
            title = "🎮 MINIGAMES ITEMS" if cat == "minigame" else "⚔️ BATTLE ITEMS"
            text += f"\n{title}\n━━━━━━━━━━━━━━━━━━\n"

            for key, item in ITEMS.items():
                if item.get("category") == cat:
                    text += (
                        f"{item['name']}\n"
                        f"🆔 `{key}` | 💰 {item['price']} | ⭐ {item['rarity']}\n"
                    )

                    if item.get("desc"):
                        text += f"📜 {item['desc']}\n"

                    if item.get("ability"):
                        text += "✨ **Abilities:**\n"
                        for ab, val in item["ability"].items():
                            text += f" • `{ab}` → `{val}`\n"

                    text += "\n"

        await auto_reply(e, text)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# BUY ITEM
# =====================
@bot.on(events.NewMessage(pattern=r"\.buy (\w+)$"))
async def buy(e):
    try:
        item_id = e.pattern_match.group(1).lower()
        item = ITEMS.get(item_id)

        if not item:
            await auto_reply(e, "❌ Item not found")
            return

        price = item["price"]

        if not spend(e.sender_id, price):
            await auto_reply(e, "❌ Not enough coins")
            return

        data, player = get_player(e.sender_id, e.sender.first_name)
        inv = player.setdefault("items", {})
        inv[item_id] = inv.get(item_id, 0) + 1
        save_players(data)

        await auto_reply(
            e,
            f"✅ **Item Purchased!**\n\n"
            f"{item['name']}\n"
            f"💰 Spent: `{price}`\n"
            f"🎒 Added to inventory"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
