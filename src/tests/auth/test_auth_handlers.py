from dataclasses import dataclass

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from auth.services.request import AUTH_COOKIE_TOKEN_KEY
from models.user import User
from repository.user import UserRepository


@dataclass
class CaseData:
    username: str
    password: str
    repo: UserRepository
    user: User


USERNAME = "TestUser"
PASSWORD = "TestUserPassword"

@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.create_user(USERNAME, PASSWORD)
    assert user is not None 

    yield CaseData(
        username=USERNAME,
        password=PASSWORD,
        repo=repo,
        user=user
    )


async def test_login(
    http_client: AsyncClient,
    test_data: CaseData
):
    response = await http_client.post("/auth/login", json={
        "username": test_data.username,
        "password": test_data.password,
    })
    assert response.status_code == 200 
    assert response.cookies.get(AUTH_COOKIE_TOKEN_KEY) is not None 

    data = response.json()
    user = data.get("user")
    assert user is not None 

    assert user.get("username") == test_data.username
    assert user.get("uuid") == str(test_data.user.uuid)


@pytest.mark.parametrize(
    "username, password", [
        [USERNAME + "1", PASSWORD],
        [USERNAME, PASSWORD + "1"],
        ["", PASSWORD],
        [USERNAME, ""],
        [USERNAME.lower(), PASSWORD],
        [USERNAME, PASSWORD.lower()],
    ]
)
async def test_login_incorrect_credentials(
    http_client: AsyncClient,
    test_data: CaseData,
    username: str,
    password: str
):
    response = await http_client.post("/auth/login", json={
        "username": username,
        "password": password,
    })
    assert response.status_code == 403
    assert response.cookies.get(AUTH_COOKIE_TOKEN_KEY) is None 


async def test_register(
    http_client: AsyncClient,
    test_data: CaseData,
):
    username = "NewUser"
    response = await http_client.post("/auth/register", json={
        "username": username,
        "password": "NewUserPassword",
    })
    assert response.status_code == 200 
    assert response.cookies.get(AUTH_COOKIE_TOKEN_KEY) is not None 

    data = response.json()
    user = data.get("user")
    assert user is not None 

    assert user.get("username") == username


async def test_register_existing_user(
    http_client: AsyncClient,
    test_data: CaseData,
):
    response = await http_client.post("/auth/register", json={
        "username": test_data.username,
        "password": test_data.password,
    })
    assert response.status_code == 403
    assert response.cookies.get(AUTH_COOKIE_TOKEN_KEY) is None 


async def test_me(
    http_client: AsyncClient,
    test_data: CaseData
):
    response = await http_client.post("/auth/login", json={
        "username": test_data.username,
        "password": test_data.password,
    })
    token = response.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    assert token is not None 

    response = await http_client.get("/auth/me")

    data = response.json()
    assert data.get("username") == test_data.username
    assert data.get("uuid") == str(test_data.user.uuid)
    

async def test_me_incorrect_token(
    http_client: AsyncClient,
    test_data: CaseData
):
    http_client.cookies.set(AUTH_COOKIE_TOKEN_KEY, "not_existing_token")
    response = await http_client.get("/auth/me")
    assert response.status_code == 403
    data = response.json()
    assert "username" not in data
    assert "uuid" not in data


async def test_logout(
    http_client: AsyncClient,
    test_data: CaseData
):
    response = await http_client.post("/auth/login", json={
        "username": test_data.username,
        "password": test_data.password,
    })
    token = response.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    assert token is not None 

    response = await http_client.post("/auth/logout")
    assert response.status_code == 200 

    data = response.json()
    assert data.get("was_logged") 




    
