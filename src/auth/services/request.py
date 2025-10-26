from auth.exceptions import UnknownUserException
from auth.exceptions import NoActiveSessionException
from redis.asyncio.client import Redis
from auth.services.session import Token
from sqlalchemy.ext.asyncio.session import AsyncSession

from auth.services.session import get_user_uuid_by_token
from models.user import User
from repository.user import UserRepository

AUTH_COOKIE_TOKEN_KEY = "auth_token"


async def get_user_by_uuid(session: AsyncSession, uuid: str) -> User:
    user = await UserRepository(session).get_user_by_uuid(uuid)
    if user is None:
        raise UnknownUserException()

    return user 


async def get_user_by_token(
    session: AsyncSession,
    cache_connection: Redis,
    token: Token
) -> User:
    uuid = await get_user_uuid_by_token(cache_connection, token)
    if uuid is None:
        raise NoActiveSessionException()

    return await get_user_by_uuid(session, uuid)



