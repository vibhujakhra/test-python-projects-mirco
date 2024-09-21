import binascii
import datetime
import logging
from datetime import timedelta
from typing import Union

from cryptography.fernet import Fernet
from fastapi import APIRouter, BackgroundTasks, Depends, Request, responses
from fastapi.responses import JSONResponse
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select, func
from starlette import status
from starlette.responses import RedirectResponse

from app.models.payment import *
from app.schemas.payment import *
from app.schemas.payment import AllPaymentDetailsResponse
from app.sdk.kafka_producer import AsyncKafkaProducer
from app.services.models import ChequeDetailServices
from app.services.payment import create_or_update_cheque, update_payment, send_online_payment_details_to_insurer, \
    get_billing_ids_by_cheque_number_for_dealer, get_cheque_ids_by_cheque_number_for_customer, \
    generate_update_payment_request
from app.services.user_services import get_user_details
from app.settings import DOMAIN_ADDRESS_SERVER, SERVICE_CREDENTIALS, OTP_EXPIRY_SEC, GATEWAY_ENCRYPTION_KEY
from app.utils.code_utils import convert_str_to_datetime, send_to_rb_coordinator
from app.utils.code_utils import create_policy, check_insurer_payment_integrated
from app.utils.code_utils import generate_otp
from app.utils.code_utils import get_transaction_types
from app.utils.exceptions import *

router = APIRouter()
logger = logging.getLogger("api")
fernet = Fernet(bytes(GATEWAY_ENCRYPTION_KEY.encode()))


@router.get("/consent_type/")
async def get_consent_type() -> List[ConsentTypeResponse]:
    logger.info("Getting list of all consent types in the database")
    consent_types = await ConsentType.fetch_all(is_active=True)
    return [ConsentTypeResponse(**consent_type.__dict__) for consent_type in consent_types]


@router.get("/consent_state/")
async def get_consent_state() -> List[ConsentStateResponse]:
    logger.info("Getting list of all consent states in the database")
    consent_states = await ConsentState.fetch_all(is_active=True)
    return [ConsentStateResponse(**consent_state.__dict__) for consent_state in consent_states]


@router.get("/payment_state/")
async def get_payment_state() -> List[PaymentStateResponse]:
    payment_states = await PaymentState.fetch_all(is_active=True)
    return [PaymentStateResponse(**payment_state.__dict__) for payment_state in payment_states]


@router.get("/payment_status/")
async def get_payment_state() -> List[PaymentStatusResponse]:
    payment_status = await PaymentStatus.fetch_all(is_active=True)
    return [PaymentStatusResponse(**status.__dict__) for status in payment_status]


@router.get("/payment_mode/")
async def get_payment_mode() -> List[PaymentModeResponse]:
    payment_modes = await PaymentMode.fetch_all(is_active=True)
    return [PaymentModeResponse(**payment_mode.__dict__) for payment_mode in payment_modes]


@router.get("/consent/{transaction_id}")
async def get_consent_by_payment(transaction_id: str) -> ConsentResponse:
    logger.info( f"Getting list of all consent by transaction_id: {transaction_id}")
    consent_obj = select(Consent).where(Consent.transaction_id == transaction_id)
    consent_obj = await sqldb.execute(consent_obj)
    consent_obj = consent_obj.scalars().all()
    consent = consent_obj[0]
    consent_state = await ConsentState.fetch(key=consent.consent_state)
    consent_type = await ConsentType.fetch(key=consent.consent_type)
    return ConsentResponse(
        consent_id=consent.id,
        consent_type=consent_type.name,
        consent_state=consent_state.name
    )


@router.get("/get_payment/{payment_id}")
async def get_payment_by_id(payment_id: int) -> PaymentResponse:
    logger.info( f"Getting list of all consent by payment_id: {payment_id}")
    payment_details = await Payment.fetch(key=payment_id)
    payment_mode_details = None
    if payment_details.payment_mode:
        payment_mode_details = await PaymentMode.fetch(key=payment_details.payment_mode)
        payment_mode_details = payment_mode_details.name

    response_dict = {
        "payment_id": payment_details.id,
        "transaction_id": payment_details.transaction_id,
        "insurer_code": payment_details.insurer_code,
        "payment_state_id": payment_details.payment_state,
        "payment_mode_id": payment_details.payment_mode,
        "payment_mode": payment_mode_details,
        "consent": payment_details.consent_id,
        "dealer_person": payment_details.dealer_person,
        "sales_manager": payment_details.sales_manager,
        "payment_amount": payment_details.payment_amount,
        "payment_state": (await PaymentState.fetch(
            key=payment_details.payment_state)).name if payment_details.payment_state else None,
        "payment_status": (
            await PaymentStatus.fetch(
                key=payment_details.payment_status)).name if payment_details.payment_status else None,
        "endorsement_number": payment_details.endorsement_number
    }
    cheque_id = payment_details.cheque_id
    if payment_details.billing_id:
        billing_obj = await Billing.fetch(key=payment_details.billing_id)
        cheque_id = billing_obj.cheque_id

    if cheque_id:
        pay_in_cheque_obj = await ChequeDetails.fetch(key=cheque_id)
        response_dict["pay_in_slip_details"] = {
            "reconciled_cheque_no": pay_in_cheque_obj.cheque_number,
            "reconciled_cheque_date": pay_in_cheque_obj.cheque_date,
            "reconciled_cheque_bank": pay_in_cheque_obj.bank_id,
            "reconciled_cheque_branch": pay_in_cheque_obj.bank_branch_and_city,
            "reconciled_cheque_amount": pay_in_cheque_obj.cheque_amount,
            "reconciled_bank_city_id": pay_in_cheque_obj.city_id,
            "unique_reference_no": pay_in_cheque_obj.unique_reference_number,
        }
        if pay_in_cheque_obj.pay_in_slip_id:
            pay_in_slip_obj = await PayInSlip.fetch(key=pay_in_cheque_obj.pay_in_slip_id)
            response_dict["pay_in_slip_details"].update({
                "pay_in_slip_date": pay_in_slip_obj.created_at.strftime('%m/%d/%Y'),
                "pay_in_slip_success_datetime": pay_in_slip_obj.modified_at,
                "pay_in_slip_no": pay_in_slip_obj.slip_number
            })

    return PaymentResponse(**response_dict)


