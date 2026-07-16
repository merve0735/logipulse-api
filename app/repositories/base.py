from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorCollection


class BaseRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_one(self, query: dict) -> Optional[dict]:
        return await self.collection.find_one(query)

    async def insert_one(self, document: dict) -> Any:
        result = await self.collection.insert_one(document)
        return result.inserted_id
