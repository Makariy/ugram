from cache.deps import cache_connection_dep
from app import app
from cache.connection import close_connection
from cache.connection import create_connection
from config.config import REDIS_DB
from config.config import REDIS_PASS
from config.config import REDIS_PORT
from config.config import REDIS_HOST
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def cache_connection():
    assert REDIS_HOST is not None 
    assert REDIS_PORT is not None 
    conn = await create_connection(
        REDIS_HOST,
        int(REDIS_PORT),
        REDIS_PASS,
        REDIS_DB + 1
    )

    app.dependency_overrides[cache_connection_dep] = lambda: conn
    try:
        yield conn
    finally:
        await close_connection(conn)