@router.patch("/update_payment/")
async def update_payment_data(request: Request, payment_data: UpdatePaymentRequest) -> PaymentResponse:
    logger.info( f"Updating requested payment data , request_data : {payment_data}")
    if payment_data.create_policy and payment_data.create_endorsement:
        raise InvalidInputException(
            name='apis.version1.payment.update_payment_data',
            message='Both endorsement and policy creation flag can not be true')

    payment_state_obj = await PaymentState.fetch_by_code(code='success')

    payment_obj = await Payment.fetch(key=payment_data.payment_id)
    if payment_data.payment_state_id:
        if payment_data.payment_state_id == payment_state_obj.id:
            service_url = SERVICE_CREDENTIALS["proposal"]["dns"] + f"/api/v1/update_ckyc_approval_status"
            ckyc_data = {
                'ckyc_approval_id': payment_data.ckyc_approval_id,
                'payment_status': 'success'
            }
            await AsyncHttpClient.patch(url=service_url, body=ckyc_data)

    if payment_data.payment_mode == (await PaymentMode.fetch_by_code(code="CC")).id:
        cheque = await create_or_update_cheque(data=payment_data, payment=payment_obj)
        await update_payment(data=payment_data, cheque=cheque)

    response_data = {
        "payment_id": payment_obj.id,
        "payment_amount": payment_obj.payment_amount,
        "transaction_id": payment_obj.transaction_id,
        "insurer_code": payment_obj.insurer_code,
        "payment_mode_id": payment_obj.payment_mode,
        "dealer_person": payment_obj.dealer_person,
        "sales_manager": payment_obj.sales_manager,
        "consent": payment_obj.consent_id,
        "proposal_number": payment_data.proposal_number,
        "endorsement_number": payment_obj.endorsement_number,
        "policy_number": payment_obj.policy_number
    }

    consent_state_obj = await ConsentState.fetch_by_code(code='done')
    consent_obj = await Consent.fetch(key=payment_obj.consent_id)
    consent_type_obj = await ConsentType.fetch_by_code(code='mandate')
    if consent_obj.consent_type != consent_type_obj.id:
        if consent_obj.consent_state != consent_state_obj.id:
            raise ConsentNotUpdatedException

    policy_obj_data = {}
    policy_data = {
        "transaction_id": payment_data.transaction_id,
        "insurer_code": payment_data.insurer_code,
        "policy_type_id": payment_data.policy_type_id,
        "model": payment_data.model,
        "variant": payment_data.variant,
        "insurer_name": payment_data.insurer_name,
        "insured_name": payment_data.insured_name,
        "proposal_type": payment_data.proposal_type,
        "dealer_name": payment_data.dealer_name,
        "dealer_code": payment_data.dealer_code,
        "registration_number": payment_data.registration_number,
        "create_policy": payment_data.create_policy,
        "proposal_number": payment_data.proposal_number,
        "chassis_number": payment_data.chassis_number,
        "engine_number": payment_data.engine_number,
        "policy_period": payment_data.policy_period,
        "policy_start_date": payment_data.policy_start_date,
        "policy_end_date": payment_data.policy_end_date,
        "policy_issuance_date": datetime.now().date().strftime("%d-%m-%Y")
    }
    policy_details = await create_policy(policy_data)
    if payment_data.create_policy:
        response_data["policy_number"] = policy_details["policy_number"]
        response_data["policy_document_url"] = policy_details["policy_pdf_url"]
        policy_obj_data["policy_number"] = policy_details["policy_number"]
        policy_obj_data["endorsement_number"] = policy_details.get('endorsement_number')

    else:
        response_data["proposal_number"] = payment_data.proposal_number

    if payment_data.payment_mode in [1, 2, 4]:
        policy_obj_data.update({
            "payment_mode": payment_data.payment_mode,
            "payment_amount": payment_data.payment_amount,
            "model": payment_data.model,
            "variant": payment_data.variant,
            "insurer_name": payment_data.insurer_name,
            "insured_name": payment_data.insured_name,
            "policy_start_date": datetime.strptime(payment_data.policy_start_date, "%d-%m-%Y"),
            "policy_end_date": datetime.strptime(payment_data.policy_end_date, "%d-%m-%Y"),
            "policy_issuance_date": datetime.strptime(payment_data.policy_start_date, "%d-%m-%Y"),
            "vehicle_cover_id": payment_data.vehicle_cover_id,
            "policy_type_id": payment_data.policy_type_id,
            "dealer_code": payment_data.dealer_code
        })
        await Payment.update(key=payment_obj.id, **policy_obj_data)
    try:
        logger.info( "Sending all the data to rb_coordinator for data ingestion")
        await send_to_rb_coordinator(transaction_id=payment_data.transaction_id, payment_status="payment_deducted")
    except Exception:
        logger.info( f"Exception occured while sending data to rb_coordinator : {str(Exception)}")
        pass
    if payment_data.create_endorsement:
        logger.info( f"Updating requested payment data for endorsement, request_data : {payment_data}")
        await payment_obj.update(key=payment_obj.id, **{"payment_amount": payment_data.payment_amount})

        endorsement_number = payment_obj.endorsement_number if payment_obj.endorsement_number else None
        if not endorsement_number:
            raise EndorsementNumberNotFoundException(message=f"Endorsement number not found for payment \
                                                               id {payment_obj.id} to create endorsement document")

        service_url = SERVICE_CREDENTIALS["policy"][
                          "dns"] + f"/api/v1/create_endorsement_document/?endorsement_number={endorsement_number}"

        response = await AsyncHttpClient.get(url=service_url)
        endorsement_document_url = response.get("document_url", None)
        response_data.update({
            "endorsement_document_url": endorsement_document_url
        })
    logger.info(
                f"updates the payment data in the database with response : {PaymentResponse(**response_data)} ")

    await payment_obj.update(key=payment_obj.id, **{"payment_state": payment_state_obj.id})
    return PaymentResponse(**response_data)


