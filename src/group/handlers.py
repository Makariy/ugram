from forms.group import RemoveMembersForm
from forms.group import GroupMembersToRolesForm
from group.deps import GroupWithAdminRole
from fastapi import Response

from auth.deps import CurrentUserDep
from db import DBSessionDep
from forms.group import GroupCreateForm, GroupForm, GroupsForm, GroupWithUsersForm
from group.deps import GroupWithRoleDep
from group.services.forms import (
    create_group_with_users_form,
    group_model_to_group_form,
    groups_to_groups_form,
)
from repository.group import GroupRepository


async def create_group(
    async_session: DBSessionDep,
    user: CurrentUserDep,
    group_form: GroupCreateForm,
    response: Response
) -> GroupForm:
    async with async_session() as session:
        repo = GroupRepository(session)
        group = await repo.create_group(
            creator_uuid=str(user.uuid),
            name=group_form.name,
            description=group_form.description
        )

    response.status_code = 201
    return await group_model_to_group_form(group)


async def get_user_groups(
    async_session: DBSessionDep,
    user: CurrentUserDep,
) -> GroupsForm:
    async with async_session() as session:
        repo = GroupRepository(session)
        groups = await repo.get_user_groups_by_user_uuid(
            str(user.uuid)
        )

    return await groups_to_groups_form(groups)


async def get_group_members(
    async_session: DBSessionDep,
    group_with_role: GroupWithRoleDep
) -> GroupWithUsersForm:
    group, _ = group_with_role
    async with async_session() as session:
        repo = GroupRepository(session)
        user_to_role = await repo.get_group_members(
            str(group.uuid)
        )

    return await create_group_with_users_form(
        group, user_to_role
    )


async def add_members_to_group(
    async_session: DBSessionDep,
    group_with_role: GroupWithAdminRole,
    form: GroupMembersToRolesForm
):
    group, _ = group_with_role
    async with async_session() as session:
        repo = GroupRepository(session)
        await repo.add_users_to_group(
            str(group.uuid), {
                user_uuid_to_role.uuid: user_uuid_to_role.role for user_uuid_to_role in form.members_to_roles
            }
        )

    return await group_model_to_group_form(group)


async def change_members_roles(
    async_session: DBSessionDep,
    group_with_role: GroupWithAdminRole,
    form: GroupMembersToRolesForm
):
    group, _ = group_with_role
    async with async_session() as session:
        repo = GroupRepository(session)
        await repo.change_users_permissions(
            str(group.uuid), {
                user_uuid_to_role.uuid: user_uuid_to_role.role for user_uuid_to_role in form.members_to_roles
            }
        )

    return await group_model_to_group_form(group)


async def remove_members_from_group(
    async_session: DBSessionDep,
    group_with_role: GroupWithAdminRole,
    form: RemoveMembersForm
):
    group, _ = group_with_role
    async with async_session() as session:
        repo = GroupRepository(session)
        await repo.remove_users_from_group(
            str(group.uuid), form.member_uuids
        )

    return await group_model_to_group_form(group)


