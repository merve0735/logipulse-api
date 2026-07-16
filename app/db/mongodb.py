from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
    await mongodb.client[settings.MONGO_DB_NAME]["users"].create_index("email", unique=True)


async def close_mongo_connection() -> None:
    mongodb.client.close()


def get_database():
    return mongodb.client[settings.MONGO_DB_NAME]
