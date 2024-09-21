import logging
from datetime import datetime

from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb

from app.models.payment import Payment
from app.services.user_services import get_user_details
from app.settings import SERVICE_CREDENTIALS
from app.utils.exceptions import *


logger = logging.getLogger(__name__)


class InsurerService:

    @staticmethod
    async def get_active_insurer_code():
        service_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + "/api/v1/insurer_list/"
        response = await AsyncHttpClient.get(url=service_url)
        status = response.dict()['status']
        if status == 1:
            response_data = response.dict()
            insurers = response_data['response_data']['data']
            return [insurer['code'] for insurer in insurers if insurer['is_active']]
        # return [i.get("code") for i in response]
        raise DataverseNotRespondingError(message="Insurer data not found from dataverse")


class PaymentServiceTrend:

    @classmethod
    async def get_payment_query(cls, start_date, end_date, request, query):
        date_from = start_date + " 00:00:00"
        date_to = end_date + " 23:59:59"
        try:
            user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
            query = query.where(Payment.created_at >= datetime.strptime(date_from, "%d-%m-%Y %H:%M:%S"),
                                Payment.created_at <= datetime.strptime(date_to, "%d-%m-%Y %H:%M:%S"))
            if user_details["dealer_code"]:
                query = query.where(Payment.dealer_code == user_details["dealer_code"])
            if user_details["insurer_code"]:
                query = query.where(Payment.insurer_code == user_details["insurer_code"])
            if request.headers.get('X-ROLE') == "insurer" and request.headers.get('X-INSURER-CODE'):
                insurer = request.headers.get('X-INSURER-CODE')
                query = query.where(Payment.insurer_code == insurer)
            if request.headers.get('X-ROLE') == "oem_dp" and request.headers.get('X-DP-CODE'):
                dp_name = request.headers.get('X-DP-CODE')
                query = query.where(Payment.dealer_person == dp_name)
            if request.headers.get('X-ROLE') == "super_admin":
                query = query.where(Payment.status_code == "success")
            payment = await sqldb.execute(query)
            return payment.all()
        except Exception as e:
            logger.exception(f"Error occurred while fetching payments")
            raise ChequeDetailsException(f"Exception occurred while fetching payments from \
                                                         {date_from} to {date_to}")
