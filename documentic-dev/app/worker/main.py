import logging

from aiokafka import AIOKafkaConsumer
from decouple import config

from .motor.cancellation_pdf_generation import create_pdf as create_cancellation_pdf
from .motor.endorsement_pdf_generation import create_pdf as create_endorsement_pdf
from .motor.policy_pdf_generation import create_pdf as create_policy_pdf

consumer = None
topic = config("KAFKA_TOPIC", default="policy_generation_data")
bootstrap_server = config("KAFKA_BROKER", default="broker:9092")
logger = logging.getLogger("worker")


async def get_consumer() -> AIOKafkaConsumer:
    """
    The get_consumer function is a helper function that returns the consumer object.
        If the consumer object has not been created yet, it will create one and return it.
        Otherwise, if the consumer already exists, then it will simply return that existing
        instance of the AIOKafkaConsumer class.

    :return: A consumer object
    """
    global consumer
    if consumer:
        return consumer

    return AIOKafkaConsumer(topic, bootstrap_servers=bootstrap_server)


async def process_request(request, data, endorsement=False, cancellation=False):
    """
    The process_request function is used to create a PDF document from the data provided.
        The function takes in three parameters: request, data and endorsement.

    :param request: Get the request object that is sent to the api
    :param data: Pass the request data to the pdf creation function
    :param endorsement: Determine whether the request is for an endorsement or not
    :param cancellation: Determine if the request is a cancellation or not
    :return: A pdf file
    """
    logger.info(f"Creating PDF for given data: {data}")
    if endorsement:
        return await create_endorsement_pdf(request=data)
    if cancellation:
        return await create_cancellation_pdf(req=request, request=data)

    return await create_policy_pdf(req=request, request=data)

# async def main():
#     logger.info("starting worker...")
#     await async_db_session.init()
#     consumer = await get_consumer()

#     try:
#         await consumer.start()
#     except Exception as e:
#         logger.exception(e)
#         raise e

#     try:
#         async for data in consumer:
#             await process_request(data=data)

#     except Exception as e:
#         logger.exception(e)
#     finally:
#         await consumer.stop()


# if __name__ == '__main__':
#     asyncio.run(main())
