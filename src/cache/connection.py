import asyncio 
from redis.asyncio.client import Redis


async def create_connection(
    host: str,
    port: int,
    password: str | None,
    db: int
) -> Redis:
    conn = Redis(
        host=host,
        port=port,
        password=password,
        db=db
    )
    await asyncio.wait_for(conn.ping(), 1)
    return conn 


async def close_connection(conn: Redis):
    await conn.aclose()


