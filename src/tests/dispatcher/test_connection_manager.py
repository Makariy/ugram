from uuid import uuid4

from dispatcher.connection_manager import ConnectionManager
from tests.dispatcher.connection import TestWebSocketConnection


async def test_connection_manager():
    manager = ConnectionManager()
    first_uuid = uuid4()
    second_uuid = uuid4()
    third_uuid = uuid4()

    first_conn = TestWebSocketConnection({"info": "first_connection"})
    second_conn = TestWebSocketConnection({"info": "second_connection"})

    await manager.add_connection(first_uuid, first_conn)
    await manager.add_connection(second_uuid, second_conn)

    assert await manager.get_connection_by_user_uuid(first_uuid) == first_conn
    assert await manager.get_connection_by_user_uuid(first_uuid) != second_conn
    assert await manager.get_connection_by_user_uuid(second_uuid) == second_conn
    assert await manager.get_connection_by_user_uuid(third_uuid) is None 

    await manager.remove_connection(second_uuid)
    assert await manager.get_connection_by_user_uuid(second_uuid) is None
    assert await manager.get_connection_by_user_uuid(first_uuid) == first_conn

