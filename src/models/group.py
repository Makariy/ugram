from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from models.base import Base
from models.user import User


class Group(Base):
    __tablename__ = "groups"

    uuid = Column(
        UUID(),
        primary_key=True,
        default=uuid4
    )
    name = Column(
        String(256),
        nullable=False,
    )
    description = Column(
        Text(),
        nullable=True,
    )
    creation_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now()
    )


class GroupRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    MEMBER_READ_ONLY = "member_read_only"


class GroupToUser(Base):
    __tablename__ = "group_to_user"

    group_uuid = Column(
        UUID(),
        ForeignKey(
            f"{Group.__tablename__}.uuid",
            ondelete="CASCADE"
        ),
        primary_key=True,
    )
    user_uuid = Column(
        UUID(),
        ForeignKey(
            f"{User.__tablename__}.uuid",
            ondelete="CASCADE"
        ),
        primary_key=True,
    )

    role = Column(
        SQLEnum(
            GroupRole
        ),
        nullable=False,
    )

    group = relationship(
        Group,
        foreign_keys=[group_uuid]
    )
    user = relationship(
        User,
        foreign_keys=[user_uuid]
    )

