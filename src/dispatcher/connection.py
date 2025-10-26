from typing import override
from dispatcher.interface import IWebSocketConnection
from websockets import State 
from websockets.asyncio.server import ServerConnection


class WebSocketConnection(IWebSocketConnection):
    def __init__(self, conn: ServerConnection):
        self._conn = conn 

    @override
    async def is_closed(self) -> bool:
        return self._conn.state in [State.CLOSED, State.CLOSING]

    @override
    async def send(self, data: bytes) -> None:
        return await self._conn.send(data)

    @override
    async def receive(self) -> bytes:
        return bytes(await self._conn.recv())

    @override
    async def close(self) -> None:
        return await self._conn.close()

    @override
    async def get_request_headers(self) -> dict | None:
        request = self._conn.request
        if request is None:
            return None 

        return dict(request.headers.items())

