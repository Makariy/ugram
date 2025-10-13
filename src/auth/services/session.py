import random
import string
from typing import TypeAlias

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.user import User
from repository.user import UserRepository
from auth.services.hash import hash_user_password


Token: TypeAlias = str

USER_SESSION_KEY_PREFIX = "user_session"


async def _generate_auth_token() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=64))


async def _render_user_session_key(token: Token, user_uuid: str) -> str:
    return f"{USER_SESSION_KEY_PREFIX}_{token}_{user_uuid}"


async def _get_user_session_key_by_token(conn: Redis, token: Token) -> str | None:
    keys = await conn.keys(f"{USER_SESSION_KEY_PREFIX}_{token}_*")
    if not keys:
        return None 

    return keys[0]


async def _get_user_session_key_by_user_uuid(conn: Redis, uuid: str) -> str | None:
    keys = await conn.keys(f"{USER_SESSION_KEY_PREFIX}_*_{uuid}")
    if not keys:
        return None 

    return keys[0]


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_username(username)
    if user is None:
        return None

    if user.password_hash != hash_user_password(password):
        return None

    return user


async def authorize_user(
    conn: Redis,
    user: User,
) -> Token:
    await logout_user_by_uuid(conn, str(user.uuid))

    token = await _generate_auth_token()
    key = await _render_user_session_key(token, str(user.uuid))
    await conn.set(key, str(user.uuid))
    return token


async def get_user_uuid_by_token(conn: Redis, token: str) -> str | None:
    key = await _get_user_session_key_by_token(conn, token)
    if key is None:
        return None 

    uuid = await conn.get(key)
    if uuid is None:
        return None
    return uuid.decode()


async def logout_user_by_token(conn: Redis, token: str) -> bool:
    key = await _get_user_session_key_by_token(conn, token)
    if key is None:
        return False 

    return await conn.delete(key) == 1


async def logout_user_by_uuid(conn: Redis, uuid: str) -> bool:
    key = await _get_user_session_key_by_user_uuid(conn, uuid)
    if key is None:
        return False 

    return await conn.delete(key) == 1

