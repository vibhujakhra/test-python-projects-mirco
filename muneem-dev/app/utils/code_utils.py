import io
import logging
from datetime import datetime
from random import randint
from typing import List
from typing import Optional

import aioboto3
import jinja2
import pandas
import pdfkit
from aiobotocore.session import get_session
from botocore.client import BaseClient
from fastapi import HTTPException
from num2words import num2words
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select, or_

from app.models.payment import Payment, ChequeDetails, PayInSlip, CHEQUE_TYPE_ENUM, Billing, PaymentMode, PaymentState
from app.schemas.pay_in_slip import GetPayInSlipQueryParam
from app.services.models import ChequeDetailServices, PaymentServices, BillingServices
from app.services.user_services import get_user_details
from app.settings import bucket_name, download_url, BASE_DIR, SERVICE_CREDENTIALS
from app.utils.exceptions import PDFGenerationException, ChequeNotFoundException

logger = logging.getLogger('utils')


def get_async_s3_client():
    async_s3_session = aioboto3.Session()
    return async_s3_session


async def create_policy(policy_data) -> dict:
    service_url = SERVICE_CREDENTIALS["policy"]["dns"] + "/api/v1/create_policy"
    policy_details = await AsyncHttpClient.post(url=service_url, body=policy_data)
    return policy_details

async def send_to_rb_coordinator(transaction_id: str, payment_status: str) -> dict:
    service_url = SERVICE_CREDENTIALS["rb_coordinator"][
                  "dns"] + f"/api/v1/motor/data_ingestion/?payment_status={payment_status}&transaction_id={transaction_id}"
    await AsyncHttpClient.post(url=service_url)
    return 


def generate_pay_in_slip_number(insurer_code: str) -> str:
    return insurer_code + "RB" + datetime.now().strftime("%d%m%Y%H%M%S%f")


