from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from db import DATABASE_URL
from models import Base


def get_test_db_name() -> str:
    slash_index = DATABASE_URL.rfind("/")
    return f"test_{DATABASE_URL[slash_index + 1:]}"


def get_test_db_url() -> str:
    slash_index = DATABASE_URL.rfind("/")
    test_db_name = get_test_db_name()
    return f"{DATABASE_URL[:slash_index]}/{test_db_name}"


@pytest_asyncio.fixture(scope="session")
async def create_test_database():
    create_engine = create_async_engine(
        DATABASE_URL,
        isolation_level="AUTOCOMMIT"
    )
    test_db_name = get_test_db_name()
    async with create_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))
        await conn.execute(text(f"CREATE DATABASE {test_db_name}"))

    await create_engine.dispose()

    migration_engine = create_async_engine(get_test_db_url(), echo=False)
    async with migration_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await migration_engine.dispose()

    try:
        yield
    finally:
        drop_engine = create_async_engine(
            DATABASE_URL,
            isolation_level="AUTOCOMMIT"
        )
        test_db_name = get_test_db_name()
        async with drop_engine.begin() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {test_db_name}"))

        await drop_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def engine(create_test_database):
    engine = create_async_engine(get_test_db_url(), echo=False)
    yield engine 
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session_maker(engine: AsyncEngine):
    try:
        async with engine.begin() as conn:
            session_maker = async_sessionmaker(
                conn,
                expire_on_commit=False
            )
            try:
                yield session_maker
            finally:
                await conn.rollback()

    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_session_maker: async_sessionmaker[AsyncSession]):
    async with db_session_maker() as session:
        yield session 

