import asyncio
import json
from dataclasses import dataclass

import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from auth.services.request import AUTH_COOKIE_TOKEN_KEY
from dispatcher.connection_manager import ConnectionManager
from dispatcher.receiver import ConnectionDispatcher
from models.user import User
from repository.user import (
    UserRepository,
)
from tests.dispatcher.connection import TestWebSocketConnection


@dataclass
class CaseData:
    username: str
    password: str
    user: User


@pytest_asyncio.fixture(scope="function")
async def test_data(db_session_maker: async_sessionmaker[AsyncSession]):
    username = "TestUser"
    password = "TestUserPassword"

    async with db_session_maker() as session:
        repo = UserRepository(session)
        user = await repo.create_user(username, password)
        assert user

    yield CaseData(
        username=username,
        password=password,
        user=user
    )

async def test_connection_dispatcher_pings(
    http_client: AsyncClient,
    cache_connection: Redis,
    test_data: CaseData,
    db_session_maker: async_sessionmaker[AsyncSession]
):
    manager = ConnectionManager()
    dispatcher = ConnectionDispatcher(
        manager,
        db_session_maker,
        cache_connection
    )
    response = await http_client.post("/auth/login", json={
        "username": test_data.username,
        "password": test_data.password
    })
    assert response.status_code == 200 

    cookies = "; ".join([f"{name}={value}" for name, value in http_client.cookies.items()])
    conn = TestWebSocketConnection({
        "cookie": cookies,
        **dict(http_client.headers.items())
    })

    asyncio.create_task(dispatcher.dispatch_connection(conn))
    raw_data = await asyncio.wait_for(conn.send_queue.get(), 1) 
    data = json.loads(raw_data.decode())

    assert data.get("type") == "ping"
    

async def test_connection_dispatcher_not_pings_for_unauth(
    http_client: AsyncClient,
    cache_connection: Redis,
    test_data: CaseData,
    db_session_maker: async_sessionmaker[AsyncSession]
):
    manager = ConnectionManager()
    dispatcher = ConnectionDispatcher(
        manager,
        db_session_maker,
        cache_connection
    )

    conn = TestWebSocketConnection({
        "cookie": f"{AUTH_COOKIE_TOKEN_KEY}=nonexisting",
    })

    asyncio.create_task(dispatcher.dispatch_connection(conn))
    
    raw_data = await asyncio.wait_for(conn.send_queue.get(), 1) 
    data = json.loads(raw_data.decode())

    assert data.get("type") == "error"
    


