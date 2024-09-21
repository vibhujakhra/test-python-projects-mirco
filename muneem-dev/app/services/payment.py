import logging
from datetime import datetime
from typing import List

from motor_integrations import get_adaptor
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select

from app import settings
from app.models.payment import PaymentStatus, CHEQUE_TYPE_ENUM, Payment, ChequeDetails, Billing, PaymentMode
from app.schemas.payment import UpdatePaymentRequest
from app.services.models import ChequeDetailServices
from app.services.user_services import get_user_details
from app.settings import SERVICE_CREDENTIALS
from app.utils.code_utils import generate_pay_in_slip_number, convert_datetime_to_str

logger = logging.getLogger(name="api")


async def create_or_update_cheque(data: UpdatePaymentRequest, payment: Payment):
    cheque_date = datetime.strptime(data.cheque_date, '%d-%m-%Y')
    payment_status = await PaymentStatus.fetch_by_code(code='pending')
    create_data = {
        "cheque_number": data.cheque_number,
        "cheque_date": cheque_date,
        "transaction_type_id": payment.transaction_type_id,
        "cheque_amount": data.payment_amount,
        "insurer_code": data.insurer_code,
        "cheque_type": CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE.name,
        "bank_id": data.bank_id,
        "bank_branch_and_city": data.bank_branch_and_city,
        "account_number": data.account_number,
        "unique_reference_number": generate_pay_in_slip_number(insurer_code=data.insurer_code),
        "payment_status": payment_status.id,
        "dealer_code": data.dealer_code
    }
    if payment.cheque_id is not None:
        logger.info(f"updating cheque with cheque id {payment.cheque_id} and data {create_data}")
        await ChequeDetails.update(key=payment.cheque_id, **create_data)
        cheque = await ChequeDetails.fetch(key=payment.cheque_id)
    else:
        logger.info(f"creating cheque with data {create_data}")
        cheque = await ChequeDetails.create(**create_data)

    return cheque


async def update_payment(data: UpdatePaymentRequest, cheque: ChequeDetails):
    update_data = {
        "cheque_id": cheque.id,
        "payment_mode": data.payment_mode,
        "model": data.model,
        "variant": data.variant,
        "insurer_name": data.insurer_name,
        "insured_name": data.insured_name,
        "payment_amount": data.payment_amount,
        "vehicle_cover_id": data.vehicle_cover_id,
        "dealer_code": data.dealer_code,
        "policy_type_id": data.policy_type_id,
        "policy_start_date": datetime.strptime(
            data.policy_start_date, "%d-%m-%Y").date() if data.policy_start_date else None,
        "policy_end_date": datetime.strptime(
            data.policy_end_date, "%d-%m-%Y").date() if data.policy_end_date else None,
        "policy_issuance_date": datetime.strptime(
            data.policy_start_date, "%d-%m-%Y").date() if data.policy_start_date else None
        # TODO: Policy issuance date logic needs to rechecked
    }

    await Payment.update(key=data.payment_id, **update_data)


async def get_cheque_data(request, transaction_type_id: int, insurer_code: str, cheque_id: int = None):
    is_endorsement = True if transaction_type_id == 2 else False
    logger.info(f"fetching cheque details for transaction_type_id: {transaction_type_id} \
                      and insurance_code: {insurer_code}")
    params = {
        "request": request,
        "transaction_type": transaction_type_id,
        "insurer_code": insurer_code.upper(),
    }
    if cheque_id:
        params.update({"cheque_id": cheque_id})
    cheque_results = await ChequeDetailServices.fetch_cheque_details(**params)
    customer_cheque_data, dealer_cheque_data = await ChequeDetailServices.segregate_cheque_ids(
        query_list=cheque_results)
    await ChequeDetailServices.get_billing(cheque_data=dealer_cheque_data)
    complete_data = customer_cheque_data + dealer_cheque_data
    data = {"data": await ChequeDetailServices.get_payment(complete_data=complete_data),
            "is_endorsement": is_endorsement}
    return data


