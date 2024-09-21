import pathlib
import os
from botocore.client import BaseClient
from fastapi import APIRouter, Depends, status
from fastapi.datastructures import UploadFile
from fastapi.responses import RedirectResponse

from schemas.cabinet import *
from settings import DOCUMENT_DNS_CONFIG, BUCKET_NAME, EXPIRY_TIME
from utils.code_utils import get_async_s3_client, check_validation

router = APIRouter()


@router.post("/upload_document", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, product_slug: str, transaction_id: str, file_name: str,
                      async_s3_client: BaseClient = Depends(get_async_s3_client)) -> AssestUploadResponse:
    """
            The upload_file function is used to upload a file to the S3 bucket.
                The function takes in the following parameters:
                    - file: This is an UploadFile object that contains information about the uploaded file.
                            It can be accessed using .file and .filename attributes of this object.
                            For more details, refer https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile-object

            :param file: UploadFile: Get the file from the request
            :param product_slug: str: Identify the product
            :param transaction_id: str: Identify the transaction
            :param file_name: str: Specify the name of the file that will be uploaded to s3
            :param async_s3_client: BaseClient: Get the async_s3_client object
            :return: A tuple of the status code and the document url
        """
    product_slug = product_slug.lower()
    file_name = file_name.lower()

    if file:
        file_extension = pathlib.Path(file.filename).suffix
        validation_check = check_validation(product_slug=product_slug,
                                            file_extension=file_extension)
        file_path = f"documents/{product_slug}/{transaction_id}/{file_name}"

        if not validation_check.is_valid:
            return AssestUploadResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                        error_message=validation_check.error_message)

        async with async_s3_client.client("s3") as s3:
            response = await s3.list_objects_v2(Bucket=BUCKET_NAME,
                                                Prefix=f"documents/{product_slug}/{transaction_id}/{file_name}")
            file_path_prefix = f"{DOCUMENT_DNS_CONFIG}/get_document"
            if 'Contents' in response:
                # "Contents" key specifically refers to a list of objects in the bucket that match the specified prefix
                existing_file_path = response['Contents'][0]['Key']
                existing_filename, existing_file_extension = os.path.splitext(existing_file_path)
                object_key_old = f"documents/{product_slug}/{transaction_id}/rejected_{file_name}{existing_file_extension}"
                await s3.copy_object(Bucket=BUCKET_NAME,
                                     CopySource=f"{BUCKET_NAME}/{file_path}{existing_file_extension}",
                                     Key=object_key_old)
                await s3.delete_object(Bucket=BUCKET_NAME, Key=existing_file_path)
            await s3.upload_fileobj(file.file, BUCKET_NAME, f"{file_path}{file_extension}")

            return AssestUploadResponse(status_code=status.HTTP_201_CREATED,
                                        document_url=f"{file_path_prefix}/{file_path}{file_extension}",
                                        old_document_url=f"{file_path_prefix}/{object_key_old}" if 'Contents' in response else None
                                        )


@router.get("/get_document/")
async def get_document(document_url: str, async_s3_client: BaseClient = Depends(get_async_s3_client)):
    """
    The get_document function is used to generate a presigned URL for an S3 object.
    The function takes in the document_url parameter, which is the path of the file on S3.
    It also takes in an async_s3_client parameter, which is a boto client that has been configured with
        AWS credentials and region information. This client can be passed into this function using dependency injection
        by calling Depends(get_async_s3_client).

    :param document_url: str: Specify the document to be downloaded
    :param async_s3_client: BaseClient: Pass in the async_s3_client object that was created by the get_async_s3_client function
    :return: A redirect response object that redirects to the signed url
    """
    async with async_s3_client.client("s3") as s3:
        url = await s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': document_url,
                'ResponseContentDisposition': 'attachment'
            },
            ExpiresIn=EXPIRY_TIME
        )
        return RedirectResponse(url)
