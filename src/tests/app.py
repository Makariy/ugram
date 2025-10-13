from redis.asyncio.client import Redis
from db import db_session_dep
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker
import httpx
import pytest_asyncio

from app import app


@pytest_asyncio.fixture(scope="function")
async def http_client(
    db_session_maker: async_sessionmaker[AsyncSession],
    cache_connection: Redis
):
    async def get_session_maker() -> async_sessionmaker[AsyncSession]:
        return db_session_maker

    app.dependency_overrides[db_session_dep] = get_session_maker

    yield httpx.AsyncClient(
        transport=httpx.ASGITransport(app),
        base_url="http://test"
    )
    del app.dependency_overrides[db_session_dep]

    

