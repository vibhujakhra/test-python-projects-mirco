import logging
import uuid
from typing import Union

from fastapi import APIRouter, status, Request
from rb_utils.async_http_client import AsyncHttpClient

from app.models.generate_policy import PolicyPDFStatus
from app.repository.services import DocumentStatusServices
from app.schemas.generate_policy import GeneratePolicyRequest, GeneratePolicyResponse, \
    GeneratePolicyValidationErrorResponse, PremiumBreakup, PremiumBreakupResponse
from app.settings import SERVICE_CREDENTIALS
from app.worker.main import process_request
from app.worker.motor.policy_pdf_generation import create_premium_breakup_pdf

motor_policy_router = APIRouter()
logger = logging.getLogger("api")


@motor_policy_router.post("/policy", status_code=status.HTTP_200_OK)
async def generate_policy(req: Request, request: GeneratePolicyRequest) -> Union[
    GeneratePolicyResponse, GeneratePolicyValidationErrorResponse]:
    """
    The generate_policy function is used to generate a policy pdf for the given transaction_id.
        It first creates a document object in the database with status IN_PROGRESS and then calls
        cleverbridge api to get transaction data. After that it validates if all required fields are present or not,
        if any field is missing then it returns validation error response else it updates document status as IN_PROGRESS,
        generates uuid for policy pdf and sends request to celery task queue.

    :param req: Request: Get the request context
    :param request: GeneratePolicyRequest: Get the transaction_id from the request body
    :return: A generatepolicyresponse object
    """
    request_data = request.dict()
    transaction_id = request_data.get('transaction_id')
    logger.info(f"Generating policy pdf for transaction_id {transaction_id}")

    document = await DocumentStatusServices.create_document(data=request_data)
    service_url = SERVICE_CREDENTIALS["cleverbridge"]["dns"] + f"/api/v1/get-detailed-transaction/{transaction_id}"
    transaction_data = await AsyncHttpClient.get(url=service_url)
    logger.info(f"Fetching data from get_detailed_transaction for transaction_id: {transaction_id}")

    transaction_data.update(document_id=document.id)

    validation_data = DocumentStatusServices.check_validations(data=transaction_data, transaction_id=transaction_id)
    if not validation_data.get('status'):
        document_status = PolicyPDFStatus.VALIDATION_ERROR.name
        request_data.update({"current_state": document_status})
        logger.info(f"updating document status for transaction_id: {transaction_id}")
        await DocumentStatusServices.update_document(data=request_data, obj=document)

        return GeneratePolicyValidationErrorResponse(**validation_data)

    document_status = PolicyPDFStatus.IN_PROGRESS.name
    policy_uuid = str(uuid.uuid4())
    request_data.update(
        {
            "policy_uuid": policy_uuid,
            "current_state": document_status
        }
    )

    await DocumentStatusServices.update_document(data=request_data, obj=document)
    url = await process_request(request=req, data=transaction_data)
    logger.info(f"Fetching policy pdf url for transaction_id: {transaction_id}")
    # await send_one(data=transaction_data)
    return GeneratePolicyResponse(status="success", policy_download_url=url)


@motor_policy_router.post("/premium_breakup_url/")
async def get_premium_breakup_url(request: PremiumBreakup) -> PremiumBreakupResponse:
    """
    The get_premium_breakup_url function is used to generate a premium breakup pdf for the given quote id.
        Args:
            request (PremiumBreakup): The request object containing the quote_id and selected_addon_id.

    :param request: PremiumBreakup: Get the quote_id and selected_addon_id
    :return: The url of the premium breakup pdf
    """
    quote_id = request.quote_id
    logger.info(f"Generating premium breakup for quote id {quote_id}")
    service_url = SERVICE_CREDENTIALS["quotes"][
                      "dns"] + f"/api/v1/get_premium_breakup_preview/?quote_request_id={request.quote_request_id}&quote_id={quote_id}"
    if request.selected_addon_id:
        service_url += f"&selected_addon_id={request.selected_addon_id}"
    result_data = await AsyncHttpClient.get(url=service_url)
    url = await create_premium_breakup_pdf(request=result_data)
    logger.info(f"Fetching policy pdf url for quote_id: {quote_id}")
    return PremiumBreakupResponse(status="success", premium_breakup_url=url)
