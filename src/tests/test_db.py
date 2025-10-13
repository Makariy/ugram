from sqlalchemy.ext.asyncio.session import AsyncSession
from hashlib import sha256

from sqlalchemy import select

from models.user import User


async def test_database_resets(db_session: AsyncSession):
    username = "Makariy"
    user = User(
        username=username,
        password_hash=sha256("secret".encode()).hexdigest(),
    )
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.username == username))
    users = result.all()
    assert len(users) == 1

