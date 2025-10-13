from auth.services.session import Token
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from auth.services.session import get_user_uuid_by_token
from cache.connection import ConnectionManager
from models.user import User
from repository.user import UserRepository

AUTH_COOKIE_TOKEN_KEY = "auth_token"


async def get_user_uuid_from_request(request: Request) -> str:
    token = request.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="You have no active session"
    )
    if token is None:
        raise exception 

    uuid = await get_user_uuid_by_token(
        await ConnectionManager.get_connection(),
        token
    )
    if uuid is None:
        raise exception

    return uuid 

    
async def get_user_by_uuid(session: AsyncSession, uuid: str) -> User:
    user = await UserRepository(session).get_user_by_uuid(uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No user associated with token"
        )

    return user 


async def get_user_by_token(session: AsyncSession, token: Token) -> User:
    uuid = await get_user_uuid_by_token(
        await ConnectionManager.get_connection(),
        token
    )
    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You have no active session"
        )

    return await get_user_by_uuid(session, uuid)



