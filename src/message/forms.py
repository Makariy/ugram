from models.message import MessageResource
from typing import Sequence
from forms.message import MessagesForm
from forms.message import ResourceForm
from forms.message import MessageForm
from models.message import Message


async def resource_model_to_form(resource: MessageResource) -> ResourceForm:
    return ResourceForm(
        file_url=resource.file_url,
        mime_type=resource.mime_type,
        extra_metadata=resource.extra_metadata,
    )


async def resources_to_form(resources: list[MessageResource]) -> list[ResourceForm]:
    return [await resource_model_to_form(resource) for resource in resources]


async def message_model_to_form(
    message: Message,
) -> MessageForm:
    return MessageForm(
        uuid=str(message.uuid),
        text=message.text,
        group_uuid=str(message.group_uuid),
        sender_uuid=str(message.sender_uuid),
        resources=await resources_to_form(message.resources),
        sending_date=message.sending_date,
    )


async def messages_to_form(messages: Sequence[Message]) -> MessagesForm:
    return MessagesForm(
        messages=[
            await message_model_to_form(message) for message in messages
        ]
    )

