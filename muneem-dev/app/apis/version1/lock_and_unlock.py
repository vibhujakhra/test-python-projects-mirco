import logging
from app.models.payment import PaymentMode
from app.schemas.pay_in_slip import LockUnlockDealerResponse
from app.services.payment import get_payment_list
from app.utils.code_utils import sqldb, select, Payment, Billing, ChequeDetails
from datetime import datetime, timedelta
from fastapi import APIRouter, Request

router = APIRouter()
logger = logging.getLogger("api")


@router.get('/lock_and_unlock_dealer/')
async def lock_and_unlock_dealer(request: Request, dealer_code: str) -> LockUnlockDealerResponse:
    """
    The lock_and_unlock_dealer function checks if any payment is not tagged with billing_id or pay_in_slip_id is None.
    If some payments are locked due to payment tag, it returns a message and the list of payments that are locked.
    If some payments are locked due to pay-in-slip, it returns a message and the list of payments that are locked.
    Else, if all the payments have been unlocked, it returns an appropriate message.

    :param dealer_code: str: Get the dealer code of the user
    :return: A dictionary with the following keys:
    """
    logger.info(f"Locking and unlocking if any payment is not tagged, or pay in slip is not generated for dealer: {dealer_code}")
    target_date = datetime.utcnow().date() - timedelta(days=10)
    payments = (
        await sqldb.execute(
            select(Payment)
            .filter(
                Payment.dealer_code == dealer_code,
                Payment.policy_issuance_date >= target_date,
                Payment.policy_issuance_date <= datetime.utcnow().date(),
            )
        )
    ).scalars().all()

    locked_due_to_payment_tag = []
    locked_due_to_pay_in_slip = []
    online_payment_id = (await PaymentMode.fetch_by_code("online_payment")).id
    for payment in payments:
        billing_obj = await Billing.fetch(key=payment.billing_id) if payment.billing_id else None
        cheque_id = billing_obj.cheque_id if billing_obj else payment.cheque_id
        if not ((billing_obj and billing_obj.id) and payment.payment_mode is online_payment_id):
            if not cheque_id:
                # If cheque_id is None, payment is not tagged
                # Check if payment is older than T+2 days
                if payment.policy_issuance_date + timedelta(days=3) <= datetime.utcnow().date():
                    locked_due_to_payment_tag.append(payment)
            else:
                cheque_details = await sqldb.execute(
                    select(ChequeDetails).where(ChequeDetails.id == cheque_id))
                cheque_detail = cheque_details.scalars().first()
                # If cheque_id is not None, payment is tagged
                if not cheque_detail.pay_in_slip_id:
                    # If pay_in_slip_id is None, pay_in_slip has not been generated
                    if payment.modified_at + timedelta(days=1) <= datetime.utcnow():
                        locked_due_to_pay_in_slip.append(payment)

    if not (locked_due_to_payment_tag or locked_due_to_pay_in_slip):
        # If all payments are unlocked
        return LockUnlockDealerResponse(
            message="Dear user your account is unlocked.",
            issue_type=None,
            payments=None,
            status_code=200
        )

    payment_tagged_list = []
    issue_type = "payment_not_tagged" if locked_due_to_payment_tag else "pay_in_slip_not_generated"
    payment_mode_data = await PaymentMode.fetch_all()
    payment_mode_dict = {payment_mode.id: payment_mode.code for payment_mode in payment_mode_data}
    for payment in (locked_due_to_payment_tag or locked_due_to_pay_in_slip):
        billing_obj = await Billing.fetch(key=payment.billing_id) if payment.billing_id else None
        cheque_id = billing_obj.cheque_id if billing_obj else payment.cheque_id
        payment_dict = {"id": payment.id, "payment_mode": payment_mode_dict.get(payment.payment_mode),
                        "transaction_type_id": payment.transaction_type_id,
                        "insurer_code": payment.insurer_code, "payment_amount": payment.payment_amount,"cheque_id": cheque_id}
        payment_tagged_list.append(payment_dict)

    logger.info(f"Dealer account lock and unlock  operation has been done for dealer {dealer_code} ")
    return LockUnlockDealerResponse(
        message="Dear user your account is locked as the payment of below mentioned policies are pending ."
        if locked_due_to_payment_tag else "Dear user your account is locked as Pay In Slip of below mentioned "
                                          "payments has not been "
                                          "generated.",
        issue_type=issue_type,
        payments=await get_payment_list(request=request, payment_details=payment_tagged_list,
                                        issue_type=issue_type),
        status_code=200
    )
