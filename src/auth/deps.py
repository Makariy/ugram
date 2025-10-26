from auth.exceptions import NoActiveSessionException
from cache.deps import CacheConnectionDep
from db import DBSessionDep
from auth.services.request import get_user_by_token
from typing import Annotated

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.security.http import HTTPAuthorizationCredentials

from auth.services.bearer import session_auth_scheme
from models.user import User



async def get_current_user(
    async_session: DBSessionDep,
    cache_connection: CacheConnectionDep,
    auth_data: Annotated[HTTPAuthorizationCredentials | None, Depends(session_auth_scheme)],
) -> User:
    if auth_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No auth data is provided",
        )
        
    token = auth_data.credentials

    async with async_session() as session:
        try:
            return await get_user_by_token(session, cache_connection, token)
        except NoActiveSessionException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have no active session"
            )


CurrentUserDep = Annotated[User, Depends(get_current_user)]

