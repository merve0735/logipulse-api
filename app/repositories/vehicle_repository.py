from app.db.mongodb import get_database
from app.repositories.base import BaseRepository


class VehicleRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_database()["vehicles"])

    async def create(self, vehicle_doc: dict):
        return await self.insert_one(vehicle_doc)

    async def get_by_plate_number(self, plate_number: str):
        return await self.find_one({"plate_number": plate_number})

    async def list_all(self) -> list[dict]:
        return [doc async for doc in self.collection.find()]