async def get_billing_payment_details(request, transaction_type_id: int, insurer_code: str, payment_mode: int,
                                      payment_mode_id: int = None) -> list:
    user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
    query = select(Payment).where(Payment.transaction_type_id == transaction_type_id,
                                  Payment.policy_number != None, Payment.billing_id == None,
                                  Payment.payment_mode == payment_mode, Payment.insurer_code == insurer_code,
                                  Payment.dealer_code == user_details['dealer_code'])
    if payment_mode_id:
        query = select(Payment).where(Payment.id == payment_mode_id,
                                      Payment.transaction_type_id == transaction_type_id,
                                      Payment.policy_number != None, Payment.billing_id == None,
                                      Payment.payment_mode == payment_mode, Payment.insurer_code == insurer_code,
                                      Payment.dealer_code == user_details['dealer_code'])
    payment_mode_obj = await PaymentMode.fetch(key=payment_mode)
    if payment_mode_obj.code == "online_payment":
        query = query.where(Payment.policy_start_date >= datetime.now().date())
    results = await sqldb.execute(query)
    payments = results.scalars().all()
    billing_payments = []
    for payment in payments:
        payment_data = payment.__dict__
        payment_data.update({
            'payment_mode': payment_mode_obj.name,
            'vehicle_name': "{} {}".format(payment_data.get('model'), payment_data.get('variant')),
            'payment_id': payment.id
        })
        billing_payments.append(payment_data)

    return billing_payments


async def get_proposal(transaction_id: str):
    get_transaction_url = SERVICE_CREDENTIALS['cleverbridge']['dns'] + f"/api/v1/get-transaction/{transaction_id}"
    response = await AsyncHttpClient.get(url=get_transaction_url)
    proposal_id = response['proposal_detail']
    get_proposal_url = SERVICE_CREDENTIALS['proposal']['dns'] + f"/api/v1/get_proposal/{proposal_id}"
    proposal = await AsyncHttpClient.get(url=get_proposal_url)

    return proposal


async def send_payment_data_to_insurer(cheque: ChequeDetails, payments: List[Payment], pay_in_slip_number: str):
    payment_request_body = {}
    policy_summary_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + f"/api/v1/policy_summary/?bank_id={cheque.bank_id}"
    policy_summary_response = await AsyncHttpClient.get(url=policy_summary_url)
    bank_code = policy_summary_response['bank']['code']

    cheque_type = 'D'
    if cheque.cheque_type == CHEQUE_TYPE_ENUM.CUSTOMER_CHEQUE:
        cheque_type = 'I'

    configuration_data = settings.INSURER_SETTINGS.get(cheque.insurer_code.lower())
    adaptor = get_adaptor(name=f"fw_{cheque.insurer_code.lower()}", configuration_data=configuration_data)
    for payment in payments:
        proposal = await get_proposal(transaction_id=payment.transaction_id)
        payment_request_body.update({
            "InsPolicyNo": payment.policy_number,
            "InsProposalNo": proposal.get('proposal_number'),
            "ReconciledChequeNo": cheque.cheque_number,
            "ReconciledChequeDate": convert_datetime_to_str(cheque.cheque_date),
            "ReconciledChequeBank": bank_code,
            "ReconciledChequeBranch": cheque.bank_branch_and_city,
            "ReconciledChequeAmount": cheque.cheque_amount,
            "ReconciledChequeIssuedBy": cheque_type,
            "PayInSlipNo": pay_in_slip_number,
            "PayInSlipDate": convert_datetime_to_str(datetime.now()),
            "UniqueReferenceNo": cheque.unique_reference_number,
            "ChequeAmount": cheque.cheque_amount,
            "ProposerPaymentMode": cheque_type,
            "PaymentAmount": payment.payment_amount
        })

        await adaptor.create_payment(payment_data=payment_request_body)


