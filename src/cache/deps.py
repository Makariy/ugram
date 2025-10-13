from fastapi import Depends
from typing import Annotated
from redis.asyncio.client import Redis


async def cache_connection_dep() -> Redis:
    raise RuntimeError("No redis connection is set")


CacheConnectionDep = Annotated[Redis, Depends(cache_connection_dep)]


