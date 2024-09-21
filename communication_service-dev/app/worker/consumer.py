import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from rb_utils.database import initiate_database

from app.schemas.communication import BaseCommunicationRequest
from app.settings import CONNECTION_CONFIG
from app.settings import KAFKA
from app.utils.process import Communicator

logger = logging.getLogger("consumer")


async def get_consumer() -> AIOKafkaConsumer:
    return AIOKafkaConsumer(*KAFKA['topic'].values(), bootstrap_servers=KAFKA["bootstrap_servers"])


async def consumer_data():
    consumer = await get_consumer()
    await consumer.start()
    try:
        initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
        async for received_data in consumer:
            data = json.loads(received_data.value)
            if data.get("email"):
                await Communicator.send_email(communication_data=BaseCommunicationRequest(**data))
            if data.get("mobile"):
                if data.get("on_whatsapp"):
                    await Communicator.send_whatsapp(communication_data=BaseCommunicationRequest(**data))
                else:
                    await Communicator.send_sms(communication_data=BaseCommunicationRequest(**data))
    finally:
        await consumer.stop()


if __name__ == '__main__':
    asyncio.run(consumer_data())
