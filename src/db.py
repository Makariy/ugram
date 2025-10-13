from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Annotated, AsyncGenerator
from fastapi import Depends 
from config.config import (
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PORT,
    DB_PASS
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker 

assert DB_HOST is not None
assert DB_NAME is not None
assert DB_USER is not None
assert DB_PORT is not None
assert DB_PASS is not None

DRIVER = "postgresql+asyncpg"
DATABASE_URL = f"{DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
_async_session = async_sessionmaker(engine, expire_on_commit=False)



async def db_session_dep() -> AsyncGenerator[async_sessionmaker[AsyncSession]]:
    yield _async_session


DBSessionDep = Annotated[async_sessionmaker[AsyncSession], Depends(db_session_dep)]

