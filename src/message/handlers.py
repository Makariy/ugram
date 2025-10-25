import datetime

from fastapi.responses import Response 
from fastapi.exceptions import HTTPException

from auth.deps import CurrentUserDep
from db import DBSessionDep
from forms.message import MessageCreateForm, MessageForm, MessagesForm
from group.deps import GroupWithRoleDep
from message.forms import message_model_to_form, messages_to_form
from models.group import GroupRole
from repository.message import MessageRepository


async def handle_send_message(
    async_session: DBSessionDep,
    user: CurrentUserDep,
    group_with_role: GroupWithRoleDep,
    message_form: MessageCreateForm,
    response: Response
) -> MessageForm:
    group, role = group_with_role
    if role == GroupRole.MEMBER_READ_ONLY:
        raise HTTPException(
            403,
            detail="You cannot send messages to this chat"
        )

    async with async_session() as session:
        repo = MessageRepository(session)
        message = await repo.create_message(
            sender_uuid=str(user.uuid),
            group_uuid=str(group.uuid),
            text=message_form.text,
            resources=message_form.resources
        )

    response.status_code = 201
    return await message_model_to_form(message)


async def handle_get_messages(
    async_session: DBSessionDep,
    user: CurrentUserDep,
    group_with_role: GroupWithRoleDep,
    last_sending_date: datetime.datetime | None = None 
) -> MessagesForm:
    group, role = group_with_role
    async with async_session() as session:
        repo = MessageRepository(session)
        messages = await repo.get_group_messages(
            group_uuid=str(group.uuid),
            count=100,
            last_sending_date=last_sending_date
        )

    return await messages_to_form(messages)


