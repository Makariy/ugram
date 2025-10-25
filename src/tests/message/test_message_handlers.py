import datetime 
from forms.message import ResourceForm
from models.group import Group
from forms.group import GroupForm
from auth.services.request import AUTH_COOKIE_TOKEN_KEY
from repository.group import GroupRepository
from dataclasses import dataclass

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.user import User
from repository.user import UserRepository


@dataclass
class CaseData:
    user: User
    group: Group
    user_repo: UserRepository
    group_repo: GroupRepository


USERNAME = "TestUser"
PASSWORD = "UserPassword"
GROUP_NAME = "GroupName"
GROUP_DESCRIPTION = "Group description"


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user(USERNAME, PASSWORD)
    assert user is not None 

    group_repo = GroupRepository(db_session)
    group = await group_repo.create_group(str(user.uuid), GROUP_NAME, GROUP_DESCRIPTION)

    yield CaseData(
        user_repo=user_repo,
        group_repo=group_repo,
        user=user,
        group=group
    )


# TODO: Make common for all the tests 
@pytest.fixture(scope="function")
async def logged_http_client(
    http_client: AsyncClient,
    test_data: CaseData
):
    response = await http_client.post("/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    token = response.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    assert token 
    yield http_client


async def test_send_message_without_resources(
    test_data: CaseData,
    logged_http_client: AsyncClient
):
    message_text = "Test message text"
    response = await logged_http_client.post(
        f"/message/{str(test_data.group.uuid)}/send",
        json={
            "text": message_text,
        }   
    )

    assert response.status_code == 201
    data = response.json()
    assert data.get("text") == message_text
    assert data.get("group_uuid") == str(test_data.group.uuid)
    assert data.get("sender_uuid") == str(test_data.user.uuid)
    assert data.get("resources") == []

        
async def test_send_message_with_resources(
    test_data: CaseData,
    logged_http_client: AsyncClient
):
    message_text = "Test message text"
    resource_file_url = "https://data.messenger.com/images/image.png"
    resource_mime_type = "image/png"
    resource_extra_metadata = {
        "width": 200,
        "height": 100
    }
    resources = ResourceForm(
        file_url=resource_file_url,
        mime_type=resource_mime_type,
        extra_metadata=resource_extra_metadata
    )
    response = await logged_http_client.post(
        f"/message/{str(test_data.group.uuid)}/send",
        json={
            "text": message_text,
            "resources": [resources.model_dump()]
        }   
    )

    assert response.status_code == 201
    data = response.json()
    assert data.get("text") == message_text
    assert data.get("group_uuid") == str(test_data.group.uuid)
    assert data.get("sender_uuid") == str(test_data.user.uuid)

    resources = data.get("resources")
    assert resources  
    assert len(resources) == 1 

    resource = resources[0]
    assert resource.get("file_url") == resource_file_url
    assert resource.get("mime_type") == resource_mime_type
    assert resource.get("extra_metadata") == resource_extra_metadata



async def test_get_messages(
    test_data: CaseData,
    logged_http_client: AsyncClient
):
    last_sending_date: datetime.datetime | None = None
    for i in range(10):
        message_send_response = await logged_http_client.post(
            f"/message/{str(test_data.group.uuid)}/send",
            json={
                "text": str(i),
                "resources": []
            }   
        )
        assert message_send_response.status_code == 201
        if i == 5:
            last_sending_date = datetime.datetime.fromisoformat(
                message_send_response.json().get("sending_date")
            )

    assert last_sending_date is not None 

    response = await logged_http_client.get(
        f"/message/messages?group_uuid={test_data.group.uuid}"
    )
    assert response.status_code == 200
    data = response.json()

    assert "messages" in data 
    messages = data.get("messages")
    assert len(messages) == 10 

    last_message_text = 9
    for message in messages:
        assert message.get("text") == str(last_message_text)
        last_message_text -= 1


    # Paginating from the middle message
    paginated_response = await logged_http_client.get(
        f"/message/messages?group_uuid={test_data.group.uuid}&last_sending_date={last_sending_date.timestamp()}",
    )

    assert paginated_response.status_code == 200
    data = paginated_response.json()

    assert "messages" in data 
    messages = data.get("messages")
    assert len(messages) == 5

    last_message_text = 4
    for message in messages:
        assert message.get("text") == str(last_message_text)
        last_message_text -= 1


