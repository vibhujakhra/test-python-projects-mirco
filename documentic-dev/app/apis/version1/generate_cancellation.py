import logging
from typing import Union

from fastapi import APIRouter, Request, status
from rb_utils.async_http_client import AsyncHttpClient

from app.schemas.generate_cancellation import GenerateCancellationRequest, GenerateCancellationResponse, \
    GenerateCancellationValidationErrorResponse
from app.settings import SERVICE_CREDENTIALS
from app.worker.main import process_request

motor_cancellation_router = APIRouter()

logger = logging.getLogger("api")


@motor_cancellation_router.post("/cancellation", status_code=status.HTTP_200_OK)
async def generate_cancellation(req: Request,request: GenerateCancellationRequest) -> Union[
    GenerateCancellationResponse, GenerateCancellationValidationErrorResponse]:
    """
    The generate_cancellation function is used to generate a cancellation document for the policy.
        It takes in a GenerateCancellationRequest object and returns either a GenerateCancellationResponse or
        an error response if there was an issue with the request.

    :param request: GenerateCancellationRequest: Get the cancellation number from the request
    :return: A url to the generated cancellation document
    """
    service_url = SERVICE_CREDENTIALS["policy"][
                      "dns"] + f"/api/v1/get_cancellation_preview/?cancellation_number={request.cancellation_number}"
    transaction_data = await AsyncHttpClient.get(url=service_url)
    transaction_data["user_id"] = ""
    if req.headers.get("user_id"):
        transaction_data["user_id"] = req.headers['user_id']
    url = await process_request(request=request, data=transaction_data, cancellation=True)
    transaction_id = transaction_data["cancellation_obj"]['transaction_id']
    logger.info(f"Created Cancellation pdf url for transaction_id: {transaction_id}")
    return GenerateCancellationResponse(status="success", cancellation_download_url=url)
