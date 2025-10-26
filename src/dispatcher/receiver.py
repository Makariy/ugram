import asyncio
import json
from typing import Never
from uuid import UUID

import websockets
from loguru import logger
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from websockets.asyncio.server import ServerConnection

from dispatcher.auth import get_user_from_websocket_connection
from dispatcher.connection import WebSocketConnection
from dispatcher.connection_manager import ConnectionManager
from dispatcher.interface import IWebSocketConnection
from models.user import User


class ConnectionDispatcher:
    def __init__(
        self,
        manager: ConnectionManager,
        db_session_maker: async_sessionmaker[AsyncSession],
        cache_conn: Redis
    ):
        self._manager: ConnectionManager = manager 
        self._db_session_maker = db_session_maker
        self._cache_conn = cache_conn

    async def dispatch_connection(self, conn: IWebSocketConnection) -> None:
        user = await self._get_user_or_close_connection(conn)
        if user is None:
            return 

        user_uuid = UUID(str(user.uuid))
        await self._manager.add_connection(user_uuid, conn)
        try:
            await self._dispatch_connection(conn)
        except Exception as e:
            logger.error(f"Got an error dispatching connection: {e}")

        finally:
            await self._manager.remove_connection(user_uuid)

    async def _get_user_or_close_connection(self, conn: IWebSocketConnection) -> User | None:
        async with self._db_session_maker() as session:
            user = await get_user_from_websocket_connection(
                session,
                self._cache_conn,
                conn
            )

        if user is None:
            await conn.send(json.dumps({
                "type": "error",
                "detail": "you are not authenticated"
            }).encode())
            return await conn.close()

        return user 

    async def _dispatch_connection(self, conn: IWebSocketConnection) -> None:
        await conn.send(json.dumps({"type": "ping"}).encode())
        while True:
            await conn.receive()
            await asyncio.sleep(0.1)



class ConnectionReceiver:
    def __init__(
        self,
        manager: ConnectionManager,
        websocket_host: str,
        websocket_port: int,
        db_session_maker: async_sessionmaker[AsyncSession],
        cache_conn: Redis
    ):
        self._websocket_host: str = websocket_host 
        self._websocket_port: int = websocket_port 
        self._dispatcher = ConnectionDispatcher(
            manager=manager,
            db_session_maker=db_session_maker,
            cache_conn=cache_conn
        )

    async def run_receiving_connections(self) -> Never:
        async with websockets.serve(
            self._receive_websocket_connection,
            self._websocket_host,
            self._websocket_port
        ) as server:
            await server.serve_forever()

        raise RuntimeError("WebSocket server has unexpectedly stopped")

    async def _receive_websocket_connection(self, raw_conn: ServerConnection) -> None:
        conn = WebSocketConnection(raw_conn)
        return await self._dispatcher.dispatch_connection(conn)

