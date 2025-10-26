from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiokafka.producer.producer import AIOKafkaProducer

from config.config import KAFKA_BOOTSTRAP_SERVERS


@asynccontextmanager
async def kafka_producer() -> AsyncGenerator[AIOKafkaProducer]:
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    )
    await producer.start()
    try:
        yield producer 
    finally:
        await producer.stop()

