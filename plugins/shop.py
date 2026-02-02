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

# =====================
# HELP
# =====================
register_help(
    "shop",
    ".coins\n"
    ".shop\n"
    ".buy <item_id>\n"
    ".inventory\n\n"
    "• One global shop\n"
    "• Minigames + Battle items\n"
)

# =====================
# COINS
# =====================
@bot.on(events.NewMessage(pattern=r"\.coins$"))
async def coins(e):
    c = get_coins(e.sender_id)
    await e.reply(f"💰 **Your Coins:** `{c}`")

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
                        f"🆔 `{key}` | 💰 {item['price']} | ⭐ {item['rarity']}\n\n"
                    )

        await e.reply(text)

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
            await e.reply("❌ Item not found")
            return

        price = item["price"]

        if not spend(e.sender_id, price):
            await e.reply("❌ Not enough coins")
            return

        data, player = get_player(e.sender_id, e.sender.first_name)

        inv = player.setdefault("items", {})
        inv[item_id] = inv.get(item_id, 0) + 1

        save_players(data)

        await e.reply(
            f"✅ **Item Purchased!**\n\n"
            f"{item['name']}\n"
            f"💰 Spent: `{price}`\n"
            f"🎒 Added to inventory"
        )

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)

# =====================
# INVENTORY
# =====================
@bot.on(events.NewMessage(pattern=r"\.inventory$"))
async def inventory(e):
    try:
        _, player = get_player(e.sender_id, e.sender.first_name)
        items = player.get("items", {})

        if not items:
            await e.reply("🎒 Inventory empty")
            return

        text = "🎒 **YOUR INVENTORY**\n\n"
        for k, v in items.items():
            item = ITEMS.get(k)
            if item:
                text += f"{item['name']} ×{v}\n"

        await e.reply(text)

    except Exception as ex:
        mark_plugin_error(PLUGIN_NAME, ex)
        await log_error(bot, PLUGIN_NAME, ex)
