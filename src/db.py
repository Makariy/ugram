from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from config.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

assert DB_HOST is not None
assert DB_NAME is not None
assert DB_USER is not None
assert DB_PORT is not None
assert DB_PASS is not None

DRIVER = "postgresql+asyncpg"
DATABASE_URL = f"{DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
_async_session = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def db_session() -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    yield _async_session


async def db_session_dep() -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    async with db_session() as async_session:
        yield async_session


DBSessionDep = Annotated[async_sessionmaker[AsyncSession], Depends(db_session_dep)]

