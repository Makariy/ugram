import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from redis.asyncio.client import Redis

from config.config import REDIS_DB, REDIS_HOST, REDIS_PASS, REDIS_PORT


async def create_connection(
    host: str, port: int, password: str | None, db: int
) -> Redis:
    conn = Redis(host=host, port=port, password=password, db=db)
    await asyncio.wait_for(conn.ping(), 1)
    return conn


async def close_connection(conn: Redis):
    await conn.aclose()


@asynccontextmanager
async def cache_conn() -> AsyncGenerator[Redis]:
    assert REDIS_HOST is not None
    assert REDIS_PORT is not None

    conn = await create_connection(REDIS_HOST, int(REDIS_PORT), REDIS_PASS, REDIS_DB)
    try:
        yield conn
    finally:
        await close_connection(conn)


