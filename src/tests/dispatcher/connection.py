from asyncio.queues import Queue
from typing import override

from dispatcher.interface import IWebSocketConnection


class TestWebSocketConnection(IWebSocketConnection):
    __test__ = False 

    def __init__(
        self,
        request_headers: dict | None = None 
    ):
        self.receive_queue = Queue[bytes]()
        self.send_queue = Queue[bytes]()
        self._is_closed = False 
        self.request_headers = request_headers

    @override 
    async def receive(self) -> bytes:
        return await self.receive_queue.get()

    @override 
    async def send(self, data: bytes) -> None:
        await self.send_queue.put(data)

    @override 
    async def is_closed(self) -> bool:
        return self._is_closed

    @override 
    async def close(self) -> None:
        self._is_closed = True 

    @override
    async def get_request_headers(self) -> dict | None:
        return self.request_headers