@router.post("/create_payment/")
async def create_payment_entry(payment_data: CreatePaymentRequest) -> PaymentResponse:
    logger.info( f" Creating payment entry with payment_data: {payment_data}")
    data = payment_data.dict()
    payment_state = await PaymentState.fetch_by_code(code='consent_pending')
    payment_status = await PaymentStatus.fetch_by_code(code='pending')
    if payment_data.consent_type_code == "mandate":
        consent_type = await ConsentType.fetch_by_code("mandate")
        consent_state = await ConsentState.fetch_by_code("done")
        consent_obj = await Consent.create(
            **{"consent_type": consent_type.id, "consent_state": consent_state.id,
               "transaction_id": payment_data.transaction_id})
        data["consent_id"] = consent_obj.id

    data['payment_state'] = payment_state.id
    data["payment_status"] = payment_status.id
    transaction_types = await get_transaction_types()
    transaction_type_id = ''
    for txn_type in transaction_types:
        if txn_type['code'] == 'policy':
            transaction_type_id = txn_type['id']

    data.update({"transaction_type_id": transaction_type_id})
    data.pop("consent_type_code")
    payment_obj = await Payment.create(**data)

    service_url = SERVICE_CREDENTIALS["cleverbridge"][
                      "dns"] + f"/api/v1/create-update-transaction/{payment_data.transaction_id}"
    await AsyncHttpClient.post(url=service_url, body={"entity_name": "payment", "entity_value": payment_obj.id})
    logger.info( " Successfully Created payment entry")
    response = PaymentResponse(
        payment_id=payment_obj.id,
        **data
    )

    return response


@router.post("/send_verification_mail/{transaction_id}")
async def send_consent_email(request: Request, transaction_id: str,
                             background_tasks: BackgroundTasks) -> SendEmailResponse:
    logger.info( f"sending consent email to transaction_id: {transaction_id}")
    consent_type_id = select(ConsentType.id).where(ConsentType.code == 'verification')
    consent_type_id = await sqldb.execute(consent_type_id)
    (consent_type_id,) = consent_type_id.one()

    consent_obj = select(Consent).where(Consent.transaction_id == transaction_id)
    consent_obj = await sqldb.execute(consent_obj)
    consent_obj = consent_obj.scalars().all()
    if consent_obj:
        consent_obj = consent_obj[0]
        consent_state = await ConsentState.fetch_by_code(code="done")
        if consent_obj.consent_state == consent_state.id:
            logger.info(
                        f"Consent for this transaction id already Done for transaction_id: {transaction_id}")
            return SendEmailResponse(
                status_code=400,
                message="Consent for this transaction id already Done.",
                consent_id=consent_obj.id
            )
        await Consent.update(key=consent_obj.id, **{"consent_type": consent_type_id})
    else:
        consent_state_id = select(ConsentState.id).where(ConsentState.code == 'pending')
        consent_state_id = await sqldb.execute(consent_state_id)
        (consent_state_id,) = consent_state_id.one()

        consent_obj = await Consent.create(
            **{"consent_type": consent_type_id, "consent_state": consent_state_id, "transaction_id": transaction_id})
    transaction_url = SERVICE_CREDENTIALS["cleverbridge"][
                          "dns"] + f"/api/v1/get-detailed-transaction/{transaction_id}"
    transaction_details = await AsyncHttpClient.get(url=transaction_url,
                                                    headers={"x-user-id": request.headers.get("x-user-id")})
    proposal_details = transaction_details['proposal_detail']
    proposal_id = proposal_details['proposal_id']

    proposal_url = SERVICE_CREDENTIALS["proposal"][
                       "dns"] + f"/api/v1/share_policy_preview/"
    request_body = {
        "proposal_id": proposal_id,
        "on_email": True,
        "subject": "Consent Verification Link",
        "template_slug": "consent_verification_link",
        "template_format_kwargs": {
            "customer_name": proposal_details["customer"]["first_name"],
            "success_url": f'{DOMAIN_ADDRESS_SERVER}/api/v1/update_consent_status?'
                           f'consent_state=done&transaction_id={transaction_id}',
            "failure_url": f'{DOMAIN_ADDRESS_SERVER}/api/v1/update_consent_status?'
                           f'consent_state=failed&transaction_id={transaction_id}'
        }
    }
    response = await AsyncHttpClient.post(url=proposal_url, body=request_body)
    logger.info( "Verification Link sent on email successfully")
    return SendEmailResponse(
        status_code=200,
        message="Verification Link sent on email successfully",
        consent_id=consent_obj.id
    )


