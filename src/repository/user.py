from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.user import User
from auth.services.hash import hash_user_password


class UserDeleteException(Exception):
    pass


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_uuid(self, uuid: str) -> User | None:
        result = await self._session.execute(select(User).where(User.uuid == uuid))
        return result.scalar_one_or_none()

    async def create_user(self, username: str, password: str) -> User | None:
        async with self._session.begin():
            existing_user = await self.get_user_by_username(username)
            if existing_user is not None:
                return None 

            user = User(username=username, password_hash=hash_user_password(password))
            self._session.add(user)

            await self._session.flush()
            return user

    async def delete_user_by_uuid(self, str_uuid: str) -> None:
        uuid = UUID(str_uuid)
        result = await self._session.execute(delete(User).where(User.uuid == uuid))
        if result.rowcount != 1:
            raise UserDeleteException(
                f"Deleted unexpected amount of users: {result.rowcount}"
            )

        return

