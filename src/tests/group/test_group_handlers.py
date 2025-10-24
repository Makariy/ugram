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
    user_repo: UserRepository
    group_repo: GroupRepository


USERNAME = "TestUser"
PASSWORD = "UserPassword"
GROUP_NAME = "GroupName"
GROUP_DESCRIPTION = "Group description"


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create_user(USERNAME, PASSWORD)
    assert user is not None 

    yield CaseData(
        group_repo=GroupRepository(db_session),
        user_repo=repo,
        user=user
    )


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


async def _test_group_create_correct(response: Response, name: str, description: str):
    assert response.status_code == 201
    
    data = response.json()

    assert data.get("name") == name
    assert data.get("description") == description


async def test_create_group(
    logged_http_client: AsyncClient,
    test_data: CaseData
):
    response = await logged_http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )

    await _test_group_create_correct(response, GROUP_NAME, GROUP_DESCRIPTION)


async def test_get_group_members(
    logged_http_client: AsyncClient,
    test_data: CaseData
):
    response = await logged_http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )

    await _test_group_create_correct(response, GROUP_NAME, GROUP_DESCRIPTION)

    group_uuid = response.json()["uuid"]
    members_response = await logged_http_client.get(
        f"/group/members?group_uuid={group_uuid}"
    )

    assert members_response.status_code == 200 

    data = members_response.json()
    assert "group" in data 
    assert "users" in data 
    
    group = data["group"]
    assert group.get("name") == GROUP_NAME
    assert group.get("description") == GROUP_DESCRIPTION
    assert group.get("uuid") == group_uuid

    members = data["users"]

    assert len(members) == 1
    member = members[0]
    user = member["user"]
    role = member["role"]

    assert user["username"] == test_data.user.username
    assert user["uuid"] == str(test_data.user.uuid)
    assert role == "admin"


async def test_get_group_members_unauthed(
    test_data: CaseData,
    logged_http_client: AsyncClient,
):
    response = await logged_http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )

    await _test_group_create_correct(response, GROUP_NAME, GROUP_DESCRIPTION)

    group_uuid = response.json()["uuid"]
    logged_http_client.cookies.clear()
    members_response = await logged_http_client.get(
        f"/group/members?group_uuid={group_uuid}"
    )
    assert members_response.status_code == 401


async def test_get_group_members_no_access(
    test_data: CaseData,
    logged_http_client: AsyncClient,
):
    new_username = "NewUsername"
    new_password = "NewPassword"
    await test_data.user_repo.create_user(
        new_username, new_password
    )

    response = await logged_http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )

    await _test_group_create_correct(response, GROUP_NAME, GROUP_DESCRIPTION)

    group_uuid = response.json()["uuid"]

    logged_http_client.cookies.clear()
    login_response = await logged_http_client.post("/auth/login", json={
        "username": new_username,
        "password": new_password
    })
    assert login_response.status_code == 200 

    members_response = await logged_http_client.get(
        f"/group/members?group_uuid={group_uuid}"
    )
    assert members_response.status_code == 401


async def test_unauthed_user_cannot_create_group(
    http_client: AsyncClient,
    test_data: CaseData
):
    response = await http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )

    assert response.status_code == 401


async def test_get_user_groups(
    logged_http_client: AsyncClient,
    test_data: CaseData
):
    second_group_name = GROUP_NAME + "2"
    second_group_description = GROUP_DESCRIPTION + "2"

    response = await logged_http_client.post(
        "/group/create",
        json={
            "name": GROUP_NAME,
            "description": GROUP_DESCRIPTION
        }
    )
    await _test_group_create_correct(response, GROUP_NAME, GROUP_DESCRIPTION)

    second_response = await logged_http_client.post(
        "/group/create",
        json={
            "name": second_group_name,
            "description": second_group_description
        }
    )
    await _test_group_create_correct(
        second_response,
        second_group_name,
        second_group_description
    )

    user_groups_response = await logged_http_client.get(
        "/group/groups"
    )
    assert user_groups_response.status_code == 200

    data = user_groups_response.json()
    assert "groups" in data

    groups = data["groups"]
    assert len(groups) == 2 

    first_group = GroupForm(**groups[0])
    second_group = GroupForm(**groups[1])

    if first_group.name != GROUP_NAME:
        first_group, second_group = second_group, first_group

    assert first_group.name == GROUP_NAME
    assert first_group.description == GROUP_DESCRIPTION
    assert second_group.name == second_group_name
    assert second_group_description == second_group_description


