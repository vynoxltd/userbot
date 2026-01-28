# database/notes.py

from utils.mongo import db

# Mongo collection
_notes = db["notes"]

# =====================
# SET NOTE
# =====================
def set_note(name: str, text: str):
    _notes.update_one(
        {"_id": name},
        {"$set": {"text": text}},
        upsert=True
    )

# =====================
# GET NOTE
# =====================
def get_note(name: str):
    data = _notes.find_one({"_id": name})
    if not data:
        return None
    return data.get("text")

# =====================
# DELETE NOTE
# =====================
def del_note(name: str):
    _notes.delete_one({"_id": name})

# =====================
# LIST ALL NOTES
# =====================
def all_notes():
    notes = {}
    for x in _notes.find():
        notes[x["_id"]] = x.get("text")
    return notes
