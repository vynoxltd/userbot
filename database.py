from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client.userbot

settings = db.settings
storage = db.storage