from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.base import BaseRepository


class RouteRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_database()["routes"])

    async def create(self, route_doc: dict):
        return await self.insert_one(route_doc)

    async def get_by_id(self, route_id: str):
        return await self.find_one({"_id": ObjectId(route_id)})

    async def list_all(self) -> list[dict]:
        return [doc async for doc in self.collection.find()]

    async def list_by_driver(self, driver_id: str) -> list[dict]:
        return [doc async for doc in self.collection.find({"assigned_driver_id": driver_id})]

    async def assign_driver(self, route_id: str, driver_id: str) -> int:
        return await self.update_one({"_id": ObjectId(route_id)}, {"assigned_driver_id": driver_id})

    async def update_status(self, route_id: str, status: str) -> int:
        return await self.update_one({"_id": ObjectId(route_id)}, {"status": status})
