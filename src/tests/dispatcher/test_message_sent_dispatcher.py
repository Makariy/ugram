from dispatcher.dispatchers.message_sent import MessageSentUpdateForm
from forms.message import MessageForm
from dispatcher.dispatchers.message_sent import TOPIC
from dispatcher.interface import Update
import asyncio
import datetime
from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from dispatcher.connection_manager import ConnectionManager
from dispatcher.dispatchers.message_sent import MessageSentDispatcher, MessageSentUpdate
from models.group import Group
from models.user import User
from repository.group import GroupRepository
from repository.user import (
    UserRepository,
)
from tests.dispatcher.connection import TestWebSocketConnection


@dataclass
class CaseData:
    user: User
    group: Group


USERNAME = "TestUser"
PASSWORD = "TestUserPassword"
GROUP_NAME = "Test group"
GROUP_DESCRIPTION = "Test group description"


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session_maker: async_sessionmaker[AsyncSession]):
    async with db_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create_user(USERNAME, PASSWORD)
        assert user is not None 

        group_repo = GroupRepository(session)
        group = await group_repo.create_group(str(user.uuid), GROUP_NAME, GROUP_DESCRIPTION)

    yield CaseData(
        user=user,
        group=group
    )


async def test_message_sent_dispatcher(
    db_session_maker: async_sessionmaker[AsyncSession],
    test_data: CaseData
):
    manager = ConnectionManager()
    dispatcher = MessageSentDispatcher(
        manager,
        db_session_maker
    )

    conn = TestWebSocketConnection()
    await manager.add_connection(UUID(str(test_data.user.uuid)), conn)

    message = MessageForm(
        uuid=uuid4().hex,
        text="This is a test message",
        group_uuid=str(test_data.group.uuid),
        sender_uuid=str(test_data.user.uuid),
        sending_date=datetime.datetime.now(),
        resources=[]
    )

    await dispatcher.dispatch(Update(
        channel=TOPIC,
        data=MessageSentUpdate(
            message=message
        ).model_dump()
    ))
    update = await asyncio.wait_for(conn.send_queue.get(), 1)
    update_form = MessageSentUpdateForm.model_validate_json(update)
    assert update_form.message == message
    

