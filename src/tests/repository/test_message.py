from forms.message import ResourceForm
import datetime 
from typing import cast
from repository.message import MessageRepository
from models.group import Group
from dataclasses import dataclass

from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.group import GroupRole
from models.user import User
from repository.group import GroupRepository
from repository.user import UserRepository


@dataclass
class CaseData:
    user_repo: UserRepository
    group_repo: GroupRepository
    message_repo: MessageRepository

    first_user: User 
    second_user: User

    group: Group


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    group_name = "TestGroup"
    group_description = "TestGroup description"

    first_username = "FirstUser"
    first_password = "FirstUserPassword"
    second_username = "SecondUser"
    second_password = "SecondUserPassword"

    user_repo = UserRepository(db_session)
    
    first_user = await user_repo.create_user(first_username, first_password)
    second_user = await user_repo.create_user(second_username, second_password)
    assert first_user
    assert second_user

    group_repo = GroupRepository(db_session)
    group = await group_repo.create_group(
        creator_uuid=str(first_user.uuid),
        name=group_name,
        description=group_description
    )

    message_repo = MessageRepository(db_session)

    yield CaseData(
        first_user=first_user,
        second_user=second_user,
        group=group,
        user_repo=user_repo,
        group_repo=group_repo,
        message_repo=message_repo
    )


async def test_create_message(test_data: CaseData):
    file_url = "https://data.messenger.com/images/image.jpeg"
    mime_type = "image/jpeg"
    extra_metadata = {
        "width": "100",
        "height": "200"
    }

    resource = ResourceForm(
        file_url=file_url,
        mime_type=mime_type,
        extra_metadata=extra_metadata
    )
    text = "Test message text"

    message = await test_data.message_repo.create_message(
        sender_uuid=str(test_data.first_user.uuid),
        group_uuid=str(test_data.group.uuid),
        text=text,
        resources=[resource]
    )

    assert message.group == test_data.group
    assert message.sender == test_data.first_user
    assert message.text == text

    resources = message.resources
    assert len(resources) == 1
    resource = resources[0]
    assert resource.file_url == file_url
    assert resource.mime_type == mime_type
    assert resource.extra_metadata == extra_metadata


async def test_get_messages(test_data: CaseData):
    for i in range(10):
        await test_data.message_repo.create_message(
            sender_uuid=str(test_data.first_user.uuid),
            group_uuid=str(test_data.group.uuid),
            text=str(i),
            resources=None 
        )

    last_messages = await test_data.message_repo.get_group_messages(
        group_uuid=str(test_data.group.uuid),
        count=5,
    )
    last_num = 9
    for message in last_messages:
        assert message.text == str(last_num)
        assert message.sender_uuid == test_data.first_user.uuid
        assert message.group_uuid == test_data.group.uuid
        assert len(message.resources) == 0
        last_num -= 1

    first_messages = await test_data.message_repo.get_group_messages(
        group_uuid=str(test_data.group.uuid),
        count=6,
        last_sending_date=cast(datetime.datetime, message.sending_date)
    )

    for message in first_messages:
        assert message.text == str(last_num)
        assert message.sender_uuid == test_data.first_user.uuid
        assert message.group_uuid == test_data.group.uuid
        assert len(message.resources) == 0
        last_num -= 1


async def test_get_messages_with_resources(test_data: CaseData):
    first_file_url = "https://data.messenger.com/images/first_image.png"
    first_mime_type = "image/png"
    first_extra_metadata = {
        "width": "100",
        "height": "200"
    }
    first_resource = ResourceForm(
        file_url=first_file_url,
        mime_type=first_mime_type,
        extra_metadata=first_extra_metadata
    )

    second_file_url = "https://data.messenger.com/images/second_image.jpeg"
    second_mime_type = "image/jpeg"
    second_extra_metadata = {
        "width": "300",
        "height": "400"
    }
    second_resource = ResourceForm(
        file_url=second_file_url,
        mime_type=second_mime_type,
        extra_metadata=second_extra_metadata
    )
    await test_data.message_repo.create_message(
        sender_uuid=str(test_data.second_user.uuid),
        group_uuid=str(test_data.group.uuid),
        text="Test message with resources",
        resources=[first_resource, second_resource]
    )

    messages = await test_data.message_repo.get_group_messages(
        group_uuid=str(test_data.group.uuid),
        count=100
    )

    assert len(messages) == 1 
    message_resources = messages[0].resources 

    assert len(message_resources) == 2 

    first_resource = message_resources[0]
    second_resource = message_resources[1]
    assert first_resource.file_url == first_file_url
    assert first_resource.mime_type == first_mime_type
    assert first_resource.extra_metadata == first_extra_metadata
    assert second_resource.file_url == second_file_url
    assert second_resource.mime_type == second_mime_type
    assert second_resource.extra_metadata == second_extra_metadata
    