async def send_online_payment_details_to_insurer(payment_id: int, billing_id: int):
    payment = await Payment.fetch(key=payment_id)
    billing = await Billing.fetch(key=billing_id)
    configuration_data = settings.INSURER_SETTINGS.get(payment.insurer_code.lower())
    adaptor = get_adaptor(name=f"fw_{payment.insurer_code.lower()}", configuration_data=configuration_data)
    proposal = await get_proposal(transaction_id=payment.transaction_id)
    payment_request_body = {
        "InsPolicyNo": payment.policy_number,
        "InsProposalNo": proposal.get('proposal_number'),
        "ReconciledChequeNo": payment.bank_ref_no,
        "ReconciledChequeDate": convert_datetime_to_str(payment.transaction_date),
        "ReconciledChequeBank": "",
        "ReconciledChequeBranch": "",
        "ReconciledChequeAmount": payment.payment_amount,
        "ReconciledChequeIssuedBy": "D",  # for Dealer Online
        "PayInSlipNo": "",
        "PayInSlipDate": "",
        "UniqueReferenceNo": generate_pay_in_slip_number(insurer_code=payment.insurer_code.upper()),
        "ChequeAmount": billing.amount,
        "ProposerPaymentMode": "G",  # For Payment Gateway
        "PaymentAmount": billing.amount
    }
    await adaptor.create_payment(payment_data=payment_request_body)


async def get_billing_ids_by_cheque_number_for_dealer(cheque_number: str) -> List[int]:
    cheque_query = select(ChequeDetails.id).filter(ChequeDetails.cheque_number == cheque_number)
    results = await sqldb.execute(cheque_query)
    cheque_ids = results.scalars().all()
    billing_query = select(Billing.id).filter(Billing.cheque_id.in_(cheque_ids))
    results = await sqldb.execute(billing_query)
    return results.scalars().all()


async def get_cheque_ids_by_cheque_number_for_customer(cheque_number: str) -> List[int]:
    cheque_query = select(ChequeDetails.id).filter(ChequeDetails.cheque_number == cheque_number)
    results = await sqldb.execute(cheque_query)
    return results.scalars().all()


async def generate_update_payment_request(payment_id: int) -> dict:
    """
    The generate_update_payment_request function is used to generate the request body for updating payment details.
    Args:
        payment_id (int): The id of the payment object that needs to be updated.
    :param payment_id: int: Fetch the payment details from the database
    :return: dict:
    """
    payment = await Payment.fetch(key=payment_id)
    proposal_url = SERVICE_CREDENTIALS["proposal"][
                       "dns"] + f"/api/v1/get_proposal_by_transaction/{payment.transaction_id}"
    proposal = await AsyncHttpClient.get(url=proposal_url)
    tp_coverage = proposal['coverage_details'].get('tp_coverage')
    od_coverage = proposal['coverage_details'].get('od_coverage')
    tp_tenure = tp_coverage['tp_tenure'] if tp_coverage else 0
    od_tenure = od_coverage['od_tenure'] if od_coverage else 0
    od_end_date = datetime.strptime(od_coverage['od_end_date'],
                                    "%d-%m-%Y").date() if od_coverage else datetime.now().date(),
    tp_end_date = datetime.strptime(tp_coverage['tp_end_date'],
                                    "%d-%m-%Y").date() if tp_coverage else datetime.now().date(),
    policy_end_date = max(od_end_date, tp_end_date)
    str_policy_end_date = policy_end_date.strftime("%d-%m-%Y")
    online_payment = await PaymentMode.fetch_by_code(code='online_payment')
    vehicle_data = proposal['vehicle_details']
    customer = proposal['customer']
    dataverse_data = await ChequeDetailServices.get_policy_summary_data(
        _ids=[("vehicle_model_id", vehicle_data['model_id']), ("variant_id", vehicle_data['variant_id']),
              ("insurer_code", payment.insurer_code), ("dealer_code", payment.dealer_code)])
    payment_data = {
        "vehicle_cover_id": proposal['vehicle_cover_id'],
        "policy_period": max(tp_tenure, od_tenure),
        "payment_amount": payment.payment_amount,
        "payment_mode": online_payment.id,
        "payment_id": payment.id,
        "transaction_id": payment.transaction_id,
        "insurer_code": payment.insurer_code,
        "policy_type_id": proposal['policy_type_id'],
        "engine_number": vehicle_data['engine_number'],
        "chassis_number": vehicle_data['chassis_number'],
        "proposal_number": proposal['proposal_number'],
        "model": dataverse_data['vehicle_model']['name'],
        "variant": dataverse_data['variant']['name'],
        "registration_number": vehicle_data['registration_number'],
        "insured_name": customer['first_name'] + " " + customer['middle_name'] if customer[
            'middle_name'] else "" + " " + customer['last_name'],
        "proposal_type": proposal['proposer_type_id'],
        "dealer_code": proposal['dealer_code'],
        "dealer_name": dataverse_data['dealer']['dealer_name'],
        "insurer_name": dataverse_data['insurer']['name'],
        "create_endorsement": False,
        "city_id": proposal['city_id'],
        "policy_start_date": proposal['policy_start_date'],
        "policy_end_date": str_policy_end_date,
        "policy_number": proposal['policy_number'],
        "create_policy": True
    }
    return payment_data