@router.post("/send_consent_otp/{transaction_id}")
async def send_consent_otp(transaction_id: str, background_tasks: BackgroundTasks, on_email: bool = False
                           ) -> SendEmailResponse:
    logger.info( f"Sending otp for transaction_id: {transaction_id}")
    consent_type_id = select(ConsentType.id).where(ConsentType.code == 'otp')
    consent_type_id = await sqldb.execute(consent_type_id)
    (consent_type_id,) = consent_type_id.one()

    consent_obj = select(Consent).where(Consent.transaction_id == transaction_id)
    consent_obj = await sqldb.execute(consent_obj)
    consent_obj = consent_obj.scalars().all()
    if consent_obj:
        consent_obj = consent_obj[0]
        consent_state = await ConsentState.fetch_by_code(code="done")
        if consent_obj.consent_state == consent_state.id:
            logger.info(
                        f"Consent for this transaction id already Done for transaction_id: {transaction_id}")
            return SendEmailResponse(
                status_code=400,
                message="Consent for this transaction id already Done.",
                consent_id=consent_obj.id

            )
        await Consent.update(key=consent_obj.id, **{"consent_type": consent_type_id})
    else:
        consent_state_id = select(ConsentState.id).where(ConsentState.code == 'pending')
        consent_state_id = await sqldb.execute(consent_state_id)
        (consent_state_id,) = consent_state_id.one()

        consent_obj = await Consent.create(
            **{"consent_type": consent_type_id, "consent_state": consent_state_id, "transaction_id": transaction_id})

    proposal_url = SERVICE_CREDENTIALS["proposal"][
                       "dns"] + f"/api/v1/get_proposal_by_transaction/{transaction_id}"
    otp = await generate_otp()
    proposal_details = await AsyncHttpClient.get(url=proposal_url)
    otp_obj_create_data = {
        "transaction_id": transaction_id,
        "otp": otp,
        "valid_till": datetime.now() + timedelta(seconds=OTP_EXPIRY_SEC)
    }
    await OTP.create(**otp_obj_create_data)
    message_data = {
        "template_slug": "consent_verification_otp",
        "mobile": proposal_details["customer"]["mobile"] or proposal_details["customer"]["phone"],
        "template_format_kwargs": {
            "customer_name": proposal_details["customer"]["first_name"],
            "otp": otp,
            "premium_amt": proposal_details["total_premium"],
            "insurer_name": proposal_details["insurer_code"],
            "proposal_no": proposal_details["proposal_number"]
        }
    }
    if on_email:
        message_data["email"] = proposal_details["email_id"]
    background_tasks.add_task(AsyncKafkaProducer.push_otp_to_kafka_topic, data=message_data)
    logger.info( f"OTP sent successfully for transaction_id: {transaction_id}")
    return SendEmailResponse(
        status_code=200,
        message="OTP sent successfully",
        consent_id=consent_obj.id
    )


@router.get("/verify_consent_otp/{transaction_id}/{otp}", response_class=JSONResponse)
async def verify_consent_otp(transaction_id: str, otp: str):
    logger.info( f"Verification of consent otp against transaction_id : {transaction_id}")
    query = select(OTP).where(OTP.transaction_id == transaction_id)
    results = await sqldb.execute(query)
    otp_obj = results.scalars().all()
    otp_obj = otp_obj[-1]
    if otp_obj.valid_till < datetime.now():
        logger.info( f"OTP expired , request new otp against transaction_id : {transaction_id}")
        return JSONResponse(
            content={
                "status": False,
                "message": "OTP expired. Please request new OTP."
            }
        )
    if otp_obj.otp != otp:
        logger.info( f"Invalid OTP")
        return JSONResponse(
            content={
                "status": False,
                "message": "OTP is not valid."
            }
        )

    await update_consent_state(consent_state="done", transaction_id=transaction_id)
    logger.info( f"OTP verify successfully against transaction_id : {transaction_id}")
    return JSONResponse(
        content={
            "status": True,
            "message": "OTP verify successfully."
        }
    )


@router.get("/update_consent_status/")
async def update_consent_state(consent_state: str, transaction_id: str) -> UpdateConsentStateSchema:
    logger.info( f"Updating consent state to {consent_state} against transaction_id: {transaction_id}")
    consent_state_id = select(ConsentState.id).where(ConsentState.code == consent_state)
    consent_state_id = await sqldb.execute(consent_state_id)
    (consent_state_id,) = consent_state_id.one()

    consent_obj = select(Consent).where(Consent.transaction_id == transaction_id)
    consent_obj = await sqldb.execute(consent_obj)
    consent_obj = consent_obj.scalars().all()
    if consent_obj:
        consent_obj = consent_obj[0]
        consent_state = await ConsentState.fetch_by_code(code="done")
        if consent_obj.consent_state == consent_state.id:
            logger.info(f"Consent for this transaction id {transaction_id} already Done")
            return UpdateConsentStateSchema(
                status_code=400,
                message="Consent for this transaction id already Done."
            )
        await Consent.update(key=consent_obj.id, **{"consent_state": consent_state_id})
        logger.info(f"Consent state updated successfully to {consent_state}")
        return UpdateConsentStateSchema(
            status_code=200,
            message="Consent state updated successfully."
        )
    logger.info(f"Consent not found for this transaction {transaction_id}.")
    return UpdateConsentStateSchema(
        status_code=400,
        message="Consent not found for this transaction."
    )


