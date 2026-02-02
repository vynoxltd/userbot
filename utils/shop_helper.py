# utils/shop_helper.py

ITEMS = {
    # =====================
    # COMMON ITEMS
    # =====================
    "wood_sword": {
        "name": "🪵 Wood Sword",
        "price": 50,
        "rarity": "common",
        "attack": 5,
        "defense": 0,
        "hp": 0,
        "consumable": False
    },
    "iron_sword": {
        "name": "⚔️ Iron Sword",
        "price": 120,
        "rarity": "common",
        "attack": 10,
        "defense": 0,
        "hp": 0,
        "consumable": False
    },
    "iron_shield": {
        "name": "🛡 Iron Shield",
        "price": 80,
        "rarity": "common",
        "attack": 0,
        "defense": 8,
        "hp": 0,
        "consumable": False
    },

    # =====================
    # RARE ITEMS
    # =====================
    "steel_sword": {
        "name": "🗡 Steel Sword",
        "price": 200,
        "rarity": "rare",
        "attack": 15,
        "defense": 2,
        "hp": 0,
        "consumable": False
    },
    "golden_armor": {
        "name": "🥋 Golden Armor",
        "price": 220,
        "rarity": "rare",
        "attack": 0,
        "defense": 15,
        "hp": 10,
        "consumable": False
    },

    # =====================
    # LEGENDARY ITEMS
    # =====================
    "diamond_sword": {
        "name": "💎 Diamond Sword",
        "price": 400,
        "rarity": "legendary",
        "attack": 25,
        "defense": 5,
        "hp": 0,
        "consumable": False
    },
    "dragon_blade": {
        "name": "🐉 Dragon Blade",
        "price": 600,
        "rarity": "legendary",
        "attack": 35,
        "defense": 10,
        "hp": 0,
        "consumable": False
    },

    # =====================
    # CONSUMABLES
    # =====================
    "health_potion": {
        "name": "🧪 Health Potion",
        "price": 30,
        "rarity": "common",
        "attack": 0,
        "defense": 0,
        "hp": 30,
        "consumable": True
    },
    "mega_potion": {
        "name": "💊 Mega Potion",
        "price": 80,
        "rarity": "rare",
        "attack": 0,
        "defense": 0,
        "hp": 70,
        "consumable": True
    }
}
