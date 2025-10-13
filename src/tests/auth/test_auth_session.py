from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession
from dataclasses import dataclass

import pytest_asyncio

from models.user import User
from repository.user import UserRepository
from auth.services.session import (
    authorize_user,
    authenticate_user,
    logout_user_by_token,
    logout_user_by_uuid,
    get_user_uuid_by_token,
)


@dataclass
class CaseData:
    username: str
    password: str
    repo: UserRepository
    user: User


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    username = "TestUser"
    password = "TestUserPassword"

    repo = UserRepository(db_session)
    user = await repo.create_user(username, password)
    assert user is not None 

    yield CaseData(username=username, password=password, repo=repo, user=user)


async def test_authenticate_user(db_session: AsyncSession, test_data: CaseData):
    user = await authenticate_user(db_session, test_data.username, test_data.password)

    assert user is not None
    assert user == test_data.user


async def test_authenticate_user_incorrect_password(
    db_session: AsyncSession, test_data: CaseData
):
    user = await authenticate_user(
        db_session, test_data.username, test_data.password + "123"
    )
    assert user is None


async def test_authenticate_not_existing_user(
    db_session: AsyncSession, test_data: CaseData
):
    user = await authenticate_user(
        db_session, test_data.username + "123", test_data.password
    )
    assert user is None


async def test_authorize_user(cache_connection: Redis, test_data: CaseData):
    token = await authorize_user(cache_connection, test_data.user)
    assert token

    user_uuid = await get_user_uuid_by_token(cache_connection, token)
    assert user_uuid == str(test_data.user.uuid)


async def test_authorize_user_deletes_previous_session(
    cache_connection: Redis,
    test_data: CaseData
):
    prev_token = await authorize_user(cache_connection, test_data.user)
    new_token = await authorize_user(cache_connection, test_data.user)
    assert prev_token != new_token

    user_uuid = await get_user_uuid_by_token(cache_connection, prev_token)
    assert user_uuid is None 


async def test_logout_user(cache_connection: Redis, test_data: CaseData):
    token = await authorize_user(cache_connection, test_data.user)
    assert token

    result = await logout_user_by_token(cache_connection, token)
    assert result
    user_uuid = await get_user_uuid_by_token(cache_connection, token)
    assert user_uuid is None


async def test_logout_not_logged_user(cache_connection: Redis):
    token = "not_existing_token"
    result = await logout_user_by_token(cache_connection, token)
    assert not result
    user_uuid = await get_user_uuid_by_token(cache_connection, token)
    assert user_uuid is None


async def test_logout_by_uuid(cache_connection: Redis, test_data: CaseData):
    token = await authorize_user(cache_connection, test_data.user)
    assert token

    result = await logout_user_by_uuid(cache_connection, str(test_data.user.uuid))
    assert result 

    user_uuid = await get_user_uuid_by_token(cache_connection, token)
    assert user_uuid is None 


async def test_logout_by_uuid_not_logged_user(cache_connection: Redis, test_data: CaseData):
    result = await logout_user_by_uuid(cache_connection, str(test_data.user.uuid))
    assert not result 

    

