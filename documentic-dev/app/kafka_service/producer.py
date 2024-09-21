import json

from aiokafka import AIOKafkaProducer

from app import settings
from app.utils.exceptions import KafkaPublishToQueueException

bootstrap_servers = settings.KAFKA.get('bootstrap_servers')
topic_name = settings.KAFKA.get('topic_name')
producer = None


async def get_producer() -> AIOKafkaProducer:
    """
    The get_producer function is a helper function that returns the global producer object.
    If the global producer object does not exist, it creates one and then returns it.

    :return: A producer object
    """
    global producer

    if producer:
        return producer

    return AIOKafkaProducer(bootstrap_servers=bootstrap_servers)


async def send_one(data):
    """
    The send_one function is a coroutine that takes in a data object and publishes it to the Kafka topic.
        The function first gets the producer, then encodes the data into JSON format. It then starts
        producing messages and sends them to the topic_name variable defined above. If an error occurs,
        it raises an exception with information about what went wrong.

    :param data: Pass the data to be sent to kafka
    :return: A coroutine that can be awaited
    """
    producer = await get_producer()
    data = json.dumps(data)

    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait(topic_name, data.encode())
    except Exception as e:
        raise KafkaPublishToQueueException(name='app.db.kafka.base.publish_to_queue',
                                           message='Error occurred while producing a message')
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
