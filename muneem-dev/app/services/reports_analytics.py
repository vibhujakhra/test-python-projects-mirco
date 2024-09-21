import logging

from datetime import datetime
from sqlalchemy import select, distinct
from sqlalchemy.orm import selectinload
from app.settings import SERVICE_CREDENTIALS
from rb_utils.database import sqldb
from rb_utils.async_http_client import AsyncHttpClient
from app.services.user_services import get_user_details
from app.utils.exceptions import *
from app.models.payment import VB64, Billing, VB64Record, Payment, ChequeDetails, PaymentMode
from app.schemas.reports_analytics import *

logger = logging.getLogger(__name__)


class ReportsAnalytics:

    @classmethod
    async def get_policy_summary(cls, user_id, start_date, end_date):
        """
        The get_policy_summary function is used to fetch the policy summary for a given date range.
        The function accepts two parameters start_date and end_date, which are used to get the policy summary for that date range.
        
        :param start_date: Specify the start date of the policy
        :param end_date: Fetch the policies that were created before or equal to the end_date
        :return: The transaction_ids of all the policies that are active in a given date range
        """
        logger = logging.getLogger("policy_summary")
        try:
            service_url = SERVICE_CREDENTIALS["policy"][
                            "dns"] + f"/api/v1/policy_by_date_range/?user_id={user_id}"
            request_body = {
                "start_date": start_date,
                "end_date": end_date
            }
            transaction_ids = await AsyncHttpClient.post(url=service_url, body=request_body)
            return transaction_ids
        except Exception as e:
            logger.exception(f"Error occurred while fetching transaction_id | Exception: {e}")


    @classmethod
    async def get_filtered_transactions(cls, zone_id, state_id, city_id, dealer_code, insurer_code, \
        transaction_ids):
        logger = logging.getLogger("policy_summary")
        try:
            service_url = SERVICE_CREDENTIALS["proposal"][
                            "dns"] + f"/api/v1/get_filtered_transactions/"
            request_body= {
                "zone_id": zone_id,
                "state_id": state_id,
                "city_id": city_id,
                "dealer_code": dealer_code,
                "insurer_code": insurer_code,
                "transactions_ids":transaction_ids
            }
            transaction_ids = await AsyncHttpClient.post(url=service_url, body=request_body)
            return transaction_ids["transaction_ids"]
        except Exception as e:
            logger.exception(f"Error occurred while fetching transaction_id | Exception: {e}")


    @classmethod
    async def vb_64_query(cls, request, filter_params):
        user_details = await get_user_details(user_id=request.headers.get('x-user-id'))

        date_from = filter_params.start_date + " 00:00:00"
        date_to = filter_params.end_date + " 23:59:59"
        report_type = { 1: "Policy", 2: "Endorsement"}

        try:
            policy_query = select(distinct(VB64Record.policy_number)).join(VB64).where(
                VB64.created_at >= datetime.strptime(date_from, "%d-%m-%Y %H:%M:%S"),
                VB64.created_at <= datetime.strptime(date_to, "%d-%m-%Y %H:%M:%S"))
        
            policy_numbers = (await sqldb.execute(policy_query)).scalars().all()

            transaction_ids = (await sqldb.execute(select(Payment.transaction_id).where(Payment.policy_number.in_(policy_numbers)))).scalars().all()

            if filter_params.created_date_from:
                policy_transactions = await cls.get_policy_summary(user_id=request.headers.get('x-user-id'), \
                    start_date=filter_params.created_date_from, end_date=filter_params.created_date_to)
                transaction_ids = list(set(policy_transactions).intersection(set(transaction_ids)))

            filtered_transactions = await cls.get_filtered_transactions(filter_params.zone_id, filter_params.state_id, \
                filter_params.city_id, filter_params.dealer_code, filter_params.insurer_code, transaction_ids)

            filtered_policies = (await sqldb.execute(select(Payment.policy_number).where(Payment.transaction_id.in_(filtered_transactions)))).scalars().all()
            vb64_list = select(VB64Record).where(VB64Record.policy_number.in_(filtered_policies)).options(
                selectinload(VB64Record.vb64))
            
            if filter_params.vb64_status:
                vb64_list = vb64_list.where(VB64Record.clearance_status == filter_params.vb64_status)
            vb64_list = (await sqldb.execute(vb64_list)).scalars().all()

            result = []
            for vb64_record_obj in vb64_list:
                temp_response = VB64Reports()
                payment_query = select(Payment).where(Payment.policy_number == vb64_record_obj.policy_number)
                if user_details["dealer_code"]:
                    payment_query = payment_query.where(Payment.dealer_code == user_details["dealer_code"])
                if user_details["insurer_code"]:
                    payment_query = payment_query.where(Payment.insurer_code == user_details["insurer_code"])
                payment_obj = (await sqldb.execute(payment_query.options(selectinload(Payment.payment_status_obj)).order_by(
                    Payment.created_at.desc()))).scalars().first()
                if not payment_obj:
                    continue

                if payment_obj.transaction_type_id == filter_params.transaction_type_id:
                    proposal_data = await AsyncHttpClient.get(url=SERVICE_CREDENTIALS["proposal"]["dns"]+\
                        f"/api/v1/get_proposal_by_transaction/{payment_obj.transaction_id}")

                    reports_data = (await AsyncHttpClient.get(url=SERVICE_CREDENTIALS["dataverse"]["dns"]+\
                        f"/api/v1/get_reports_data/?rto_id={proposal_data.get('rto_id')}"))

                    policy_reports_data = (await AsyncHttpClient.get(url=SERVICE_CREDENTIALS["policy"]["dns"]+\
                        f"/api/v1/get_policy_reports_data?transaction_id={payment_obj.transaction_id}"))

                    full_name = proposal_data.get("customer", {}).get("first_name")
                    middle_name = proposal_data.get("customer", {}).get("middle_name")
                    last_name = proposal_data.get("customer", {}).get("last_name")
                    if middle_name:
                        full_name += (" "+middle_name)
                    if last_name:
                        full_name+= (" "+ last_name)
                    pending_days = (datetime.now() - payment_obj.created_at).days
                    temp_response.zone = reports_data["rto_zone"]
                    temp_response.state = reports_data["state"]
                    temp_response.city = reports_data["city"]
                    temp_response.dealer = payment_obj.dealer_person
                    temp_response.insurance_company = payment_obj.insurer_name
                    temp_response.policy_no = f"`{payment_obj.policy_number}"
                    temp_response.start_date = payment_obj.policy_start_date
                    temp_response.issuance_date = payment_obj.policy_issuance_date
                    temp_response.payment_id = payment_obj.id
                    temp_response.bank_name = vb64_record_obj.bank_name
                    temp_response.customer_name = full_name
                    temp_response.vb_64_status = vb64_record_obj.clearance_status
                    temp_response.pending_days_count = pending_days
                    temp_response.clearance_date = vb64_record_obj.clearance_date
                    temp_response.upload_date = vb64_record_obj.vb64.upload_date
                    temp_response.gross_premium = payment_obj.payment_amount
                    temp_response.approval_status = policy_reports_data.get("endorsement_status")
                    temp_response.cancellation_status = policy_reports_data.get("cancellation_status")
                    temp_response.endorsement_no = f"`{payment_obj.endorsement_number}"
                    temp_response.type = report_type[filter_params.transaction_type_id]
                    temp_response.policy_payment_status = payment_obj.payment_status_obj.name if payment_obj.payment_status else None

                    if payment_obj.cheque_id:
                        cheque_obj = await ChequeDetails.fetch(key=payment_obj.cheque_id)
                
                        # temp_response.policy_payment_status = cheque_obj.payment_status
                    if payment_obj.billing_id:
                        billing_obj = await Billing.fetch(key=payment_obj.billing_id)
                        cheque_obj = await ChequeDetails.fetch(key=billing_obj.cheque_id)

                    if payment_obj.billing_id or payment_obj.cheque_id:
                        temp_response.unique_reference_no = cheque_obj.unique_reference_number
                        temp_response.cheque_date = cheque_obj.cheque_date
                        temp_response.bank_city = cheque_obj.bank_branch_and_city
                        temp_response.cheque_no = cheque_obj.cheque_number

                    if payment_obj.payment_mode:
                        payment_mode_obj = await PaymentMode.fetch(key=payment_obj.payment_mode)
                        temp_response.premium_source = payment_mode_obj.name
                    result.append(temp_response)
            if not result:
                return {"message": "VB Endorsement Records are not present for given date range"}
            return result
        except Exception as e:
            logger.exception(f"Error occured while fetching vb64_endorsement")
            raise ChequeDetailsException(f"Exception occured while fetching vb64_endorsement")
