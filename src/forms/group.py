from models.group import GroupRole
from forms.user import UserForm
from datetime import datetime 
from pydantic.main import BaseModel


class GroupForm(BaseModel):
    uuid: str 
    name: str 
    description: str | None 
    creation_date: datetime


class GroupsForm(BaseModel):
    groups: list[GroupForm]


class GroupCreateForm(BaseModel):
    name: str 
    description: str


class UserWithRoleForm(BaseModel):
    user: UserForm
    role: GroupRole


class GroupWithUsersForm(BaseModel):
    group: GroupForm
    users: list[UserWithRoleForm]



class GroupMemberUUIDToRole(BaseModel):
    uuid: str 
    role: GroupRole


class GroupMembersToRolesForm(BaseModel):
    members_to_roles: list[GroupMemberUUIDToRole]


class RemoveMembersForm(BaseModel):
    member_uuids: list[str]


