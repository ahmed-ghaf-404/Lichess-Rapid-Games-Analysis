import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "chessdb")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

games_collection = db["games"]
