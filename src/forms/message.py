from pydantic.main import BaseModel
from datetime import datetime 


class ResourceForm(BaseModel):
    file_url: str 
    mime_type: str | None 
    extra_metadata: dict 


class MessageCreateForm(BaseModel):
    text: str | None 
    resources: list[ResourceForm] | None = None 


class MessageForm(BaseModel):
    uuid: str
    text: str | None 
    group_uuid: str 
    sender_uuid: str 
    sending_date: datetime
    resources: list[ResourceForm] | None 


class MessagesForm(BaseModel):
    messages: list[MessageForm]

