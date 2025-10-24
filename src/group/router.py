from group.handlers import get_group_members
from fastapi.routing import APIRouter

from group.handlers import create_group, get_user_groups


router = APIRouter()
router.add_api_route(
    "/create",
    create_group,
    methods=["POST"]
)
router.add_api_route(
    "/groups",
    get_user_groups,
    methods=["GET"]
)
router.add_api_route(
    "/members",
    get_group_members,
    methods=["GET"]
)

