from aiokafka.producer.producer import AIOKafkaProducer
from fastapi import Depends
from typing import Annotated


async def kafka_producer_dep() -> AIOKafkaProducer:
    raise RuntimeError("No kafka connection is set")


KafkaProducerDep = Annotated[AIOKafkaProducer, Depends(kafka_producer_dep)]


