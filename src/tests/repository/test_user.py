from repository.user import UserDeleteException
import pytest 
from auth.services.hash import hash_user_password
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession
from dataclasses import dataclass

import pytest_asyncio

from models.user import User
from repository.user import UserRepository


@dataclass
class CaseData:
    username: str
    password: str
    repo: UserRepository


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    username = "TestUser"
    password = "TestUserPassword"

    repo = UserRepository(db_session)

    yield CaseData(username=username, password=password, repo=repo)


async def test_create_user(test_data: CaseData):
    user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert user is not None 
    assert user.username == test_data.username 
    assert user.password_hash == hash_user_password(test_data.password)


async def test_create_user_with_existing_username(test_data: CaseData):
    original_user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert original_user is not None 

    new_user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert new_user is None 

    original_user_refreshed = await test_data.repo.get_user_by_uuid(str(original_user.uuid))
    assert original_user_refreshed is not None 
    assert original_user_refreshed.username == test_data.username 
    assert original_user_refreshed.password_hash == hash_user_password(test_data.password)


async def test_get_user_by_username(test_data: CaseData):
    user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert user is not None 
    
    retrieved_user = await test_data.repo.get_user_by_username(test_data.username)
    assert user == retrieved_user


async def test_get_user_by_uuid(test_data: CaseData):
    user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert user is not None 
    
    retrieved_user = await test_data.repo.get_user_by_uuid(str(user.uuid))
    assert user == retrieved_user


async def test_delete_user_by_uuid(test_data: CaseData):
    user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert user is not None 

    await test_data.repo.delete_user_by_uuid(str(user.uuid))


async def test_delete_user_by_uuid_not_exists(test_data: CaseData):
    user = await test_data.repo.create_user(
        test_data.username,
        test_data.password
    )
    assert user is not None 

    with pytest.raises(UserDeleteException):
        await test_data.repo.delete_user_by_uuid(
            "aaaaaaaa" + str(user.uuid)[8:]
        )

