from auth.services.forms import users_sequence_to_users_list_form
from forms.user import UsersListForm
from auth.services.forms import user_model_to_user_form
from cache.deps import CacheConnectionDep
from auth.deps import CurrentUserDep
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
        user=await user_model_to_user_form(user)
    )


async def handle_login(
    async_session: DBSessionDep,
    cache_connection: CacheConnectionDep,
    response: Response,
    form: UserLoginForm,
) -> LoginResponse:
    async with async_session() as session:
        user = await authenticate_user(session, form.username, form.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
        )

    token = await authorize_user(cache_connection, user)
    return await _add_cookie_and_return_response(user, token, response)


async def handle_registration(
    async_session: DBSessionDep,
    cache_connection: CacheConnectionDep,
    response: Response,
    form: UserRegistrationForm,
) -> LoginResponse:
    async with async_session() as session:
        user = await UserRepository(session).create_user(form.username, form.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A user with this username already exists"
        )

    token = await authorize_user(cache_connection, user)
    return await _add_cookie_and_return_response(user, token, response)


async def handle_me(
    user: CurrentUserDep
) -> UserForm:
    return await user_model_to_user_form(user)


async def handle_logout(
    cache_connection: CacheConnectionDep,
    response: Response,
    request: Request
):
    token = request.cookies.get(AUTH_COOKIE_TOKEN_KEY)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No session token is set"
        )

    result = await logout_user_by_token(cache_connection, token)
    response.delete_cookie(AUTH_COOKIE_TOKEN_KEY, httponly=True)

    return LogoutResponse(was_logged=result)


async def handle_get_all_users(
    async_session: DBSessionDep
) -> UsersListForm:
    async with async_session() as session:
        users = await UserRepository(session).get_all_users()

    return await users_sequence_to_users_list_form(users)


