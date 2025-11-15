from forms.user import UsersListForm
from sqlalchemy.sql.schema import Sequence
from forms.user import UserForm
from models.user import User


async def user_model_to_user_form(user: User) -> UserForm:
    return UserForm(
        username=user.username,
        uuid=str(user.uuid)
    )


async def users_sequence_to_users_list_form(users: Sequence[User]) -> UsersListForm:
    return UsersListForm(
        users=[await user_model_to_user_form(user) for user in users]
    )