# @router.get("/cheque_status/")
# async def get_cheque_status(req: Request, request: ChequeStatusRequest = Depends()) -> List[ChequeStatusResponse]:
#     filter_query = {}
#     for data in request:
#         if data[0] == 'payment_mode' and data[1]:
#             filter_query.update({'cheque_type': CHEQUE_TYPE_ENUM(data[1])})
#         elif data[1]:
#             filter_query.update({data[0]: data[1]})
#     transaction_types = await get_transaction_types()
#     if not transaction_types:
#         raise DataverseNotRespondingError(message='Unable to get response from dataverse to get transaction type')
#
#     user_details = await get_user_details(user_id=req.headers.get('x-user-id'))
#     query = select(ChequeDetails).filter(ChequeDetails.dealer_code == user_details["dealer_code"])
#     if request.start_date and request.end_date:
#         [filter_query.pop(key) for key in ['start_date', 'end_date']]
#         query = query.filter(ChequeDetails.cheque_date >= request.start_date,
#                              ChequeDetails.cheque_date <= request.end_date)
#     query = query.filter_by(**filter_query)
#     results = await sqldb.execute(query)
#     cheque_details_objs = results.all()
#     result_list = []
#     for cheque_details_obj in cheque_details_objs:
#         cheque_details_obj = cheque_details_obj[0]
#         payment_status = await PaymentStatus.fetch(key=cheque_details_obj.payment_status, )
#         transaction_type = transaction_types[0]['name']
#         for txn_type in transaction_types:
#             if txn_type['id'] == cheque_details_obj.transaction_type_id:
#                 transaction_type = txn_type['name']
#         result_list.append(ChequeStatusResponse(
#             transaction_type=transaction_type,
#             transaction_date=cheque_details_obj.cheque_date,
#             amount=cheque_details_obj.cheque_amount,
#             payment_mode=cheque_details_obj.cheque_type.name,
#             cheque_number=cheque_details_obj.cheque_number,
#             status=payment_status.name,
#             remark=payment_status.name
#         ))
#     return result_list


@router.get('/get_cheque_details/', response_model=ChequeDetailsResponse)
async def get_cheque_details(cheque_id: int):
    logger.info( f"Fetching cheque details for cheque_id {cheque_id}")
    cheque = await ChequeDetails.fetch(key=cheque_id)
    dataverse_data = await ChequeDetailServices.get_policy_summary_data(_ids=[("bank_id", cheque.bank_id)])
    bank_name = dataverse_data['bank'].get('name')
    response_data = {
        "transaction_type_id": "policy" if cheque.transaction_type_id == 1 else "endorsement",
        "cheque_number": cheque.cheque_number,
        "cheque_date": cheque.created_at.strftime("%d-%m-%Y"),
        "bank_name": bank_name,
        "bank_branch_and_city": cheque.bank_branch_and_city,
        "account_number": cheque.account_number,
        "cheque_type": cheque.cheque_type.name.lower(),
        "unique_reference_number": cheque.unique_reference_number,
        "cheque_amount": cheque.cheque_amount,
        "clearance_date": cheque.clearance_date.strftime("%d-%m-%Y") if cheque.clearance_date else None
    }
    return response_data


@router.post("/create_endorsement_payment/")
async def create_endorsement_payment(request: Request, endorsement_number: str, insurer_code: str) -> JSONResponse:
    logger.info(
                f"Creating endorsement payment against endorsement_number: {endorsement_number} for insurer_code {insurer_code}")
    service_url = SERVICE_CREDENTIALS["policy"][
                      "dns"] + f"/api/v1/get_endorsement_list/?endorsement_number={endorsement_number}"
    endorsement_response = await AsyncHttpClient.get(url=service_url,
                                                     headers={"x-user-id": request.headers.get('x-user-id')})
    endorsement_details = None
    if endorsement_response:
        endorsement_details = endorsement_response[0]
    if not endorsement_details:
        logger.info( f'Unable to get data from winterfell for endorsement_number: {endorsement_number}')
        raise EndorsementDataNotFoundException(
            name='apis.version1.payment.create_endorsement_payment',
            message=f'Unable to get data from winterfell for endorsement_number: {endorsement_number}')
    transaction_types = await get_transaction_types()
    transaction_type_id = [txn_type['id'] for txn_type in transaction_types if txn_type['code'] == 'endorsement']

    consent_obj = await ConsentState.fetch_by_code(code="done")
    consent_obj_id = select(Consent.id).where(Consent.transaction_id == endorsement_details['transaction_id'],
                                              Consent.consent_state == consent_obj.id)
    consent_obj_id = await sqldb.execute(consent_obj_id)
    (consent_obj_id,) = consent_obj_id.one()

    payment_state = await PaymentState.fetch_by_code(code='consent_done')
    payment_data = {
        "transaction_type_id": transaction_type_id[0],
        "transaction_id": endorsement_details['transaction_id'],
        "insurer_code": insurer_code,
        "dealer_person": endorsement_details.get('dealer_name'),
        "insured_name": endorsement_details.get('insured_name'),
        "model": endorsement_details.get('model'),
        "variant": endorsement_details.get('variant'),
        "policy_number": endorsement_details.get('policy_number'),
        "consent_id": consent_obj_id,
        "endorsement_number": endorsement_number,
        "payment_state": payment_state.id
    }
    payment = await Payment.create(**payment_data)
    service_url = SERVICE_CREDENTIALS["policy"]["dns"] + "/api/v1/update_endorsement_data/"
    request_data = {
        'endorsement_number': endorsement_number,
        'new_payment_id': payment.id,
        'endorsement_state_code': "accepted"
    }
    await AsyncHttpClient.patch(url=service_url, body=request_data)
    logger.info(f"Payment created with endorsement_payment_id: {payment.id}")
    return JSONResponse(content={"endorsement_payment_id": payment.id})