async def get_search_data(request, query_params: GetPayInSlipQueryParam, insurer_code: Optional[str] = None) -> dict:
    final_payment_dict = {}
    user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
    payment_query = select(Payment)
    payment_mode_online = await PaymentMode.fetch_by_code(code="online_payment")
    is_payment_query = False
    pay_in_slip_query = select(PayInSlip)
    is_pay_in_slip_query = False
    if query_params.policy_number:
        payment_query = payment_query.where(Payment.policy_number == query_params.policy_number)
        is_payment_query = True
        is_pay_in_slip_query = True
    if query_params.dealer_code:
        payment_query = payment_query.where(Payment.dealer_code == query_params.dealer_code)
        is_payment_query = True
        is_pay_in_slip_query = True
    if user_details["dealer_code"]:
        payment_query = payment_query.where(Payment.dealer_code == user_details["dealer_code"])
        is_payment_query = True
    if user_details["insurer_code"]:
        payment_query = payment_query.where(Payment.insurer_code == user_details["insurer_code"])
        is_payment_query = True

    # If payment query_params is selected
    if is_payment_query:
        payment_query = payment_query.where(or_(Payment.billing_id != None, Payment.cheque_id != None))
        payment = await sqldb.execute(payment_query)
        payments = payment.scalars().all()

        cheque_query = select(ChequeDetails)
        is_cheque_query = False
        if query_params.cheque_number:
            cheque_query = cheque_query.where(ChequeDetails.cheque_number == query_params.cheque_number)
            is_cheque_query = True
        if query_params.cheque_date_from and query_params.cheque_date_to:
            cheque_date_from = query_params.cheque_date_from + " 00:00:00"
            cheque_date_to = query_params.cheque_date_to + " 23:59:59"
            cheque_query = cheque_query.filter(
                ChequeDetails.created_at >= datetime.strptime(cheque_date_from, "%d-%m-%Y %H:%M:%S"),
                ChequeDetails.created_at <= datetime.strptime(cheque_date_to, "%d-%m-%Y %H:%M:%S"))
            is_cheque_query = True

        # if cheque query param is also opted
        if is_cheque_query:
            cheque = await sqldb.execute(cheque_query)
            cheques = cheque.scalars().all()

            cheque_set = set([cheque.id for cheque in cheques])
            for cheque in cheques:
                if cheque.cheque_type != CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
                    billing_set = set([(await BillingServices.get_by_cheque_id(cheque_id=cheque.id)).id])
            payments = [payment for payment in payments if
                        (payment.cheque_id in cheque_set or payment.billing_id in billing_set)]
            is_pay_in_slip_query = True

        # payments are already filtered according to cheque
        # filtering payment with pay_in_slip query now
        if not insurer_code:
            if query_params.insurer_code and query_params.insurer_code.upper():
                pay_in_slip_query = pay_in_slip_query.where(PayInSlip.insurer_code == query_params.insurer_code.upper())
                is_pay_in_slip_query = True
        else:
            pay_in_slip_query = pay_in_slip_query.where(PayInSlip.insurer_code == insurer_code.upper())
            is_pay_in_slip_query = True

        if query_params.transaction_type_id:
            pay_in_slip_query = pay_in_slip_query.where(
                PayInSlip.transaction_type_id == query_params.transaction_type_id)
            is_pay_in_slip_query = True
        if query_params.pay_in_slip_number:
            pay_in_slip_query = pay_in_slip_query.where(PayInSlip.slip_number == query_params.pay_in_slip_number)
            is_pay_in_slip_query = True
        if query_params.pay_in_slip_date_from and query_params.pay_in_slip_date_to:
            pay_in_slip_date_from = query_params.pay_in_slip_date_from + " 00:00:00"
            pay_in_slip_date_to = query_params.pay_in_slip_date_to + " 23:59:59"
            pay_in_slip_query = pay_in_slip_query.filter(
                PayInSlip.created_at >= datetime.strptime(pay_in_slip_date_from, "%d-%m-%Y %H:%M:%S"),
                PayInSlip.created_at <= datetime.strptime(pay_in_slip_date_to, "%d-%m-%Y %H:%M:%S"))
            is_pay_in_slip_query = True

        pay_in_slip_set = set()
        if is_pay_in_slip_query:
            pay_in_slip = await sqldb.execute(pay_in_slip_query)
            pay_in_slips = pay_in_slip.scalars().all()

            pay_in_slip_set = set([pay_in_slip.id for pay_in_slip in pay_in_slips])


        for payment in payments:
            if not payment.payment_mode == payment_mode_online.id:
                if payment.cheque_id:
                    cheque = await ChequeDetails.fetch(key=payment.cheque_id)
                elif payment.billing_id:
                    billing = await Billing.fetch(key=payment.billing_id)
                    cheque = await ChequeDetails.fetch(key=billing.cheque_id)

                if is_pay_in_slip_query and cheque.pay_in_slip_id in pay_in_slip_set:
                    if final_payment_dict.get(cheque.pay_in_slip_id) is None:
                        final_payment_dict[cheque.pay_in_slip_id] = [{"payment": payment, "cheque": cheque,
                                                                      "pay_in_slip": await PayInSlip.fetch(
                                                                          key=cheque.pay_in_slip_id)}]
                    else:
                        final_payment_dict[cheque.pay_in_slip_id].append({"payment": payment, "cheque": cheque,
                                                                          "pay_in_slip": await PayInSlip.fetch(
                                                                              key=cheque.pay_in_slip_id)})
    else:
        cheque_query = select(ChequeDetails)
        is_cheque_query = False
        if user_details["dealer_code"]:
            cheque_query = cheque_query.where(ChequeDetails.dealer_code == user_details["dealer_code"])
            is_cheque_query = True
        if user_details["insurer_code"]:
            cheque_query = cheque_query.where(ChequeDetails.insurer_code == user_details["insurer_code"])
            is_cheque_query = True
        if query_params.cheque_number:
            cheque_query = cheque_query.where(ChequeDetails.cheque_number == query_params.cheque_number)
            is_cheque_query = True
        if query_params.cheque_date_from and query_params.cheque_date_to:
            cheque_date_from = query_params.cheque_date_from + " 00:00:00"
            cheque_date_to = query_params.cheque_date_to + " 23:59:59"
            cheque_query = cheque_query.where(
                ChequeDetails.created_at >= datetime.strptime(cheque_date_from, "%d-%m-%Y %H:%M:%S"),
                ChequeDetails.created_at <= datetime.strptime(cheque_date_to, "%d-%m-%Y %H:%M:%S"))
            is_cheque_query = True

        if is_cheque_query:
            cheque_query = cheque_query.where(ChequeDetails.pay_in_slip_id) is not None
            cheque = await sqldb.execute(cheque_query)
            cheques = cheque.scalars().all()

            pay_in_slip_query = select(PayInSlip)
            is_pay_in_slip_query = False
            if not insurer_code:
                if query_params.insurer_code and query_params.insurer_code.upper():
                    pay_in_slip_query = pay_in_slip_query.where(
                        PayInSlip.insurer_code == query_params.insurer_code.upper())
                    is_pay_in_slip_query = True
            else:
                pay_in_slip_query = pay_in_slip_query.where(PayInSlip.insurer_code == insurer_code.upper())
                is_pay_in_slip_query = True

            if query_params.transaction_type_id:
                pay_in_slip_query = pay_in_slip_query.where(
                    PayInSlip.transaction_type_id == query_params.transaction_type_id)
                is_pay_in_slip_query = True
            if query_params.pay_in_slip_number:
                pay_in_slip_query = pay_in_slip_query.where(PayInSlip.slip_number == query_params.pay_in_slip_number)
                is_pay_in_slip_query = True
            if query_params.pay_in_slip_date_from and query_params.pay_in_slip_date_to:
                pay_in_slip_date_from = query_params.pay_in_slip_date_from + " 00:00:00"
                pay_in_slip_date_to = query_params.pay_in_slip_date_to + " 23:59:59"
                pay_in_slip_query = pay_in_slip_query.filter(
                    PayInSlip.created_at >= datetime.strptime(pay_in_slip_date_from, "%d-%m-%Y %H:%M:%S"),
                    PayInSlip.created_at <= datetime.strptime(pay_in_slip_date_to, "%d-%m-%Y %H:%M:%S"))
                is_pay_in_slip_query = True

            # if pay_in_slip query param is opted
            pay_in_slip_set = set()
            if is_pay_in_slip_query:
                pay_in_slip = await sqldb.execute(pay_in_slip_query)
                pay_in_slips = pay_in_slip.scalars().all()

                pay_in_slip_set = set([pay_in_slip.id for pay_in_slip in pay_in_slips])
                cheques = [cheque for cheque in cheques if cheque.pay_in_slip_id in pay_in_slip_set]

            # at this stage cheque are filtered according to cheque query and pay in slip query
            for cheque in cheques:
                if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
                    payments = await PaymentServices.get_by_cheque_id(cheque_id=cheque.id)
                else:
                    billing = await BillingServices.get_by_cheque_id(cheque_id=cheque.id)
                    payments = await PaymentServices.get_by_billing_id(billing_id=billing.id)

                pay_in_slip = await PayInSlip.fetch(key=cheque.pay_in_slip_id)
                for payment in payments:
                    if final_payment_dict.get(pay_in_slip.id) is None:
                        final_payment_dict[pay_in_slip.id] = [{"payment": payment, "cheque": cheque,
                                                               "pay_in_slip": pay_in_slip}]
                    else:
                        final_payment_dict[pay_in_slip.id].append({"payment": payment, "cheque": cheque,
                                                                   "pay_in_slip": pay_in_slip})
        else:
            # if only pay_in_slip query param is selected
            pay_in_slip_query = select(PayInSlip)
            is_pay_in_slip_query = False
            if not insurer_code:
                if query_params.insurer_code and query_params.insurer_code.upper():
                    pay_in_slip_query = pay_in_slip_query.where(
                        PayInSlip.insurer_code == query_params.insurer_code.upper())
                    is_pay_in_slip_query = True
            else:
                pay_in_slip_query = pay_in_slip_query.where(PayInSlip.insurer_code == insurer_code.upper())
                is_pay_in_slip_query = True

            if query_params.transaction_type_id:
                pay_in_slip_query = pay_in_slip_query.where(
                    PayInSlip.transaction_type_id == query_params.transaction_type_id)
                is_pay_in_slip_query = True
            if query_params.pay_in_slip_number:
                pay_in_slip_query = pay_in_slip_query.where(PayInSlip.slip_number == query_params.pay_in_slip_number)
                is_pay_in_slip_query = True
            if query_params.pay_in_slip_date_from and query_params.pay_in_slip_date_to:
                pay_in_slip_date_from = query_params.pay_in_slip_date_from + " 00:00:00"
                pay_in_slip_date_to = query_params.pay_in_slip_date_to + " 23:59:59"
                pay_in_slip_query = pay_in_slip_query.filter(
                    PayInSlip.created_at >= datetime.strptime(pay_in_slip_date_from, "%d-%m-%Y %H:%M:%S"),
                    PayInSlip.created_at <= datetime.strptime(pay_in_slip_date_to, "%d-%m-%Y %H:%M:%S"))
                is_pay_in_slip_query = True

            if is_pay_in_slip_query:
                pay_in_slip = await sqldb.execute(pay_in_slip_query)
                pay_in_slips = pay_in_slip.scalars().all()

            for pay_in_slip in pay_in_slips:
                cheques = await ChequeDetailServices.get_by_pay_in_slip_id(pay_in_slip_id=pay_in_slip.id)
                for cheque in cheques:
                    if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
                        payments = await PaymentServices.get_by_cheque_id(cheque_id=cheque.id)
                    else:
                        billing = await BillingServices.get_by_cheque_id(cheque_id=cheque.id)
                        payments = await PaymentServices.get_by_billing_id(billing_id=billing.id)

                    for payment in payments:
                        if final_payment_dict.get(pay_in_slip.id) is None:
                            final_payment_dict[pay_in_slip.id] = [{"payment": payment, "cheque": cheque,
                                                                   "pay_in_slip": pay_in_slip}]
                        else:
                            final_payment_dict[pay_in_slip.id].append({"payment": payment, "cheque": cheque,
                                                                       "pay_in_slip": pay_in_slip})

    return final_payment_dict


