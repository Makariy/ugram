from dispatcher.dispatchers.message_sent import MessageSentUpdate
from dispatcher.dispatchers.message_sent import TOPIC as MESSAGE_SENT_TOPIC
from aiokafka.producer.producer import AIOKafkaProducer
from forms.message import MessageForm


async def send_message_event_to_kafka(
    producer: AIOKafkaProducer,
    message: MessageForm
) -> None:
    await producer.send_and_wait(
        MESSAGE_SENT_TOPIC,
        MessageSentUpdate(
            message=message
        ).model_dump_json().encode()
    )

