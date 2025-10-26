from dispatcher.interface import IWebSocketConnection
from uuid import UUID 


class ConnectionManager:
    def __init__(self):
        self._user_uuid_to_connection: dict[UUID, IWebSocketConnection] = {}

    async def add_connection(
        self,
        user_uuid: UUID,
        conn: IWebSocketConnection
    ) -> None:
        self._user_uuid_to_connection[user_uuid] = conn 

    async def remove_connection(
        self,
        user_uuid: UUID,
    ) -> bool:
        if user_uuid not in self._user_uuid_to_connection:
            return False 

        del self._user_uuid_to_connection[user_uuid]
        return True 

    async def get_connection_by_user_uuid(self, user_uuid: UUID) -> IWebSocketConnection | None:
        return self._user_uuid_to_connection.get(user_uuid)