@router.patch("/update_approval_details/")
async def update_approval_details(request: ApprovalDetailsRequest):
    logger.info( "Updating approval details")
    query = select(Payment).where(Payment.transaction_id == request.transaction_id)
    results = await sqldb.execute(query)
    (payment,) = results.one()
    await Payment.update(key=payment.id, **{"policy_number": request.policy_number})
    logger.info( f"Policy number:- {request.policy_number} successfully updated")
    return {"message": 'Policy number successfully updated'}


@router.get("/update_gateway_status/")
async def update_gateway_status(request: Request, data: str) -> RedirectResponse:
    """
    The update_gateway_status function updates the payment data of an online billing order.

    :param request: Request: Pass the request object to this function
    :param data: str: Encrypted data received from the gateway
    :return: A redirect response to the billing details page
    """
    logger.info( "updating the payment data of an online billing order")
    order_data = eval(fernet.decrypt(binascii.unhexlify(data)).decode())
    payment_status = await PaymentStatus.fetch_by_code(code=order_data['payment_status'])
    transaction_date = convert_str_to_datetime(order_data['transaction_date'])
    if order_data['reference_type'] == 'billing':
        await Billing.update(key=int(order_data['reference_id']), billing_status=payment_status.id)
        return_url = f"{DOMAIN_ADDRESS_SERVER}/billings/payments/payment-details"
        payment_data = await sqldb.execute(
            select(Payment.id).where(Payment.billing_id == int(order_data['reference_id'])))
        payment_ids = payment_data.scalars().all()
    else:
        payment_ids = [int(order_data['reference_id'])]
        payment = await Payment.fetch(key=int(order_data['reference_id']))
        return_url = f"{DOMAIN_ADDRESS_SERVER}/policy/quotes/{payment.transaction_id}/proposals"

    new_payment_data = {
        "order_id": order_data['order_id'],
        "bank_ref_no": order_data['bank_ref_no'],
        "transaction_date": transaction_date
    }
    if payment_status.code == 'failure':
        payment_state = await PaymentState.fetch_by_code(code='payment_failed')
        payment_status = await PaymentStatus.fetch_by_code(code='failure')
        new_payment_data.update({
            "payment_state": payment_state.id,
            "payment_status": payment_status.id
        })
    elif payment_status.code == 'success':
        payment_state = await PaymentState.fetch_by_code(code='success')
        payment_status = await PaymentStatus.fetch_by_code(code='success')
        new_payment_data.update({
            "payment_state": payment_state.id,
            "payment_status": payment_status.id
        })
    paylink_payment_mode = await PaymentMode.fetch_by_code(code='paylink')
    for payment_id in payment_ids:
        await Payment.update(key=payment_id, **new_payment_data)
        results = await sqldb.execute(
            select(Payment.payment_mode, Payment.insurer_code).filter(Payment.id == payment_id))
        payment_mode, insurer_code = results.first()
        if await check_insurer_payment_integrated(insurer_code=insurer_code):
            await send_online_payment_details_to_insurer(payment_id=payment_id,
                                                         billing_id=int(order_data['reference_id']))
        if payment_mode == paylink_payment_mode:
            update_payment_request = await generate_update_payment_request(payment_id=payment_id)
            # temporary fix
            await update_payment_data(request=request, payment_data=UpdatePaymentRequest(**update_payment_request))
    return responses.RedirectResponse(return_url, status_code=status.HTTP_302_FOUND)


@router.post("/create_payment_mode_dealer_mapping/")
async def create_payment_mode_dealer_mapping(request: PaymentDealerRequest):
    logger.info( f"Mapping payment Mode {request.payment_mode_code} with dealer_code {request.dealer_code}")
    try:
        for payment_mode in request.payment_mode_code:
            payment_mode_obj = await PaymentMode.fetch_by_code(code=payment_mode)
            payment_request = {
                "payment_mode_id": payment_mode_obj.id,
                "dealer_code": request.dealer_code
            }
            await DealerPaymentMapping.create(**payment_request)
        logger.info("Payment mode successfully mapped with dealer")
        return {"message": 'Payment mode successfully mapped with dealer'}
    except Exception as e:
        logger.info( f"Exception occurred:{str(e)}")
        return e


@router.get("/fetch_payment_state_for_payment_id/")
async def fetch_payment_state_for_payment_id(payment_id: int) -> PaymentStateResponse:
    logger.info( f"Fetching Payment state for payment_id: {payment_id}")
    payment = await Payment.fetch(key=payment_id)
    payment_state = await PaymentState.fetch(key=payment.payment_state)
    return PaymentStateResponse(**payment_state.__dict__, amount=payment.payment_amount, order_id=payment.order_id)


@router.post("/convert_online_payments_to_cheque/")
async def convert_online_payments_to_cheque(payment_data: List[OnlineToChequeRequest]) -> SuccessResponse:
    logger.info( f"converting online payments to cheque for payment_ids: {payment_data}")
    payment_mode = await PaymentMode.fetch_by_code(code='DC')
    for payment in payment_data:
        await Payment.update(key=payment.payment_id, payment_mode=payment_mode.id)
    logger.info("Payments have been converted into dealer's cheque")
    return SuccessResponse(
        status_code=200,
        message="Payments have been converted into dealer's cheque"
    )


@router.get("/expired_online_payments/")
async def get_expired_online_payments() -> List[ExpiredOnlinePaymentResponse]:
    logger.info( "Fetching expired online payments")
    online_payment_mode = await PaymentMode.fetch_by_code(code='online_payment')
    pending_payment_status = await PaymentStatus.fetch_by_code(code='pending')
    query = select(Payment).where(Payment.payment_mode == online_payment_mode.id,
                                  Payment.payment_status == pending_payment_status.id,
                                  Payment.billing_id == None,
                                  Payment.policy_start_date < datetime.now().date())
    results = await sqldb.execute(query)
    online_pending_payments = results.scalars().all()
    return [ExpiredOnlinePaymentResponse(**payment.__dict__) for payment in online_pending_payments]


