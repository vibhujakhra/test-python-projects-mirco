import aioboto3

from schemas.cabinet import ValidationResponse
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME


def get_async_s3_client():
    """
    The get_async_s3_client function returns an aioboto3.Session object that can be used to interact with AWS S3.
    :return: An async_s3_session object
    """
    async_s3_session = aioboto3.Session(
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        region_name=REGION_NAME
        )
    return async_s3_session


def check_validation(product_slug: str, file_extension: str) -> ValidationResponse:
    """
    The check_validation function checks if the product slug and file extension are valid.
        Args:
            product_slug (str): The name of the product for which a document is being uploaded.
            file_name (str): The name of the document being uploaded.
            file_extension (str): The extension of the document being uploaded, e.g.,".png", ".jpg", ".jpeg",".zip"

    :param product_slug: str: Check if the product slug is in the allowed_product_list
    :param file_name: str: Check if the file name is valid
    :param file_extension: str: Check if the file extension is allowed
    :return: A validation response object
    """
    allowed_product_list = ["health", "motor", "life", "insurer_dg_signature", "discount_document"]
    allowed_file_extension = [".png", ".jpg", ".jpeg", ".pdf", ".zip"]
    if product_slug not in allowed_product_list:
        return ValidationResponse(is_valid=False, error_message=f"{product_slug} is not a allowed product slug.")
    if file_extension not in allowed_file_extension:
        return ValidationResponse(is_valid=False, error_message=f"{file_extension} in not a allowed file format.")
    return ValidationResponse(is_valid=True)

