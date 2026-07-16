from app.db.mongodb import get_database
from app.repositories.base import BaseRepository


class RouteRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_database()["routes"])

    async def create(self, route_doc: dict):
        return await self.insert_one(route_doc)

    async def list_all(self) -> list[dict]:
        return [doc async for doc in self.collection.find()]

    async def list_by_driver(self, driver_id: str) -> list[dict]:
        return [doc async for doc in self.collection.find({"assigned_driver_id": driver_id})]