async def get_query_result(request, data: dict):
    result, bank_cache = [], {}
    for pay_in_slip_id, pay_in_slip_list in data.items():
        if pay_in_slip_list:
            pay_in_slip = pay_in_slip_list[0].get('pay_in_slip')
            payment = pay_in_slip_list[0].get('payment')

            # fetching insurer data for view pdf preview
            user_details = await ChequeDetailServices.get_detail_transactions(transaction_id=payment.transaction_id)
            response = await ChequeDetailServices.get_policy_summary_data(
                _ids=[("insurer_code", pay_in_slip.insurer_code), ("user_details", user_details['user_id'])])
            insurer_data = response['insurer']
            if insurer_data.get('cms_bank_name_id'):
                cms_bank_name_obj = await ChequeDetailServices.get_policy_summary_data(
                    _ids=[("bank_id", insurer_data.get('cms_bank_name_id'))])
                cms_bank_name = cms_bank_name_obj['bank']['name']
            else:
                cms_bank_name = "NA"
            dealer_code = payment.dealer_code
            dealer_obj = await ChequeDetailServices.get_policy_summary_data(
                _ids=[("dealer_code", dealer_code)])
            dealer_city_obj = await ChequeDetailServices.get_policy_summary_data(
                _ids=[("city_id", dealer_obj['dealer']['city_id'])])

            payment_mode = await PaymentMode.fetch(key=payment.payment_mode)
            row_data = {
                "pay_in_slip_id": pay_in_slip_id,
                "pay_in_slip_number": pay_in_slip.slip_number,
                "pay_in_slip_date": pay_in_slip.created_at.strftime("%d-%m-%Y"),
                "pay_in_slip_amount": pay_in_slip.pay_in_slip_amount,
                "pay_in_slip_amount_words": num2words(pay_in_slip.pay_in_slip_amount, lang='en_IN'),
                "insurer_name": payment.insurer_name,
                "dealer_name": dealer_obj['dealer']['dealer_name'],
                "insurer_logo": insurer_data.get("insurer_logo"),
                "servicing_office_of_insurer": insurer_data.get('servicing_office_address'),
                "irda_registration_number": insurer_data.get('irda_registration_no'),
                "dealer_code": dealer_code,
                "payment_mode": payment_mode.name,
                "dealer_city_district": dealer_city_obj['city']['name'],
                "house_bank_name": cms_bank_name,
                "cheque_data": []
            }

            for pay_in_slip_data in pay_in_slip_list:
                payment = pay_in_slip_data['payment']
                cheque = pay_in_slip_data['cheque']
                if bank_cache.get(cheque.bank_id) is None:
                    dataverse_data = await ChequeDetailServices.get_policy_summary_data(
                        _ids=[("bank_id", cheque.bank_id)])
                    bank_cache[cheque.bank_id] = dataverse_data['bank'].get('name')

                row_data['cheque_data'].append({
                    "unique_reference_number": cheque.unique_reference_number,
                    "cheque_number": cheque.cheque_number,
                    "cheque_date": cheque.cheque_date.strftime("%d-%m-%Y"),
                    "insured_name": payment.insured_name,
                    "bank_name": bank_cache[cheque.bank_id],
                    "bank_branch_and_city": cheque.bank_branch_and_city,
                    "bank_city_id": cheque.city_id,
                    "cheque_amount": payment.payment_amount,
                    "paid_by": "Dealer" if cheque.cheque_type == CHEQUE_TYPE_ENUM.DEALER_CHEQUE else "Customer",
                    "policy_number": payment.policy_number
                })
        result.append(row_data)
    return result