@router.get("/check_payment_status/")
async def check_payment_status(request: Request, payment_id: int) -> Union[
    ValidCheckPaymentStatusResponse, InValidResponse]:
    logger.info( f"Checking payment status for payment_id: {payment_id}")
    payment = await Payment.fetch(key=payment_id)
    query = select(PaymentStatus.id).where(PaymentStatus.code.in_(('success', 'failure')))
    results = await sqldb.execute(query)
    final_payment_status = results.scalars().all()
    if payment.payment_status in final_payment_status:
        logger.info("No need to update payment as payment is already in success or failure state")
        raise FinalizedPaymentStatus(name='app.apis.version1.payment',
                                     message='No need to update payment as payment is already in success or failure state')
    callback_url = SERVICE_CREDENTIALS["callback"][
                       "dns"] + f"/api/v1/check_order_status/?order_id={payment.order_id}"
    order_status_data = await AsyncHttpClient.get(url=callback_url,
                                                  headers={"x-user-id": request.headers.get("x-user-id")})
    if order_status_data.get('order_status'):
        logger.info( "Successfully fetched payment_status")
        return ValidCheckPaymentStatusResponse(
            payment_status=order_status_data['order_status']
        )
    else:
        logger.info( 'unable to fetch the status from payment gateway')
        return InValidResponse(
            error_message='unable to fetch the status from payment gateway'
        )


@router.get("/get_all_payment_details/")
async def get_all_payment_details(req: Request, request: PaymentStatusRequest = Depends()) -> \
        List[AllPaymentDetailsResponse]:
    """
    The get_all_payment_details function returns a list of all payment details.
    :param req: Request: Get the user id from the request header
    :param request: PaymentStatusRequest: Get the transaction type, payment mode and other
    :return: The list of payment status related details
    """
    logger.info( f"Fetching all payment details as requested: {request}")
    payment_mode = await PaymentMode.fetch(key=request.payment_mode)
    user_details = await get_user_details(user_id=req.headers.get('x-user-id'))
    filter_query = {"transaction_type_id": request.transaction_type_id, "payment_mode": request.payment_mode,
                    "dealer_code": user_details["dealer_code"]}
    payment_status = None
    if request.payment_status:
        filter_query['payment_status'] = request.payment_status
        payment_status = (await PaymentStatus.fetch(key=request.payment_status)).name
    if request.policy_number:
        filter_query['policy_number'] = request.policy_number
    if request.order_id:
        filter_query['order_id'] = request.order_id
    query = select(Payment).filter_by(**filter_query)
    if request.cheque_number:
        if payment_mode.code == 'DC':
            billing_ids = await get_billing_ids_by_cheque_number_for_dealer(cheque_number=request.cheque_number)
            query = query.filter(Payment.billing_id.in_(billing_ids))
        elif payment_mode.code == 'CC':
            cheque_ids = await get_cheque_ids_by_cheque_number_for_customer(cheque_number=request.cheque_number)
            query = query.filter(Payment.cheque_id.in_(cheque_ids))
    if request.start_date and request.end_date:
        query = query.filter(Payment.created_at >= request.start_date, Payment.created_at <= request.end_date)
    results = await sqldb.execute(query)
    payments = results.scalars().all()
    payment_list = []
    transaction_types = await get_transaction_types()
    if not transaction_types:
        logger.info( 'Unable to get response from dataverse to get transaction type')
        raise DataverseNotRespondingError(message='Unable to get response from dataverse to get transaction type')
    transaction_type = next(
        (txn_type['name'] for txn_type in transaction_types if txn_type['id'] == request.transaction_type_id), None)

    for payment in payments:
        cheque_number = None
        cheque_date = None
        if payment_mode.code == 'DC' and payment.billing_id:
            cheque_id = (await Billing.fetch(key=payment.billing_id)).cheque_id
            cheque_query = select(ChequeDetails.cheque_number, ChequeDetails.cheque_date).filter(
                ChequeDetails.id == cheque_id)
            results = await sqldb.execute(cheque_query)
            cheque_data = results.first()
            cheque_number, cheque_date = cheque_data if cheque_data else (None, None)
        elif payment_mode.code == 'CC' and payment.cheque_id:
            cheque_query = select(ChequeDetails.cheque_number, ChequeDetails.cheque_date).filter(
                ChequeDetails.id == payment.cheque_id)
            results = await sqldb.execute(cheque_query)
            cheque_data = results.first()
            cheque_number, cheque_date = cheque_data if cheque_data else (None, None)
        payment_state = await PaymentState.fetch(key=payment.payment_state)
        if not request.payment_status:
            payment_status = (
                await PaymentStatus.fetch(key=payment.payment_status)).name if payment.payment_status else None
        payment_list.append(AllPaymentDetailsResponse(
            payment_id=payment.id,
            policy_number=payment.policy_number,
            transaction_type=transaction_type,
            transaction_date=payment.transaction_date.date() if payment.transaction_date else None,
            cheque_date=cheque_date,
            payment_status=payment_status,
            order_id=payment.order_id,
            cheque_number=cheque_number,
            verify_status='ReCheck',
            vb64_status=payment_state.name,
            vb64_remarks=payment_state.name,
            payment_mode=payment_mode.name,
            amount=payment.payment_amount
        ))
    logger.info( "Successfully fetched the payment_details")
    return payment_list