async def get_payment_list(request, payment_details: list, issue_type: str) -> List[dict]:
    """
    The get_payment_list function takes in a list of payment details and returns a list of dictionaries containing
    the insurer code, the payment mode id, the name of the payment mode, transaction type id, transaction type name,
    and total amount paid for each unique combination. It also contains a count for the number of transactions.

    :param payment_details: list: Get the list of payment details
    :return: A list of dictionaries
    """
    service_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + "/api/v1/transaction_type/"
    transaction_type_dict = {
        transaction_type['id']: transaction_type['name']
        for transaction_type in await AsyncHttpClient.get(url=service_url)
    }

    payment_dict = {}
    payment_details_list = {}

    for payment_detail in payment_details:
        payment_mode_data = await PaymentMode.fetch_by_code(code=payment_detail['payment_mode'])
        key_to_check = (payment_detail['insurer_code'], payment_detail['payment_mode'], payment_detail['transaction_type_id'])
        payment_amount = payment_detail['payment_amount']
        transaction_type_name = transaction_type_dict.get(payment_detail['transaction_type_id'])

        if key_to_check not in payment_dict:
            payment_dict[key_to_check] = {
                "insurer_code": payment_detail['insurer_code'],
                "payment_mode_id": payment_mode_data.id,
                "payment_mode": payment_mode_data.code,
                "transaction_type_id": payment_detail['transaction_type_id'],
                "transaction_type_name": transaction_type_name,
                "payment_amount": 0,
                "transaction_count": 0,
            }

        payment_dict[key_to_check]['payment_amount'] += payment_amount
        payment_dict[key_to_check]['transaction_count'] += 1
        temp_payment_list = payment_details_list.get(key_to_check, [])
        cheque_data_response = await (
            get_billing_payment_details(request=request, transaction_type_id=payment_detail['transaction_type_id'],
                                        insurer_code=payment_detail['insurer_code'], payment_mode=payment_mode_data.id,
                                        payment_mode_id=payment_detail["id"])
            if issue_type == "payment_not_tagged"
            else get_cheque_data(request=request, transaction_type_id=payment_detail['transaction_type_id'],
                                insurer_code=payment_detail['insurer_code'], cheque_id=payment_detail['cheque_id'])
        )

        payment_details_list[key_to_check] = temp_payment_list + cheque_data_response.get("data", []) if \
            issue_type is not "payment_not_tagged" else temp_payment_list + cheque_data_response

    return_list = []
    for comb, payment_data in payment_dict.items():
        payment_data["payment_detail_list"] = payment_details_list[comb]
        return_list.append(payment_data)
    return return_list
