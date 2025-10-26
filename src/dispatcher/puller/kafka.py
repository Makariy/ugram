from typing import Sequence
import json
from typing import AsyncGenerator, override

from aiokafka import AIOKafkaConsumer

from config.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from dispatcher.interface import IUpdatesPuller, Update
from loguru import logger


class KafkaUpdatesPuller(IUpdatesPuller):
    def __init__(self, topics: Sequence[str]):
        self._topics = topics

    @override
    async def run_pulling_updates(self) -> AsyncGenerator[Update]:
        consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=KAFKA_GROUP_ID,
            enable_auto_commit=True,
            auto_offset_reset="latest"
        )

        logger.info("Starting kafka consume")
        await consumer.start()
        try:
            logger.info("Consuming kafka")
            async for update in self._run_pulling_updates(consumer):
                yield update
        finally:
            await consumer.stop()

    async def _run_pulling_updates(self, consumer: AIOKafkaConsumer) -> AsyncGenerator[Update]:
        async for raw_update in consumer:
            if raw_update.value is None:
                continue 

            update = Update(
                channel=raw_update.topic,
                data=json.loads(raw_update.value.decode())
            )
            yield update

