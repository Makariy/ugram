from contextlib import asynccontextmanager

from fastapi import FastAPI

from cache.connection import cache_conn
from cache.deps import cache_connection_dep
from producer.connection import kafka_producer
from producer.deps import kafka_producer_dep


@asynccontextmanager
async def connections_lifespan(app: FastAPI):
    async with cache_conn() as conn:
        async with kafka_producer() as producer:
            app.dependency_overrides[cache_connection_dep] = lambda: conn
            app.dependency_overrides[kafka_producer_dep] = lambda: producer
            yield

