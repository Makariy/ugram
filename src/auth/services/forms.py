from forms.user import UserForm
from models.user import User


async def user_model_to_user_form(user: User) -> UserForm:
    return UserForm(
        username=user.username,
        uuid=str(user.uuid)
    )

