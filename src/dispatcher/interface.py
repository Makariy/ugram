from abc import ABC, abstractmethod
from typing import AsyncGenerator

from pydantic.main import BaseModel


class Update(BaseModel):
    channel: str 
    data: dict 


class IUpdatesPuller(ABC):
    @abstractmethod
    def run_pulling_updates(self) -> AsyncGenerator[Update]:
        pass


class IUpdateDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, update: Update) -> None:
        pass 


class IWebSocketConnection(ABC):
    @abstractmethod
    async def is_closed(self) -> bool:
        pass 

    @abstractmethod
    async def send(self, data: bytes) -> None:
        pass 

    @abstractmethod
    async def receive(self) -> bytes:
        pass 

    @abstractmethod
    async def get_request_headers(self) -> dict | None:
        pass 

    @abstractmethod
    async def close(self) -> None:
        pass

