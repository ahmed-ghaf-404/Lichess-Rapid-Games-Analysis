import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "chess-games")

client = MongoClient(MONGO_URL)

db = client[DB_NAME]
games_collection = db["games"]

logging.getLogger(__name__).debug("mongodb.client_created mode=sync database=%s", DB_NAME)