async def get_detail_pay_in_slip_data(request, cheques: List[ChequeDetails], pay_in_slip: PayInSlip):
    detail_data, bank_cache = {}, {}
    # cheques list will always have cheque
    try:
        cheque = cheques[0]
    except IndexError:
        raise ChequeNotFoundException(message="No cheque found for pay in slip generation")
    response = await ChequeDetailServices.get_policy_summary_data(
        _ids=[("insurer_code", cheque.insurer_code)])
    insurer_data = response['insurer']
    detail_data.update({
        "insurer_name": insurer_data.get("name"),
        "insurer_logo": insurer_data.get("insurer_logo"),
        "irda_registration_number": insurer_data.get('irda_registration_no')
    })
    user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
    if insurer_data.get('cms_bank_name_id'):
        cms_bank_name_obj = await ChequeDetailServices.get_policy_summary_data(
            _ids=[("bank_id", insurer_data.get('cms_bank_name_id'))])
        cms_bank_name = cms_bank_name_obj['bank']['name']
    else:
        cms_bank_name = "NA"
    user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
    detail_data.update({
        "pay_in_slip_id": pay_in_slip.id,
        "pay_in_slip_number": pay_in_slip.slip_number,
        "pay_in_slip_date": pay_in_slip.created_at.strftime("%d-%m-%Y"),
        "pay_in_slip_amount": pay_in_slip.pay_in_slip_amount,
        "pay_in_slip_amount_words": num2words(pay_in_slip.pay_in_slip_amount, lang='en_IN'),
        "house_bank_name": cms_bank_name,
        "dealer_city_district": user_details["city"],
        "cheque_data": []
    })

    for cheque in cheques:
        if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
            payments = await PaymentServices.get_by_cheque_id(cheque_id=cheque.id)
        elif cheque.cheque_type == CHEQUE_TYPE_ENUM.DEALER_CHEQUE:
            billing = await BillingServices.get_by_cheque_id(cheque_id=cheque.id)
            payments = await PaymentServices.get_by_billing_id(billing_id=billing.id)

        if bank_cache.get(cheque.bank_id) is None:
            dataverse_data = await ChequeDetailServices.get_policy_summary_data(_ids=[("bank_id", cheque.bank_id)])
            bank_cache[cheque.bank_id] = dataverse_data['bank'].get('name')

        for payment in payments:
            row_data = {
                "unique_reference_number": cheque.unique_reference_number,
                "cheque_number": cheque.cheque_number,
                "cheque_date": cheque.cheque_date.strftime("%d-%m-%Y"),
                "insured_name": payment.insured_name,
                "bank_name": bank_cache[cheque.bank_id],
                "bank_branch_and_city": cheque.bank_branch_and_city,
                "cheque_amount": payment.payment_amount,
                "paid_by": "Dealer" if cheque.cheque_type == CHEQUE_TYPE_ENUM.DEALER_CHEQUE else "Customer",
                "policy_number": payment.policy_number
            }
            detail_data['cheque_data'].append(row_data)
            dealer_code = payment.dealer_code
            dealer_code_details = await ChequeDetailServices.get_user_details_by_code(code=dealer_code)
            dealer_obj = await ChequeDetailServices.get_policy_summary_data(
                _ids=[("dealer_code", dealer_code), ("insurer_code", cheque.insurer_code),
                      ("user_details", dealer_code_details["user_id"])])
            dealer_name = dealer_obj['dealer']['dealer_name']
            payment_mode = await PaymentMode.fetch(key=payment.payment_mode)

            detail_data.update({
                "dealer_name": dealer_name,
                "dealer_code": dealer_code,
                "payment_mode": payment_mode.name,
                "servicing_office_of_insurer": dealer_obj['ic_location_detail']['servicing_office_address'],
            })
    return detail_data


