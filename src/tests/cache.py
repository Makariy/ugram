from config.config import REDIS_DB
from config.config import REDIS_PASS
from config.config import REDIS_PORT
from config.config import REDIS_HOST
from cache.connection import ConnectionManager
import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
async def cache_connection():
    assert REDIS_HOST is not None 
    assert REDIS_PORT is not None 
    await ConnectionManager.connect(
        REDIS_HOST,
        int(REDIS_PORT),
        REDIS_PASS,
        REDIS_DB + 1
    )

    conn = await ConnectionManager.get_connection()
    yield conn

    await ConnectionManager.close()

