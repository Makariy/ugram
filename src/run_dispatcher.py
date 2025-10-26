import asyncio
from typing import Awaitable, Never

from cache.connection import cache_conn
from config.config import WEBSOCKET_HOST, WEBSOCKET_PORT
from db import db_session
from dispatcher.connection_manager import ConnectionManager
from dispatcher.dispatcher import UpdatesDispatcher
from dispatcher.dispatchers.message_sent import TOPIC as MESSAGE_SENT_TOPIC
from dispatcher.dispatchers.message_sent import MessageSentDispatcher
from dispatcher.puller.kafka import KafkaUpdatesPuller
from dispatcher.receiver import ConnectionReceiver


async def _run_receiving_connections(manager: ConnectionManager) -> Never:
    assert WEBSOCKET_HOST is not None 
    assert WEBSOCKET_PORT is not None 

    async with cache_conn() as cache:
        async with db_session() as db_session_maker:
            receiver = ConnectionReceiver(
                manager,
                websocket_host=WEBSOCKET_HOST,
                websocket_port=int(WEBSOCKET_PORT),
                db_session_maker=db_session_maker,
                cache_conn=cache
            )
            await receiver.run_receiving_connections()

    raise RuntimeError("ConnectionReceiver has unexpectedly stopped")


async def _run_dispatching_updates(manager: ConnectionManager):
    puller = KafkaUpdatesPuller(
        [MESSAGE_SENT_TOPIC]
    )
    async with db_session() as db_session_maker:
        dispatcher = UpdatesDispatcher(puller, {
            MESSAGE_SENT_TOPIC: MessageSentDispatcher(manager, db_session_maker)
        })
        await dispatcher.run_dispatching()

    raise RuntimeError("UpdatesDispatcher has unexpectedly stopped")


async def main():
    manager = ConnectionManager()
    tasks: list[Awaitable] = [
        asyncio.create_task(_run_receiving_connections(manager)),
        asyncio.create_task(_run_dispatching_updates(manager)),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())

