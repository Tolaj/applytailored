from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME

db_client = None
db = None


async def connect_db():
    global db_client, db
    db_client = AsyncIOMotorClient(MONGO_URI)
    db = db_client[DB_NAME]
    print("✓ Connected to MongoDB")


async def close_db():
    global db_client
    if db_client:
        db_client.close()
        print("✓ MongoDB connection closed")
