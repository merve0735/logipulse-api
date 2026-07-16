from app.db.mongodb import get_database
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(get_database()["users"])

    async def get_by_email(self, email: str):
        return await self.find_one({"email": email})

    async def create(self, user_doc: dict):
        return await self.insert_one(user_doc)
