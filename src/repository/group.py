from uuid import UUID
from models.group import GroupRole
from typing import Mapping
from models.user import User 
from models.group import GroupToUser
from models.group import Group

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession


class GroupDeleteException(Exception):
    pass


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_group_by_uuid(self, uuid: str) -> Group | None:
        result = await self._session.execute(
            select(Group). 
                where(Group.uuid == UUID(uuid))
        )
        return result.scalar_one_or_none()

    async def get_group_with_user_role(
        self,
        group_uuid: str,
        user_uuid: str
    ) -> tuple[Group, GroupRole] | None:
        result = await self._session.execute(
            select(Group, GroupToUser). 
                join(
                    GroupToUser,
                    (GroupToUser.user_uuid == UUID(user_uuid)) & 
                    (GroupToUser.group_uuid == group_uuid)
                )
        )
        
        group_with_role = result.first()
        if not group_with_role:
            return None 

        group, group_role = group_with_role
        return group, GroupRole(group_role.role)

    async def get_user_groups_by_user_uuid(
        self,
        uuid: str 
    ) -> list[Group]:
        result = await self._session.execute(
            select(Group).
                join(
                    GroupToUser,
                    (GroupToUser.user_uuid == UUID(uuid)) & 
                    (GroupToUser.group_uuid == Group.uuid)
                )
        )
        groups = result.scalars().all()
        return list(groups)

    async def add_users_to_group(
        self, 
        group_uuid: str,
        user_uuid_to_role: Mapping[str, GroupRole]
    ):
        for user_uuid, role in user_uuid_to_role.items():
            self._session.add(
                GroupToUser(
                    group_uuid=group_uuid,
                    user_uuid=user_uuid,
                    role=role
                )
            )

        await self._session.commit()

    async def create_group(
        self,
        creator_uuid: str,
        name: str,
        description: str
    ) -> Group:
        async with self._session.begin():
            group = Group(name=name, description=description)
            self._session.add(group)
            await self._session.flush()

            creator_role = GroupToUser(
                group_uuid=group.uuid,
                user_uuid=creator_uuid,
                role=GroupRole.ADMIN
            )
            self._session.add(creator_role)

        return group

    async def get_group_members(self, group_uuid: str) -> Mapping[User, GroupRole]:
        result = await self._session.execute(
            select(User, GroupToUser).
                join(
                    GroupToUser,
                    (User.uuid == GroupToUser.user_uuid) & 
                    (GroupToUser.group_uuid == group_uuid)
                )
        )

        user_to_role: dict[User, GroupRole] = {}
        user: User
        group_to_user: GroupToUser
        for user, group_to_user in result.all():
            user_to_role[user] = group_to_user.role

        return user_to_role

    async def delete_group(self, group_uuid: str) -> None:
        result = await self._session.execute(
            delete(Group).
                where(Group.uuid == group_uuid)
        )
        if result.rowcount != 1:
            raise GroupDeleteException(f"Group {group_uuid} does not exist")


