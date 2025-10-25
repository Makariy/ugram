from message.handlers import handle_get_messages
from message.handlers import handle_send_message
from fastapi.routing import APIRouter


router = APIRouter()
router.add_api_route(
    "/{group_uuid:str}/send",
    handle_send_message,
    methods=["POST"]
)
router.add_api_route(
    "/messages",
    handle_get_messages,
    methods=["GET"]
)

