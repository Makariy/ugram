from typing import Sequence
import datetime 
from models.message import MessageResource
from forms.message import ResourceForm
from models.message import Message
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession


class MessageDeleteException(Exception):
    pass


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_message_by_uuid(self, uuid: str) -> Message | None:
        result = await self._session.execute(
            select(Message). 
                where(Message.uuid == UUID(uuid))
        )
        return result.scalar_one_or_none()

    async def _add_resources_to_message(
        self,
        message: Message,
        resources: list[ResourceForm]
    ):
        for resource in resources:
            self._session.add(
                MessageResource(
                    file_url=resource.file_url,
                    mime_type=resource.mime_type,
                    extra_metadata=resource.extra_metadata,
                    message_uuid=message.uuid
                )
            )

    async def create_message(
        self,
        sender_uuid: str,
        group_uuid: str,
        text: str | None,
        resources: list[ResourceForm] | None
    ) -> Message:
        async with self._session.begin():
            message = Message(
                sender_uuid=UUID(sender_uuid),
                group_uuid=UUID(group_uuid),
                text=text,
                sending_date=datetime.datetime.now()
            )
            self._session.add(message)
            await self._session.flush()

            if resources:
                await self._add_resources_to_message(message, resources)
            await self._session.refresh(message)

        return message

    async def delete_message(self, message_uuid: str) -> None:
        result = await self._session.execute(
            delete(Message).
                where(Message.uuid == UUID(message_uuid))
        )
        if result.rowcount != 1:
            raise MessageDeleteException(f"Message {message_uuid} does not exist")

    async def get_group_messages(
        self,
        group_uuid: str,
        last_sending_date: datetime.datetime | None = None,
        count: int = 50,
    ) -> Sequence[Message]:
        assert count > 0
        if last_sending_date is None:
            last_sending_date = datetime.datetime.now()

        async with self._session.begin():
            result = await self._session.execute(
                select(Message). 
                    where(Message.group_uuid == UUID(group_uuid)). 
                    where(Message.sending_date < last_sending_date).
                    order_by(Message.sending_date.desc()).
                    limit(count)
            )
            messages = result.scalars().all()

        return messages



