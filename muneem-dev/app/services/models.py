import logging
from typing import List

from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.payment import Billing, ChequeDetails, CHEQUE_TYPE_ENUM, Payment
from app.services.user_services import get_user_details
from app.settings import SERVICE_CREDENTIALS
from app.utils.exceptions import *

logger = logging.getLogger(__name__)


class ChequeDetailServices:

    @classmethod
    async def fetch_cheque_details(cls, request, transaction_type: int, insurer_code: str, cheque_id: int = None):
        try:
            user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
            query = select(ChequeDetails)
            if user_details["dealer_code"]:
                query = query.filter(ChequeDetails.dealer_code == user_details["dealer_code"])
            if cheque_id:
                query = query.filter(ChequeDetails.id == cheque_id)
            query = query.where(ChequeDetails.transaction_type_id == transaction_type,
                                ChequeDetails.insurer_code == insurer_code,
                                ChequeDetails.pay_in_slip_id == None)
            cheque_details = await sqldb.execute(query)
            return cheque_details.scalars().all()
        except Exception as e:
            logger.exception(f"Error Occured while fetching the details for cheque.")
            raise ChequeDetailsException(f"Exception occured while fetching cheque details for \
                                         transaction_type: {transaction_type} and insurer_code: {insurer_code}")

    @classmethod
    async def segregate_cheque_ids(cls, query_list: list) -> tuple:
        bank_cache = {}
        customer_data, dealer_data = [], []
        for cheque in query_list:
            if bank_cache.get(cheque.bank_id) is None:
                dataverse_data = await ChequeDetailServices.get_policy_summary_data(_ids=[("bank_id", cheque.bank_id)])
                bank_cache[cheque.bank_id] = dataverse_data['bank'].get('name')

            if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
                customer_data.append({
                    "cheque_id": cheque.id,
                    "cheque_number": cheque.cheque_number,
                    "bank": bank_cache[cheque.bank_id],
                    "bank_id": cheque.bank_id,
                    "bank_branch_and_city": cheque.bank_branch_and_city,
                    "cheque_date": cheque.cheque_date.strftime("%d-%m-%Y"),
                    "cheque_type": CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE.value,
                    "account_number": cheque.account_number,
                    "cheque_amount": cheque.cheque_amount,
                    "paid_by": "customer",
                    "billing_id": None
                })

            if cheque.cheque_type == CHEQUE_TYPE_ENUM.DEALER_CHEQUE:
                dealer_data.append({
                    "cheque_id": cheque.id,
                    "cheque_number": cheque.cheque_number,
                    "bank": bank_cache[cheque.bank_id],
                    "bank_id": cheque.bank_id,
                    "bank_branch_and_city": cheque.bank_branch_and_city,
                    "cheque_date": cheque.cheque_date.strftime("%d-%m-%Y"),
                    "cheque_type": CHEQUE_TYPE_ENUM.DEALER_CHEQUE.value,
                    "cheque_amount": cheque.cheque_amount,
                    "account_number": cheque.account_number,
                    "paid_by": "dealer",
                    "billing_id": None,
                })

        return (customer_data, dealer_data)

    @classmethod
    async def get_payment(cls, complete_data: List[dict], sub_payment_data: bool = False) -> List[dict]:
        for data in complete_data:
            query = select(Payment)
            if data['cheque_type'] == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE.value:
                query = query.where(Payment.cheque_id == data['cheque_id'])
            elif data['cheque_type'] == CHEQUE_TYPE_ENUM.DEALER_CHEQUE.value:
                query = query.where(Payment.billing_id == data['billing_id']).group_by(Payment.id)
            else:
                raise PayInDataNotFoundException(name="db.service.pay_in_slip.get_payment",
                                                 message="Cheque and billing id not found.")
            payment_details = await sqldb.execute(query)
            payments = payment_details.scalars().all()
            if sub_payment_data:
                # in this case, need to show only parent row data as well as sub row data
                sub_payment_data = []
                for payment in payments:
                    payment_data = {}
                    policy_start_date = payment.policy_start_date
                    policy_end_date = payment.policy_end_date
                    policy_period = policy_start_date.strftime("%d-%m-%Y") + " - " + policy_end_date.strftime(
                        "%d-%m-%Y")
                    payment_data.update(
                        {"payment_amount": payment.payment_amount, "policy_number": payment.policy_number,
                         "policy_period": policy_period, "insured_name": payment.insured_name,
                         "endorsement_number": payment.endorsement_number})
                    sub_payment_data.append(payment_data)
                return sub_payment_data
            else:
                # in this case, need to show only parent row data
                if not payments:
                    logger.info(f"No payment found with billing id {data['billing_id']} for pay in slip creation")
                    continue

                sub_payment_count = len(payments)
                payment = payments[0]
                policy_start_date = payment.policy_start_date
                policy_end_date = payment.policy_end_date
                policy_period = policy_start_date.strftime("%d-%m-%Y") + " - " + policy_end_date.strftime("%d-%m-%Y")
                data.update({"policy_number": payment.policy_number, "policy_period": policy_period,
                             "insured_name": payment.insured_name, "sub_payment_count": sub_payment_count,
                             "endorsement_number": payment.endorsement_number})

        return complete_data

    @classmethod
    async def get_billing(cls, cheque_data: List[dict]):
        for cheque in cheque_data:
            try:
                query = select(Billing)
                query = query.where(Billing.cheque_id == cheque['cheque_id'])
                billing_details = await sqldb.execute(query)
                (billing,) = billing_details.one()
                cheque.update({"billing_id": billing.id})
            except Exception as e:
                logger.exception(f"Error Occured while fetching the details for billing.")
                raise ChequeDetailsException(f"Exception occured while fetching billing details for \
                                             cheque_id: {cheque['cheque_id']}")

    @classmethod
    async def get_policy_summary_data(cls, _ids: list) -> dict:
        uri = "/api/v1/policy_summary?"
        for id in _ids:
            uri += (id[0] + "=" + str(id[1]) + "&")

        logger.info(f"uri formed for data fetching is {uri}")
        service_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + uri
        policy_summary_details = await AsyncHttpClient.get(url=service_url)
        return policy_summary_details

    @classmethod
    async def get_user_details_by_code(cls, code: str) -> dict:
        uri = f"/api/v1/get_user_codes/?dealer_code={code}"
        service_url = SERVICE_CREDENTIALS["auth"]["dns"] + uri
        user_data = await AsyncHttpClient.get(url=service_url)
        return user_data

    @classmethod
    async def get_by_pay_in_slip_id(cls, pay_in_slip_id: int):
        try:
            query = select(ChequeDetails)
            query = query.where(ChequeDetails.pay_in_slip_id == pay_in_slip_id)
            cheque = await sqldb.execute(query)
            return cheque.scalars().all()
        except Exception as e:
            logger.exception(f"Error Occured while fetching cheque object.")
            raise ChequeDetailsException(f"Exception occured while fetching cheque object \
                                         for pay_in_slip_id: {pay_in_slip_id}")

    @classmethod
    async def get_detail_transactions(cls, transaction_id):
        logger = logging.getLogger('app')
        logger.info(f"fetching data for transaction_id: {transaction_id}")
        service_url = SERVICE_CREDENTIALS["cleverbridge"]["dns"] + f"/api/v1/get-transaction/{transaction_id}"
        transaction_data = await AsyncHttpClient.get(url=service_url)
        return transaction_data


