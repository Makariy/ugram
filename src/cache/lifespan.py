from config.config import REDIS_DB
from config.config import REDIS_PASS
from config.config import REDIS_PORT
from config.config import REDIS_HOST
from cache.connection import ConnectionManager
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def cache_lifespan(app: FastAPI):
    assert REDIS_HOST is not None 
    assert REDIS_PORT is not None 

    await ConnectionManager.connect(
        REDIS_HOST,
        int(REDIS_PORT),
        REDIS_PASS,
        REDIS_DB
    )
    yield 
    await ConnectionManager.close()


