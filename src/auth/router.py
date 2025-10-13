from auth.handlers import (
    handle_login,
    handle_registration,
    handle_me,
    handle_logout,
)
from fastapi import APIRouter


router = APIRouter()
router.add_api_route(
    "/login",
    handle_login,
    methods=["POST"]
)
router.add_api_route(
    "/register",
    handle_registration,
    methods=["POST"]
)
router.add_api_route(
    "/me",
    handle_me,
    methods=["GET"]
)
router.add_api_route(
    "/logout",
    handle_logout,
    methods=["POST"]
)

