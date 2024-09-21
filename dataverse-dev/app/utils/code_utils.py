import aioboto3

from app.schemas.admin_db_details import ValidationResponse


def get_async_s3_client():
    async_s3_session = aioboto3.Session()
    return async_s3_session


def check_validation(product_slug: str, file_name: str, file_extension: str) -> ValidationResponse:
    allowed_product_list = ["Insurance_Company_Logo"]
    allowed_file_extension = [".png", ".jpg", ".jpeg", ".pdf"]
    if product_slug not in allowed_product_list:
        return ValidationResponse(is_valid=False, error_message=f"{product_slug} is not a allowed product slug.")
    if file_extension not in allowed_file_extension:
        return ValidationResponse(is_valid=False, error_message=f"{file_extension} in not a allowed file format.")
    return ValidationResponse(is_valid=True)
