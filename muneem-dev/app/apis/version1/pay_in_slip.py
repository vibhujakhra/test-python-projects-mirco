import logging
from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, Request
from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.payment import PaymentState, PaymentMode, Payment, Billing, PayInSlip, CHEQUE_TYPE_ENUM
from app.schemas.pay_in_slip import GeneratePayInSlipRequest, MultipleChequeDetailSchema, ChequeIDRequest, \
    ViewPayInSlipResponse, UpdateChequeRequest, UpdateChequeResponse, MultipleViewPayInSlipResponse, PDFURLResponse, \
    GetPayInSlipQueryParam
from app.services.payment import send_payment_data_to_insurer, get_cheque_data
from app.utils.code_utils import ChequeDetailServices, ChequeDetails, PaymentServices, BillingServices, \
    check_insurer_payment_integrated, get_detail_pay_in_slip_data, get_search_data, get_query_result, \
    prepare_pay_in_slip_pdf
from app.utils.exceptions import ChequeNotFoundException

router = APIRouter()
logger = logging.getLogger("api")


# @router.get('/cheque_details/', response_model=ChequeDetailSchema) #TODO: Under observation
@router.get('/cheque_details/')
async def get_check_details(request: Request, transaction_type_id: int, insurer_code: str):
    logger.info(f"Get cheque details for transaction_type_id: {transaction_type_id} and insurer_code: {insurer_code}")
    data = await get_cheque_data(request=request, transaction_type_id=transaction_type_id, insurer_code=insurer_code)
    return data

@router.post('/multiple_cheque_details/', response_model=MultipleChequeDetailSchema)
async def get_multiple_cheque_details(request: ChequeIDRequest):
    logger.info("Get Multiple cheque details for request_data")
    complete_data = []
    request_body = request.dict()
    cheque_id = request_body['cheque_id']
    billing_id = request_body['billing_id']

    cheque = await ChequeDetails.fetch(key=cheque_id)
    cheque_type = CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE.value
    complete_data.append({"cheque_id": cheque.id, "cheque_type": cheque_type})
    if billing_id:
        cheque_type = CHEQUE_TYPE_ENUM.DEALER_CHEQUE.value
        complete_data[0].update({"cheque_id": cheque.id, "cheque_type": cheque_type, "billing_id": billing_id})

    data = {"data": await ChequeDetailServices.get_payment(complete_data=complete_data, sub_payment_data=True)}
    return data


@router.post('/generate_pay_in_slip/')
async def generate_pay_in_slip(req: Request, request: GeneratePayInSlipRequest) -> Union[ViewPayInSlipResponse, dict]:
    logger.info(f"Genrating pay in slip for insurer : {request.insurer_code}")
    request_body = request.dict()
    cheque_ids = request_body['cheque_ids']
    insurer_code = request_body['insurer_code']
    transaction_type_id = request_body['transaction_type_id']
    is_payment_integrated = await check_insurer_payment_integrated(insurer_code=insurer_code)

    if not cheque_ids:
        logger.info("No cheque found for pay in slip creation")
        raise ChequeNotFoundException(message="No cheque found for pay in slip creation")

    # checking validation of either pay in slip is already generated or not
    # against the given cheque ids
    cheque = await ChequeDetails.fetch(key=cheque_ids[0])
    if cheque.pay_in_slip_id is not None:
        logger.info(f"Pay-In Slip already generated against cheque no.: {cheque.cheque_number}")
        return {"message": f"Pay-In Slip already generated against cheque no.: {cheque.cheque_number}"}

    pay_in_slip = await PayInSlip.create(**{"insurer_code": insurer_code.upper(),
                                            "transaction_type_id": transaction_type_id})
    slip_number = insurer_code.upper() + "_" + str(pay_in_slip.id)
    await ChequeDetails.update_all(cheque_ids, **{"pay_in_slip_id": pay_in_slip.id})

    cheques = []
    pay_in_slip_amount = 0
    payment_state = await PaymentState.fetch_by_code(code='vb64_pending')
    for cheque_id in cheque_ids:
        cheque = await ChequeDetails.fetch(key=cheque_id)
        pay_in_slip_amount += cheque.cheque_amount
        cheques.append(cheque)

        payments = []
        # updating payment state for each and every payment which belongs to above pay in slip
        if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
            payments = await PaymentServices.get_by_cheque_id(cheque_id=cheque.id)
        elif cheque.cheque_type == CHEQUE_TYPE_ENUM.DEALER_CHEQUE:
            billing = await BillingServices.get_by_cheque_id(cheque_id=cheque.id)
            payments = await PaymentServices.get_by_billing_id(billing_id=billing.id)

        if is_payment_integrated:
            await send_payment_data_to_insurer(cheque=cheque, payments=payments, pay_in_slip_number=slip_number)

        payment_ids = [payment.id for payment in payments]
        await Payment.update_all(payment_ids, **{"payment_state": payment_state.id})

    slip_number = insurer_code.upper() + "_" + str(pay_in_slip.id)
    pay_in_slip_data = {"pay_in_slip_amount": pay_in_slip_amount, "slip_number": slip_number}

    await PayInSlip.update(key=pay_in_slip.id, **pay_in_slip_data)
    pay_in_slip = await PayInSlip.fetch(key=pay_in_slip.id)
    logger.info(f"Pay in slip is generated with pay_in_slip number: {slip_number}")
    return await get_detail_pay_in_slip_data(request=req, cheques=cheques, pay_in_slip=pay_in_slip)


