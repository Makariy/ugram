from dataclasses import dataclass

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.group import GroupRole
from models.user import User
from repository.group import GroupDeleteException, GroupRepository
from repository.user import UserRepository


@dataclass
class CaseData:
    user: User
    group_name: str 
    group_description: str
    repo: GroupRepository

    first_user: User 
    second_user: User


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session: AsyncSession):
    user = await UserRepository(db_session).create_user(
        "TestUser",
        "TestUserPassword"
    )
    assert user is not None 

    group_name = "TestGroup"
    group_description = "TestGroup description"

    first_username = "FirstUser"
    first_password = "FirstUserPassword"
    second_username = "SecondUser"
    second_password = "SecondUserPassword"
    repo = UserRepository(db_session)
    first_user = await repo.create_user(first_username, first_password)
    second_user = await repo.create_user(second_username, second_password)
    assert first_user
    assert second_user

    repo = GroupRepository(db_session)

    yield CaseData(
        user=user,
        group_name=group_name,
        group_description=group_description,
        repo=repo,
        first_user=first_user,
        second_user=second_user,
    )


async def test_create_group(test_data: CaseData):
    group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        test_data.group_name,
        test_data.group_description,
    )
    assert group.name == test_data.group_name
    assert group.description == test_data.group_description


async def test_get_user_groups_by_user_uuid(test_data: CaseData):
    first_group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        test_data.group_name,
        test_data.group_description,
    )

    second_group_name = test_data.group_name + "2"
    second_group_description = test_data.group_description + "2"
    second_group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        second_group_name,
        second_group_description,
    )
    
    groups = await test_data.repo.get_user_groups_by_user_uuid(str(test_data.user.uuid))
    first_ret_group, second_ret_group = groups
    if first_ret_group.uuid != first_group.uuid:
        first_ret_group, second_ret_group = second_ret_group, first_ret_group

    assert first_ret_group == first_group
    assert second_ret_group == second_group


async def test_add_users_to_group(
    test_data: CaseData,
):
    group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        test_data.group_name,
        test_data.group_description,
    )

    await test_data.repo.add_users_to_group(
        str(group.uuid),
        {
            str(test_data.first_user.uuid): GroupRole.MEMBER,
            str(test_data.second_user.uuid): GroupRole.MEMBER_READ_ONLY
        }
    )

    first_user_groups = await test_data.repo.get_user_groups_by_user_uuid(
        str(test_data.first_user.uuid)
    )
    assert len(first_user_groups) == 1
    second_user_groups = await test_data.repo.get_user_groups_by_user_uuid(
        str(test_data.second_user.uuid)
    )
    assert len(second_user_groups) == 1

    assert first_user_groups[0] == group
    assert second_user_groups[0] == group


async def test_get_group_members(test_data: CaseData):
    group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        test_data.group_name,
        test_data.group_description,
    )

    await test_data.repo.add_users_to_group(
        str(group.uuid),
        {
            str(test_data.first_user.uuid): GroupRole.MEMBER,
            str(test_data.second_user.uuid): GroupRole.MEMBER_READ_ONLY
        }
    )

    user_to_role = await test_data.repo.get_group_members(str(group.uuid))

    assert user_to_role.get(test_data.user) == GroupRole.ADMIN
    assert user_to_role.get(test_data.first_user) == GroupRole.MEMBER
    assert user_to_role.get(test_data.second_user) == GroupRole.MEMBER_READ_ONLY


async def test_delete_group(test_data: CaseData):
    group = await test_data.repo.create_group(
        str(test_data.user.uuid),
        test_data.group_name,
        test_data.group_description,
    )

    await test_data.repo.delete_group(str(group.uuid))
    group_members = await test_data.repo.get_group_members(str(group.uuid))
    assert not group_members


async def test_delete_not_existing_group(test_data: CaseData):
    with pytest.raises(GroupDeleteException):
        await test_data.repo.delete_group(str(test_data.user.uuid))

