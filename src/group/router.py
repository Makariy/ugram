from group.handlers import change_members_roles
from group.handlers import remove_members_from_group
from group.handlers import add_members_to_group
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
router.add_api_route(
    "/{group_uuid:str}/add_members",
    add_members_to_group,
    methods=["POST"]
)
router.add_api_route(
    "/{group_uuid:str}/remove_members",
    remove_members_from_group,
    methods=["POST"]
)
router.add_api_route(
    "/{group_uuid:str}/change_roles",
    change_members_roles,
    methods=["POST"]
)
