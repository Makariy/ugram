from models.group import GroupRole
from typing import Annotated
from uuid import UUID

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends

from auth.deps import CurrentUserDep
from db import DBSessionDep
from models.group import Group
from repository.group import GroupRepository


async def get_group_and_check_access(
    async_session: DBSessionDep,
    user: CurrentUserDep,
    group_uuid: UUID
):
    async with async_session() as session:
        repo = GroupRepository(session)
        group_with_role = await repo.get_group_with_user_role(
            group_uuid=str(group_uuid),
            user_uuid=str(user.uuid)
        )

    if group_with_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Group doesn't exist or you are not authorized to access it",
        )

    yield group_with_role


GroupWithRoleDep = Annotated[tuple[Group, GroupRole], Depends(get_group_and_check_access)]


async def get_group_and_check_user_is_admin(group_with_role: GroupWithRoleDep):
    _, role = group_with_role
    if role != GroupRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only group admins can access this"
        )
    yield group_with_role


GroupWithAdminRole = Annotated[tuple[Group, GroupRole], Depends(get_group_and_check_user_is_admin)]


