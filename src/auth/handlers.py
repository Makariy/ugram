from auth.deps import GetCurrentUserDep
from db import DBSessionDep
from models.user import User
from auth.services.session import (
    Token,
    logout_user_by_token,
    authenticate_user,
    authorize_user,
)
from repository.user import UserRepository
from fastapi import Response, Request, HTTPException, status
from pydantic import BaseModel

from cache.connection import ConnectionManager
from forms.user import UserLoginForm, UserRegistrationForm, UserForm
from auth.services.request import AUTH_COOKIE_TOKEN_KEY


class LoginResponse(BaseModel):
    user: UserForm


class LogoutResponse(BaseModel):
    was_logged: bool


async def _add_cookie_and_return_response(
    user: User, token: Token, response: Response
) -> LoginResponse:
    response.set_cookie(
        AUTH_COOKIE_TOKEN_KEY,
        token,
        httponly=True,
    )
    return LoginResponse(
        user=UserForm(
            username=user.username,
            uuid=str(user.uuid)
        )
    )


async def handle_login(
    async_session: DBSessionDep,
    response: Response,
    form: UserLoginForm,
):
    async with async_session() as session:
        user = await authenticate_user(session, form.username, form.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )

    conn = await ConnectionManager.get_connection()
    token = await authorize_user(conn, user)
    return await _add_cookie_and_return_response(user, token, response)


async def handle_registration(
    async_session: DBSessionDep,
    response: Response,
    form: UserRegistrationForm,
):
    async with async_session() as session:
        user = await UserRepository(session).create_user(form.username, form.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A user with this username already exists"
        )

    token = await authorize_user(await ConnectionManager.get_connection(), user)
    return await _add_cookie_and_return_response(user, token, response)


async def handle_me(
    async_session: DBSessionDep,
    user: GetCurrentUserDep
):
    return UserForm(
        username=user.username,
        uuid=str(user.uuid)
    )


async def handle_logout(
    response: Response,
    request: Request
):
    token = request.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No session token is set"
        )

    result = await logout_user_by_token(await ConnectionManager.get_connection(), token)
    response.delete_cookie(AUTH_COOKIE_TOKEN_KEY, httponly=True)

    return LogoutResponse(was_logged=result)

