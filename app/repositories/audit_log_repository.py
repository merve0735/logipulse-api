from app.db.mongodb import get_database
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_database()["audit_logs"])

    async def create(self, log_doc: dict):
        return await self.insert_one(log_doc)

    async def find_filtered(self, query: dict, limit: int, offset: int) -> tuple[list[dict], int]:
        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        items = [doc async for doc in cursor]
        return items, total
