import logging

from fastapi import APIRouter, Request
from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.payment import *
from app.schemas.payment import *
from app.services.payment import get_billing_payment_details
from app.utils.code_utils import generate_pay_in_slip_number
from app.utils.exceptions import BillingStatusNotMappedException, InternalServerException

router = APIRouter()
logger = logging.getLogger("api")


@router.get("/get_billing_payments/")
async def get_billing_payments(request: Request,
                               transaction_type_id: int, insurer_code: str, payment_mode: int) -> list:
    logger.info(f"Get billing payments for transaction_type_id: {transaction_type_id}, insurer_code: {insurer_code}, payment_mode: {payment_mode}")
    try:
        billing_payments = await get_billing_payment_details(request=request, transaction_type_id=transaction_type_id,
                                                             insurer_code=insurer_code, payment_mode=payment_mode)
    except Exception as e:
        logger.exception("An exception occurred {e} while getting billing payments in method get_billing_payments")
        raise InternalServerException(name='Error occured in getting billing payments',
                                    message=f"Error occurred while returning response due to exception :{ e }")


    return billing_payments


@router.post("/generate_billing/")
async def create_billing(request: CreateBillingRequest) -> CreateBillingResponse:
    logger.info("Generate billing with request data")
    billing_request = request.dict()
    payment_ids = billing_request.pop('payment_ids')
    query = select(PaymentState).where(PaymentState.code == 'pay_in_slip_pending')
    results = await sqldb.execute(query)
    (payment_state_obj,) = results.one()
    query = select(PaymentStatus).where(PaymentStatus.code == 'pending')
    results = await sqldb.execute(query)
    (payment_status_obj,) = results.one()
    query = select(PaymentMode.id).where(PaymentMode.code.in_(('online_payment', "paylink")))
    results = await sqldb.execute(query)
    online_payment_modes = results.scalars().all()

    if request.payment_mode in online_payment_modes:
        billing_details = await Billing.create(
            **{"insurer_code": billing_request['insurer_code'], "amount": request.cheque_amount,
               "billing_status": payment_status_obj.id})
    else:
        billing_request.update({
            'transaction_type_id': billing_request['transaction_type_id'] or 1,
            'cheque_type': CHEQUE_TYPE_ENUM.DEALER_CHEQUE,
            "unique_reference_number": generate_pay_in_slip_number(insurer_code=billing_request['insurer_code']),
            "payment_status": payment_status_obj.id
        })
        if billing_request.get("payment_mode"):
            billing_request.pop("payment_mode")
        cheque_details = await ChequeDetails.create(**billing_request)
        billing_details = await Billing.create(
            **{"insurer_code": billing_request['insurer_code'], "cheque_id": cheque_details.id,
               "amount": request.cheque_amount})

    await Payment.update_all(keys=payment_ids, **{"billing_id": billing_details.id, "payment_state": payment_state_obj.id})
    logger.info("Billing has been generated successfully")

    return CreateBillingResponse(
        billing_id=billing_details.id,
        status_code=200,
        message='Billing has been generated successfully'
    )


@router.get("/get_billing_status/")
async def get_billing_status(billing_id: int) -> PaymentStateResponse:
    logger.info(f"Getting billing status for id: {billing_id}")
    billing = await Billing.fetch(key=billing_id)
    if billing.billing_status:
        billing_status = await PaymentStatus.fetch(key=billing.billing_status)
        return PaymentStateResponse(**billing_status.__dict__, amount=billing.amount)
    else:
        logger.info(f"Exception occured while getting billing status for billing id: {billing_id}")
        raise BillingStatusNotMappedException(name='app.apis.version1.billing', message='billing status is not mapped')
