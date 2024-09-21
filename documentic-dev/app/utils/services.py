import logging

from aiobotocore.session import get_session
from decouple import config

logger = logging.getLogger(__name__)


async def save_to_s3_bucket(raw_pdf_content: str, product_slug: str,
                            transaction_id: str, file_name: str):
    logger.info(f"uploading policy pdf on s3 bucket for transaction_id {transaction_id}")
    bucket = config('BUCKET_NAME', default="sleep-dev")
    key = f"documents/{product_slug}/{transaction_id}/{file_name}"

    session = get_session()
    async with session.create_client('s3') as client:
        logger.info(f"bucket_name: {bucket}, key: {key}, session: {session} and s3 client: {client}")
        response = await client.put_object(Bucket=bucket, Key=key, Body=raw_pdf_content)
        logger.info(f"response of s3 upload is {response}")
        if response.get('ResponseMetadata'):
            meta_data = response.get('ResponseMetadata')
            status_code = meta_data.get('HTTPStatusCode')
            if status_code and status_code == 200:
                url = config("DOWNLOAD_URL", default="http://cabinet.sleepdev.renewbuy.in/api/v1/get_document/{}")
                policy_download_url = url.format(key)
                logger.info(f"download url for pdf is {policy_download_url}")
                return policy_download_url
