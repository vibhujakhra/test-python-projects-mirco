import json
import logging

from aiokafka import AIOKafkaProducer

from app.settings import KAFKA
from app.utils.exceptions import KafkaProducerException

logger = logging.getLogger("producer")


class AsyncKafkaProducer:

    @classmethod
    async def push_email_to_kafka_topic(cls, data: dict):

        producer = AIOKafkaProducer(bootstrap_servers=KAFKA["bootstrap_servers"])
        message_data = json.dumps(data)
        await producer.start()
        try:
            await producer.send_and_wait(KAFKA["topic"]["email_topic"], message_data.encode())
        except Exception as e:
            logger.exception(f"An exception occurred {e} while pushing message on topic with data: {data}")
            raise KafkaProducerException(name='sdk.producer.push_email_to_kafka_topic',
                                         message='Error occurred while producing a message')
        finally:
            await producer.stop()

    @classmethod
    async def push_otp_to_kafka_topic(cls, data: dict):
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA["bootstrap_servers"])
        message_data = json.dumps(data)
        await producer.start()
        try:
            await producer.send_and_wait(KAFKA["topic"]["otp_topic"], message_data.encode())
        except Exception as e:
            logger.exception(f"An exception occurred {e} while pushing message on topic with data: {data}")
            raise KafkaProducerException(name='sdk.producer.push_otp_to_kafka_topic',
                                         message='Error occurred while producing a message')
        finally:
            await producer.stop()
