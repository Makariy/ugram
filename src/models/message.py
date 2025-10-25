from sqlalchemy.dialects.postgresql.json import JSONB
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, ForeignKey, UUID, DateTime, Text, String
from sqlalchemy.orm import relationship
from .base import Base
from .user import User 
from .group import Group


# TODO: add message type (text_only, text_with_attachments, attachments_only, audio, sticker)
class Message(Base):
    __tablename__ = "messages"

    uuid = Column(
        UUID(),
        primary_key=True,
        default=uuid4
    )
    text = Column(
        Text(),
        nullable=True,
    )
    sending_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now()
    )

    sender_uuid = Column(
        UUID(),
        ForeignKey(
            f"{User.__tablename__}.uuid",
            ondelete="SET NULL"
        ),
    )
    group_uuid = Column(
        UUID(),
        ForeignKey(
            f"{Group.__tablename__}.uuid",
            ondelete="CASCADE"
        ),
    )

    sender = relationship(
        User,
        foreign_keys=[sender_uuid]
    )
    group = relationship(
        Group,
        foreign_keys=[group_uuid]
    )
    resources = relationship(
        "MessageResource",
        back_populates="message",
        lazy="selectin"
    )
    

class MessageResource(Base):
    __tablename__ = "message_resource"

    uuid = Column(
        UUID(),
        primary_key=True,
        default=uuid4
    )
    file_url = Column(
        String(512)
    )
    mime_type = Column(
        String(256),
        nullable=True
    )
    extra_metadata = Column(
        JSONB(),
        nullable=True
    )
    message_uuid = Column(
        UUID(),
        ForeignKey(
            f"{Message.__tablename__}.uuid",
            ondelete="CASCADE"
        ),
    )
    message = relationship(
        Message,
        foreign_keys=[message_uuid],
    )

