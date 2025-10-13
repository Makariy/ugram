from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime
from .base import Base


class User(Base):
    __tablename__ = "users"

    uuid = Column(
        UUID(),
        primary_key=True,
        default=uuid4
    )
    username = Column(
        String(256),
        nullable=False,
        unique=True
    )
    password_hash = Column(
        String(256),
        nullable=False
    )
    registration_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now()
    )

