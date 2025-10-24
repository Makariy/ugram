from forms.group import GroupsForm
from forms.group import GroupWithUsersForm
from auth.services.forms import user_model_to_user_form
from models.user import User
from forms.group import UserWithRoleForm
from models.group import GroupRole
from typing import Mapping
from forms.group import GroupForm
from models.group import Group


async def group_model_to_group_form(group: Group) -> GroupForm:
    return GroupForm(
        uuid=str(group.uuid),
        name=group.name,
        description=group.description,
        creation_date=group.creation_date
    )


async def groups_to_groups_form(groups: list[Group]) -> GroupsForm:
    return GroupsForm(
        groups=[await group_model_to_group_form(group) for group in groups]
    )


async def users_to_group_role_to_user_with_role_forms(
    user_to_role: Mapping[User, GroupRole]
) -> list[UserWithRoleForm]:
    user_with_role_forms: list[UserWithRoleForm] = []
    for user, role in user_to_role.items():
        user_with_role_forms.append(
            UserWithRoleForm(
                user=await user_model_to_user_form(user),
                role=role
            )
        )

    return user_with_role_forms


async def create_group_with_users_form(
    group: Group,
    user_to_role: Mapping[User, GroupRole]
) -> GroupWithUsersForm:
    return GroupWithUsersForm(
        group=await group_model_to_group_form(group),
        users=await users_to_group_role_to_user_with_role_forms(
            user_to_role
        )
    )


