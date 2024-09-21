import logging
from typing import Union

from fastapi import APIRouter, status, Request
from rb_utils.async_http_client import AsyncHttpClient

from app.schemas.generate_endorsement import GenerateEndorsementRequest, GenerateEndorsementResponse, \
    GenerateEndorsementValidationErrorResponse
from app.settings import SERVICE_CREDENTIALS
from app.worker.main import process_request

motor_endorsement_router = APIRouter()
logger = logging.getLogger("api")


@motor_endorsement_router.post("/endorsement", status_code=status.HTTP_200_OK)
async def generate_endorsement(req: Request, request: GenerateEndorsementRequest) -> Union[
    GenerateEndorsementResponse, GenerateEndorsementValidationErrorResponse]:
    """
    The generate_endorsement function is used to generate an endorsement for a policy.
        It takes in the following parameters:
            - request (GenerateEndorsementRequest): The GenerateEndorsementRequest object containing the
                endorsement number of the policy to be endorsed.

    :param req: Request: Get the request object
    :param request: GenerateEndorsementRequest: Pass the endorsement number to the generate_endorsement function
    :return: A generateendorsementresponse object
    """
    service_url = SERVICE_CREDENTIALS["policy"][
                      "dns"] + f"/api/v1/get_endorsement_preview/?endorsement_number={request.endorsement_number}"
    transaction_data = await AsyncHttpClient.get(url=service_url)
    transaction_data["user_id"] = ""
    if req.headers.get("user_id"):
        transaction_data["user_id"] = req.headers['user_id']
    url = await process_request(request=req, data=transaction_data, endorsement=True)
    transaction_id = transaction_data["endorsement_obj"]['transaction_id']
    logger.info(f"Created endorsement pdf url for transaction id: {transaction_id}")
    return GenerateEndorsementResponse(status="success", endorsement_download_url=url)
