import json
import os

INV_FILE = "utils/inventory.json"

def load_inv():
    if not os.path.exists(INV_FILE):
        return {}
    with open(INV_FILE, "r") as f:
        return json.load(f)

def save_inv(data):
    with open(INV_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_item(user_id, item_id, qty=1):
    data = load_inv()
    uid = str(user_id)
    data.setdefault(uid, {})
    data[uid][item_id] = data[uid].get(item_id, 0) + qty
    save_inv(data)

def get_inventory(user_id):
    data = load_inv()
    return data.get(str(user_id), {})
