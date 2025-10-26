from http.cookies import SimpleCookie

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession

from auth.exceptions import NoActiveSessionException, UnknownUserException
from auth.services.request import AUTH_COOKIE_TOKEN_KEY, get_user_by_token
from dispatcher.interface import IWebSocketConnection
from models.user import User


async def _parse_request_auth_cookie(headers: dict) -> str | None:
    cookies = headers.get("cookie")
    if cookies is None:
        return None 

    parser = SimpleCookie()
    parser.load(cookies)
    cookie = parser.get(AUTH_COOKIE_TOKEN_KEY)
    if cookie is None:
        return None 

    return cookie.value


async def get_user_from_websocket_connection(
    db_session: AsyncSession,
    cache_conn: Redis,
    conn: IWebSocketConnection
) -> User | None:
    headers = await conn.get_request_headers()
    if headers is None:
        return None 

    token = await _parse_request_auth_cookie(headers)
    if token is None:
        return None 

    try:
        return await get_user_by_token(
            db_session,
            cache_conn,
            token
        )
    except (UnknownUserException, NoActiveSessionException):
        return None 