async def upload_csv_to_s3(key: str, data, async_s3_client: BaseClient) -> str:  # TODO: need to check with @naveen
    logger.info(f"uploading csv on s3 bucket for key {key}")
    df = pandas.DataFrame(data)
    io_bytes_obj = io.BytesIO()
    df.to_csv(io_bytes_obj, header=data[0].keys(), index=False)
    async with async_s3_client.client("s3") as s3:
        await s3.put_object(Body=io_bytes_obj.getvalue(), Bucket=bucket_name, Key=key)
        return f"{download_url}{key}"


async def get_transaction_types() -> list:
    service_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + "/api/v1/transaction_type/"
    return await AsyncHttpClient.get(url=service_url)


async def prepare_pay_in_slip_pdf(context_data: dict, slip_number: str):
    template_path = BASE_DIR + "/template/"
    templateLoader = jinja2.FileSystemLoader(searchpath=template_path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template_file = "pay_in_slip_pdf.html"
    template = templateEnv.get_template(template_file)
    filled_template = template.render(**context_data)
    pdf_name = slip_number + ".pdf"

    try:
        pay_in_slip_pdf = pdfkit.from_string(filled_template, False)
        pay_in_slip_pdf = await save_to_s3_bucket(raw_pdf_content=pay_in_slip_pdf, product_slug='motor',
                                                  pay_in_slip_number=slip_number, file_name=pdf_name)
    except Exception:
        logger.exception(f"Error encountered while creating pay in slip pdf for slip number: {slip_number}")
        raise PDFGenerationException(name="utils.code_utils.prepare_pay_in_slip",
                                     message=f"Error encountered while generating pdf for slip \
                                               number: {slip_number}, please try after some time")

    return pay_in_slip_pdf


async def save_to_s3_bucket(raw_pdf_content: str, product_slug: str,
                            pay_in_slip_number: str, file_name: str):
    logger.info(f"uploading pay in slip pdf on s3 bucket for slip number: {pay_in_slip_number}")
    bucket = bucket_name
    key = f"documents/{product_slug}/{pay_in_slip_number}/{file_name}"

    session = get_session()  # TODO: need to check with @naveen
    async with session.create_client('s3') as client:
        logger.info(f"bucket_name: {bucket}, key: {key}, session: {session} and s3 client: {client}")
        response = await client.put_object(Bucket=bucket, Key=key, Body=raw_pdf_content)
        logger.info(f"response of s3 upload is {response}")
        if response.get('ResponseMetadata'):
            meta_data = response.get('ResponseMetadata')
            status_code = meta_data.get('HTTPStatusCode')
            if status_code and status_code == 200:
                policy_download_url = f"{download_url}{key}"
                logger.info(f"download url for pdf is {policy_download_url}")
                return policy_download_url


async def check_insurer_headers(request):
    insurer_code = request.headers.get("x-insurer-code")
    if not insurer_code:
        raise HTTPException(
            status_code=500,
            detail="Insurer detail is missing",
        )
    return insurer_code


async def generate_otp(opt_length=6):
    range_start = 10 ** (opt_length - 1)
    range_end = (10 ** opt_length) - 1
    return str(randint(range_start, range_end))


# async def update_payin_slip_and_vb64(policy_number, pay_in_slip):
#     service_url = SERVICE_CREDENTIALS["policy"]["dns"] + f"/api/v1/update_payin_vb644/?policy_number={policy_number}" \
#                   + f"&deposit_slip={pay_in_slip}"
#     await AsyncHttpClient.post(url=service_url)


async def update_deposit_slip(policy_number):
    service_url = SERVICE_CREDENTIALS["policy"]["dns"] + f"/api/v1/update_payinstatus_vb644/?policy_number={policy_number}"
    await AsyncHttpClient.post(url=service_url)


async def check_insurer_payment_integrated(insurer_code: str) -> bool:
    policy_summary_url = SERVICE_CREDENTIALS['dataverse'][
                             'dns'] + f"/api/v1/policy_summary/?insurer_code={insurer_code.upper()}"
    policy_summary_response = await AsyncHttpClient.get(url=policy_summary_url)
    if policy_summary_response['insurer']['is_payment_integrated']:
        return True
    return False


def convert_str_to_datetime(date_str: str, date_format: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    return datetime.strptime(date_str, date_format)


def convert_datetime_to_str(date_time: datetime, date_format: str = '%m/%d/%Y') -> str:
    return date_time.strftime(date_format)