class PaymentServices:

    @classmethod
    async def get_by_cheque_id(cls, cheque_id: int):
        try:
            query = select(Payment)
            query = query.where(Payment.cheque_id == cheque_id)
            payment = await sqldb.execute(query)
            return payment.scalars().all()
        except Exception as e:
            logger.exception(f"Error Occured while fetching payment object.")
            raise ChequeDetailsException(f"Exception occured while fetching payment object \
                                         for cheque_id: {cheque_id}")

    @classmethod
    async def get_by_billing_id(cls, billing_id: int):
        try:
            query = select(Payment)
            query = query.where(Payment.billing_id == billing_id)
            payment = await sqldb.execute(query)
            return payment.scalars().all()
        except Exception as e:
            logger.exception(f"Error Occurred while fetching payment object.")
            raise ChequeDetailsException(f"Exception occurred while fetching payment object \
                                         for billing_id: {billing_id}")


class BillingServices:

    @classmethod
    async def get_by_cheque_id(cls, cheque_id: int):
        try:
            query = select(Billing)
            query = query.where(Billing.cheque_id == cheque_id)
            billing = await sqldb.execute(query)
            (billing,) = billing.one()
            return billing
        except Exception as e:
            logger.exception(f"Error Occured while fetching billing object.")
            raise ChequeDetailsException(f"Exception occured while fetching billing object \
                                         for cheque_id: {cheque_id}")
