from repository.group import GroupRepository
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from typing import override

from uuid import UUID
from loguru import logger
from pydantic import ValidationError
from pydantic.main import BaseModel

from dispatcher.connection_manager import ConnectionManager
from dispatcher.interface import IUpdateDispatcher, Update
from forms.message import MessageForm


TOPIC = "message_sent"


class MessageSentUpdate(BaseModel):
    message: MessageForm



class MessageSentUpdateForm(BaseModel):
    type: str = "MESSAGE_SENT"
    message: MessageForm


class MessageSentDispatcher(IUpdateDispatcher):
    def __init__(
        self,
        manager: ConnectionManager,
        db_session_maker: async_sessionmaker[AsyncSession]
    ):
        self._manager = manager
        self._db_session_maker = db_session_maker

    @override
    async def dispatch(self, update: Update) -> None:
        try:
            data = MessageSentUpdate(**update.data)
        except ValidationError as e:
            logger.error(f"Could not construct MessageSentUpdate: {e}")
            return 
        
        await self._dispatch(data)

    async def _dispatch(self, update: MessageSentUpdate) -> None:
        async with self._db_session_maker() as session:
            group_repo = GroupRepository(session)
            users_to_roles = await group_repo.get_group_members(update.message.group_uuid)

        for user in users_to_roles.keys():
            await self._try_send_message_update(
                UUID(str(user.uuid)),
                update.message
            )

    async def _try_send_message_update(self, user_uuid: UUID, message: MessageForm) -> None:
        try:
            conn = await self._manager.get_connection_by_user_uuid(user_uuid)
            if conn is None:
                return 

            await conn.send(
                MessageSentUpdateForm(message=message).model_dump_json().encode()
            )
        except Exception as e:
            logger.error(f"Got an error sending update to user {user_uuid=}: {e}")


