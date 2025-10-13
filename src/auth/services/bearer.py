from auth.services.request import AUTH_COOKIE_TOKEN_KEY
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class SessionTokenAuth(HTTPBearer):
    def __init__(self, **kwargs):
        super().__init__(scheme_name="Session Token", **kwargs)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        token = request.cookies.get(AUTH_COOKIE_TOKEN_KEY)
        
        if not token:
            return await super().__call__(request)
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            

session_auth_scheme = SessionTokenAuth(auto_error=False)