@router.patch('/update_cheque/', response_model=UpdateChequeResponse)
async def update_cheque(request: UpdateChequeRequest):
    logger.info( f"Updating requested cheque for cheque_id: {request.cheque_id}")
    request_body = request.dict()
    cheque_id = request_body.pop('cheque_id')
    request_body = {key: value for key, value in request_body.items() if value}
    if request_body.get("cheque_date"):
        request_body['cheque_date'] = datetime.strptime(request_body['cheque_date'], "%d-%m-%Y")

    await ChequeDetails.update(cheque_id, **request_body)
    updated_cheque = await ChequeDetails.fetch(key=cheque_id)
    dataverse_data = await ChequeDetailServices.get_policy_summary_data(_ids=[("bank_id", updated_cheque.bank_id)])
    updated_cheque_data = {"cheque_id": cheque_id,
                           "cheque_number": updated_cheque.cheque_number,
                           "cheque_date": updated_cheque.cheque_date.strftime("%d-%m-%Y"),
                           "account_number": updated_cheque.account_number,
                           "bank": dataverse_data['bank'].get('name'),
                           "bank_branch_and_city": updated_cheque.bank_branch_and_city}

    return updated_cheque_data


@router.get('/pay_in_slip_details/', response_model=MultipleViewPayInSlipResponse)
async def get_pay_in_slip_details(request: Request, query_param: GetPayInSlipQueryParam = Depends()):
    logger.info("Fetching pay in slip details as per request")
    search_data = await get_search_data(request=request, query_params=query_param)
    query_result = await get_query_result(request=request, data=search_data)
    logger.info( "Successfully get the Requested pay in slip details")
    return {"data": query_result}


@router.get('/ic_pay_in_slip_details/', response_model=MultipleViewPayInSlipResponse)
async def get_pay_in_slip_details(request: Request, query_param: GetPayInSlipQueryParam = Depends()):
    logger.info( "Fetching IC pay in slip details as per request")
    insurer_code = request.headers.get('X-Insurer-Code')
    search_data = await get_search_data(request=request, query_params=query_param, insurer_code=insurer_code)
    query_result = await get_query_result(request=request, data=search_data)
    logger.info( "Successfully fetched IC pay in slip details as per request")
    return {"data": query_result}


@router.get('/pay_in_slip_pdf/', response_model=PDFURLResponse)
async def get_pay_in_slip_pdf(request: Request, pay_in_slip_id: str):
    logger.info( f"Requested pay in slip pdf for pay_in_slip_id : {pay_in_slip_id}")
    pay_in_slip = await PayInSlip.fetch(key=int(pay_in_slip_id))
    cheque = await ChequeDetailServices.get_by_pay_in_slip_id(pay_in_slip_id=int(pay_in_slip_id))
    context_payload = await get_detail_pay_in_slip_data(request, cheques=cheque, pay_in_slip=pay_in_slip)

    pdf_url = await prepare_pay_in_slip_pdf(context_data=context_payload, slip_number=pay_in_slip.slip_number)
    logger.info("Pay in slip pdf url generated ")
    return {"pdf_url": pdf_url}


@router.get('/fetch_policy_feed_file_transactions/')
async def get_policy_feed_file_transactions(insurer_code: str, generation_date: str):
    """
    The get_policy_feed_file_transactions function returns a list of transaction ids for the given insurer code and date.
    The transactions are filtered by payment mode, pay in slip id, cheque details id and billing detail id.

    :param request: Request: Get the request object
    :param insurer_code: str: Fetch the insurer code from the request
    :param generation_date: str: Get the transaction ids for a particular date
    :return: A list of transaction ids

    """
    logger.info( f"Fetching list of transaction ids for the given insurer code: {insurer_code} and date: {generation_date}")
    response = []
    allowed_payment_mode = (await sqldb.execute(
        select(PaymentMode.code, PaymentMode.id).where(PaymentMode.code.in_(["CC", "DC", "online_payment"])))).all()
    allowed_payment_mode = {code: obj_id for code, obj_id in allowed_payment_mode}
    start_date = datetime.strptime(f"{generation_date} 00:00:00", "%d-%m-%Y %H:%M:%S")
    end_date = datetime.strptime(f"{generation_date} 23:59:59", "%d-%m-%Y %H:%M:%S")
    response += (await sqldb.execute(
        select(Payment.transaction_id).filter(
            Payment.created_at >= start_date, Payment.created_at <= end_date,
            Payment.insurer_code == insurer_code, Payment.payment_mode.in_(
                [allowed_payment_mode["CC"], allowed_payment_mode["online_payment"]]
            )))).scalars().all()

    pay_in_slip_ids = (await sqldb.execute(select(PayInSlip.id).where(
        PayInSlip.created_at >= start_date, PayInSlip.created_at <= end_date,
        PayInSlip.insurer_code == insurer_code))).scalars().all()
    cheque_detail_ids = (await sqldb.execute(
        select(ChequeDetails.id).where(ChequeDetails.pay_in_slip_id.in_(pay_in_slip_ids)))).scalars().all()
    billing_detail_ids = (
        await sqldb.execute(select(Billing.id).where(Billing.cheque_id.in_(cheque_detail_ids)))).scalars().all()

    response += (await sqldb.execute(
        select(Payment.transaction_id).filter(
            Payment.payment_mode == allowed_payment_mode["DC"],
            Payment.billing_id.in_(billing_detail_ids))
    )).scalars().all()

    return set(response)