@router.get("/get_payment_status/")
async def get_payment_status(transaction_id) -> PaymentStatusAndModeResponse:
    """
        The get_payment_status function returns the status and mode of a payment.
            Args:
                transaction_id (str): The unique identifier for the payment.

        :param transaction_id: Get the payment status and payment mode of a particular transaction
        :return: The payment status and payment mode of the given transaction id
    """
    try:
        logger.info(f"Fetching payment status against tranaction_id: {transaction_id}")
        payment = (await sqldb.execute(select(Payment).where(
            Payment.transaction_id == transaction_id).order_by(Payment.id.desc()))).scalars().first()
        payment_status = (await PaymentStatus.fetch(key=payment.payment_status)).code
        payment_mode = (await PaymentMode.fetch(key=payment.payment_mode)).code
        return PaymentStatusAndModeResponse(
            payment_status=payment_status,
            payment_mode=payment_mode
        )
    except:
        logger.info("No payment detail found for this transaction_id")
        raise PaymentNotFoundException(message="No payment detail found for this transaction_id")


@router.get("/get_delayed_payment_list/")
async def get_delayed_payment_list(insurer_code: str) -> List[DelayedPaymentDetailsResponse]:
    """
    The get_delayed_payment_list function returns a list of payments whose payment is delayed for 12 days after
    payment tagged. Each object contains the payment_state, payment_id, modified_at date and time, insurer code and
    dealer code for each delayed payment.
    :return: A list of DelayedPaymentDetailsResponse objects
    """
    logger.info( f"Getting list of delayed payment for insurer_code: {insurer_code}")
    vb64_pending_obj = await PaymentState.fetch_by_code(code="vb64_pending")
    vb64_success_obj = await PaymentState.fetch_by_code(code="vb64_verified")
    target_date = datetime.utcnow().date() - timedelta(days=12)
    vb64_failure_obj = await PaymentState.fetch_by_code(code="vb64_not_verified")
    payment_details = (
        await sqldb.execute(
            select(
                Payment.dealer_code, Payment.insurer_code, Payment.payment_state, func.count(Payment.id)
            ).where(
                Payment.payment_state.in_((vb64_success_obj.id, vb64_failure_obj.id, vb64_pending_obj.id)),
                Payment.modified_at >= target_date, Payment.insurer_code == insurer_code
            ).group_by(
                Payment.dealer_code, Payment.insurer_code, Payment.payment_state
            )
        )
    ).all()
    delayed_payment_list = []
    for payment in payment_details:
        delayed_payment_list.append(
            DelayedPaymentDetailsResponse(dealer_code=payment[0],
                                          insurer_code=payment[1],
                                          transaction_count=payment[2],
                                          is_vb64_verified=True if payment[3] == vb64_success_obj.id else False
                                          ))
    logger.info("Successfully fetched the list of delayed payments")
    return delayed_payment_list


@router.get("/check_new_endorsement_allowed/")
async def check_new_endorsement_allowed(transaction_id: str) -> List:
    """
    The check_new_endorsement_allowed function is used to check if a new endorsement can be created or not.
        It checks the payment state of all payments associated with the transaction_id and returns a list of unverified
        payments. If there are no unverified payments, it returns an empty list else list of endorsement numbers.

    :param transaction_id: str: Fetch the payment_state of a transaction
    :return: A list of unverified payments
    :doc-author: Ramkishor Beniwal
    """
    logger.info( f"checking if a new endorsement can be created or not for transaction_id {transaction_id}")
    verified_payment_states = await PaymentState.fetch_value_list(
        codes=["payment_pending", "payment_failed", "consent_pending", "vb64_verified"], value_list=["id"])
    allowed_payment_states = [payment_state_id for (payment_state_id,) in verified_payment_states]
    vb64_unverified_payments = (
        await sqldb.execute(
            select(Payment.endorsement_number).where(
                Payment.transaction_id == transaction_id,
                Payment.payment_state.not_in(allowed_payment_states)))).scalars().all()

    logger.info(
                f"unverified endorsement list for transaction_id {transaction_id}: {vb64_unverified_payments}")
    if None in vb64_unverified_payments:
        return []
    else:
        logger.info( "Getting unverified payments")
        return vb64_unverified_payments


@router.get("/check_endorsement_payment/")
async def check_endorsement_payment(endorsement_number: str) -> bool:
    """
    The check_endorsement_payment function checks if the payment is done or not for a given endorsement number.
        It returns True if the payment is done, else False.

    :param endorsement_number: str: Check if the payment is done or not for a particular endorsement
    :return: A boolean value
    :doc-author: Trelent
    """
    logger.info( f"Checking if payment is done or not for endorsement id {endorsement_number}.")
    allowed_payment_states = await PaymentState.fetch_value_list(
        codes=["payment_pending", "payment_failed", "consent_pending", "consent_done"], value_list=["id"])
    allowed_payment_states = [payment_state_id for (payment_state_id,) in allowed_payment_states]
    endorsement_payment_found = (
        await sqldb.execute(
            select(Payment.endorsement_number).where(
                Payment.endorsement_number == endorsement_number,
                Payment.payment_state.not_in(allowed_payment_states)
            )
        )
    ).scalars().all()
    return True if endorsement_payment_found else False

@router.post("/payment_amount_by_ids/")
async def get_payment_amount_by_ids(request: PaymentIdsRequest):
    payment_obj = await sqldb.execute(
        select(Payment.id, Payment.payment_amount).where(Payment.id.in_(map(int, request.payment_ids))))
    payment_data = payment_obj.all()
    return dict(payment_data)
