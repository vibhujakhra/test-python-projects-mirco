import codecs
import csv
import io
import logging
from datetime import timedelta

import aioboto3
import pandas as pd
from botocore.client import BaseClient
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.payment import *
from app.schemas.pay_in_slip import LockUnlockDealerResponse
from app.schemas.payment import *
from app.settings import SERVICE_CREDENTIALS
from app.utils.code_utils import send_to_rb_coordinator, upload_csv_to_s3, update_deposit_slip
from app.utils.exceptions import ColumnMisMatchError

router = APIRouter()
logger = logging.getLogger("api")
path = 'app/csv_templates/'


def get_async_s3_client():
    async_s3_session = aioboto3.Session()
    return async_s3_session


@router.post("/upload_64vb/")
async def upload_64vb(request: Request, upload_request: UploadVB64Request = Depends(),
                      async_s3_client: BaseClient = Depends(get_async_s3_client)) -> SuccessResponse:
    """
    The upload_64vb function is used to upload 64vb file.
        Args:
            upload_request (UploadVB64Request): The request object containing the uploaded file and other details.
            async_s3_client (BaseClient): The s3 client instance for uploading the document to s3 bucket.

    :param upload_request: UploadVB64Request: Get the request data
    :param async_s3_client: BaseClient: Get the s3 client object
    :return: A successresponse object
    :Sample CSV File:
    _____________________________________________________________________________________________________________
    |POLICY_NUMBER      | CLEARANCE_DATE |  CHEQUE_NUMBER   | BANK_NAME                        |CLEARANCE_STATUS |
    |996692323750002002 | 03-04-2023     | 123458           | ABCD BANK                        | clear           |
    |996692323750001988 | 03-04-2023     | 123450           | A B E CO OPERATIVE BANK LTD      | clear           |
    |996692323750001998 | 03-04-2023     | 123456           | ABHINANDAN URBAN CO OP BANK LTD  | clear           |
    |996692323750001999 | 03-04-2023     | 123456           | ABHINANDAN URBAN CO OP BANK LTD  | clear           |
    |___________________|________________|__________________|__________________________________|_________________|

    """
    logger.info( "Uploading vb64 data into database")
    vb64_records = csv.DictReader(codecs.iterdecode(upload_request.document_file.file, 'utf-8'))
    required_headers = {"POLICY_NUMBER", "CLEARANCE_STATUS", "CLEARANCE_DATE", "CHEQUE_NUMBER", "BANK_NAME"}
    if upload_request.vb64_type_id == 2:
        required_headers.update({"ENDORSEMENT_NUMBER"})
    if not set(vb64_records.fieldnames) == required_headers:
        logger.info( "File Columns are not matching with the required data")
        raise ColumnMisMatchError(message='File Columns are not matching with the required data')

    vb64_obj = await VB64.create(**{"vb64_type_id": upload_request.vb64_type_id})
    success_status_obj = await PaymentStatus.fetch_by_code(code="success")
    failure_status_obj = await PaymentStatus.fetch_by_code(code="failure")

    vb64_success_obj = await PaymentState.fetch_by_code(code="vb64_verified")
    vb64_failure_obj = await PaymentState.fetch_by_code(code="vb64_not_verified")
    vb64_pending_obj = await PaymentState.fetch_by_code(code="vb64_pending")

    query = select(PaymentMode.id).where(PaymentMode.code.in_(('online_payment', "paylink")))
    results = await sqldb.execute(query)
    online_payment_modes = results.scalars().all()

    success_records = failure_records = total_records = 0
    failure_download_url = None
    record_list = []
    updated_vb64_records = []
    failure_list = []

    for record in vb64_records:
        total_records += 1
        data = {
            "policy_number": record['POLICY_NUMBER'].replace("`", ""),
            "clearance_status": record['CLEARANCE_STATUS'],
            "remarks": '',
            "upload_status": ''
        }
        if upload_request.vb64_type_id == 2:
            data.update({"endorsement_number": record['ENDORSEMENT_NUMBER'].replace("`", "")})
            allowed_payment_states = await PaymentState.fetch_value_list(
                codes=["payment_pending", "payment_failed", "consent_pending", "consent_done"], value_list=["id"])
            allowed_payment_states = [payment_state_id for (payment_state_id,) in allowed_payment_states]
            payment_obj = select(Payment).where(
                Payment.endorsement_number == data.get("endorsement_number"),
                Payment.payment_state.not_in(allowed_payment_states))
            payment_obj = await sqldb.execute(payment_obj)
            payment_obj = payment_obj.scalars().first()
        else:
            payment_obj = select(Payment).where(Payment.policy_number == data.get("policy_number"))
            payment_obj = await sqldb.execute(payment_obj)
            payment_obj = payment_obj.scalars().first()

        billing_obj = None
        if payment_obj.billing_id:
            billing_obj = await Billing.fetch(key=payment_obj.billing_id)

        cheque_id = payment_obj.cheque_id or billing_obj.cheque_id
        clearance_date_obj = datetime.strptime(record['CLEARANCE_DATE'], "%d-%m-%Y").date() if record[
            'CLEARANCE_DATE'] else None
        filter_query = {
            "policy_number": data.get("policy_number"),
            "upload_status": "success"
        }
        if data.get("endorsement_number"):
            filter_query["endorsement_number"] = data.get("endorsement_number")
        vb64_upload_status = await sqldb.execute(select(VB64Record.id).filter_by(**filter_query))
        vb64_upload_status = vb64_upload_status.all()
        insurer_code = (await sqldb.execute(select(Payment.insurer_code).where(Payment.policy_number==filter_query['policy_number']))).scalars().first()
        if vb64_upload_status:
            failure_records += 1
            remarks = "Already Uploaded"
            upload_status = 'failure'

        elif insurer_code != request.headers.get('X-INSURER-CODE'):
            failure_records += 1
            remarks = f"Upload this 64vb file with the correct insurer: {insurer_code}"
            upload_status = 'failure'


        elif cheque_id:
            cheque_date = select(ChequeDetails.cheque_date).where(ChequeDetails.id == cheque_id)
            cheque_date = await sqldb.execute(cheque_date)
            (cheque_date,) = cheque_date.first()
            if cheque_date > clearance_date_obj:
                failure_records += 1
                await ChequeDetails.update(key=cheque_id, **{"payment_status": failure_status_obj.id})
                await Payment.update(key=payment_obj.id,
                                     **{"payment_state": vb64_failure_obj.id, "payment_status": failure_status_obj.id})
                remarks = "Unable to submit the record as cheque clearance date should be greater than cheque date"
                upload_status = 'failure'
                logger.info(f"{remarks} upload_status:{upload_status}")
                data.update({"clearance_status": "not_clear"})
            elif data.get("clearance_status").lower() == 'clear':
                success_records += 1
                await ChequeDetails.update(key=cheque_id, **{"payment_status": success_status_obj.id})
                await Payment.update(key=payment_obj.id,
                                     **{"payment_state": vb64_success_obj.id, "payment_status": success_status_obj.id})
                remarks = "VB64 record submitted successfully"
                upload_status = 'success'
                logger.info(f"{remarks} upload_status:{upload_status}")
                await update_deposit_slip(policy_number=data.get("policy_number"))
            elif data.get("clearance_status").lower() == 'not clear':
                success_records += 1
                await ChequeDetails.update(key=cheque_id, **{"payment_status": failure_status_obj.id})
                await Payment.update(key=payment_obj.id, **{"payment_state": vb64_failure_obj.id, "payment_status": failure_status_obj.id})
                remarks = "VB64 record submitted successfully with VB64 not verified status"
                upload_status = 'success'
                logger.info(f"{remarks} upload_status:{upload_status}")
        elif payment_obj.payment_mode in online_payment_modes:
            if data.get("clearance_status").lower() == 'clear':
                success_records += 1
                await Payment.update(key=payment_obj.id, **{"payment_state": vb64_success_obj.id})
                remarks = "VB64 record submitted successfully"
                upload_status = 'success'
                logger.info(f"{remarks} upload_status:{upload_status}")
                await update_deposit_slip(policy_number=data.get("policy_number"))
            elif data.get("clearance_status").lower() == 'not clear':
                success_records += 1
                await Payment.update(key=payment_obj.id, **{"payment_state": vb64_failure_obj.id})
                remarks = "VB64 record submitted successfully with VB64 not verified status"
                upload_status = 'success'
                logger.info(f"{remarks} upload_status:{upload_status}")

        vb64_data = {
            "vb64_id": vb64_obj.id,
            "policy_number": data.get("policy_number"),
            "bank_name": record['BANK_NAME'],
            "cheque_number": record['CHEQUE_NUMBER'],
            "upload_status": upload_status,
            "remarks": remarks,
            "clearance_date": clearance_date_obj,
            "clearance_status": data.get("clearance_status")
        }
        if upload_request.vb64_type_id == 2:
            vb64_data.update({"endorsement_number": data.get("endorsement_number")})
        await VB64Record.create(**vb64_data)
        payment_status = "success" if (data.get("clearance_status").lower() == "clear") else "failure"
        try:
            logger.info("Sending payment status and updated data to rb_coordinator for data ingestion")
            await send_to_rb_coordinator(transaction_id=payment_obj.transaction_id, payment_status=payment_status)
        except Exception:
            logger.info("Not able to send data to rb_coordinator")
            pass
        record.update({
            'UPLOAD_STATUS': upload_status,
            'REMARKS': remarks
        })
        record_list.append(record)

        if upload_status == "failure":
            failure_list.append(record)
    if failure_list:
        await Payment.update(key=payment_obj.id,
                             **{"payment_state": vb64_pending_obj.id, "payment_status": failure_status_obj.id})
        file_name = f"failure_data_{vb64_obj.id}.csv"
        key = f"documents/motor/{file_name}"
        failure_download_url = await upload_csv_to_s3(key=key, data=failure_list, async_s3_client=async_s3_client)
    # if cheque_id:
    #     # TODO: Currently we are not generating pay in slip for online payments
    #     cheque_obj = await ChequeDetails.fetch(key=cheque_id)
    #     payin_slip_obj = await PayInSlip.fetch(key=cheque_obj.pay_in_slip_id)
    #     await update_payin_slip_and_vb64(policy_number=policy_number, pay_in_slip=payin_slip_obj.slip_number)

    # uploading vb64 document to s3 bucket
    file_name = f"{vb64_obj.id}.csv"
    key = f"documents/motor/{file_name}"
    download_url = await upload_csv_to_s3(key=key, data=record_list, async_s3_client=async_s3_client)
    vb64_update_data = {
        "vb64_type_id": upload_request.vb64_type_id,
        "uploaded_by": upload_request.uploaded_by,
        "upload_date": datetime.now().date(),
        "success_records": success_records,
        "failed_records": failure_records,
        "total_records": total_records,
        "file_location": download_url
    }
    await vb64_obj.update(key=vb64_obj.id, **vb64_update_data)

    message = '64vb file uploaded successfully'
    if success_records and failure_records:
        message = f"Successful Entries: {success_records} Failed Entries: {failure_records}.Please check the CSV for the Failed entries"
    elif not success_records and failure_records:
        message = "Unsuccessful! Please check the CSV for failure reason."
    logger.info( message)
    return SuccessResponse(
        status_code=200,
        message=message,
        failure_download_url=failure_download_url
    )


@router.post("/64vb_details/")
async def get_64vb_details(request: Request, vb_request: Get64VBRequest) -> List[Get64VBResponse]:
    # insurer_code = await check_insurer_headers(request)
    logger.info("Fetching 64vb details as requested")
    query = select(VB64).where(VB64.vb64_type_id == vb_request.vb64_type_id,
                               VB64.upload_date >= vb_request.start_date,
                               VB64.upload_date <= vb_request.end_date)
    #    VB64.insurer_code == insurer_code)
    results = await sqldb.execute(query)
    vb64_details = results.all()
    complete_data = [Get64VBResponse(**data[0].__dict__) for data in vb64_details]
    return complete_data


@router.get("/download_vb64_template/{service_type}/")
async def download_vb64_template(service_type: str):
    """
        The download_template function is used to download a CSV template for the specified service type.

        :param service_type: str: Determine which template to download
        :return: A streaming response
    """
    logger.info(f"Download 64 vb templated for uploading data for {service_type}")
    file_path_dict = {
        "policy": path + 'policy_template.csv',
        "endorsement": path + 'endorsement_template.csv',
    }
    try:
        # Check if the requested file type is supported
        if service_type not in file_path_dict:
            raise ValueError(f"Unsupported file type '{service_type}'")
        # Read the CSV file
        template_loc = file_path_dict[service_type]
        df = pd.read_csv(template_loc)
        # Convert the DataFrame to a CSV string
        csv_string = df.to_csv(index=False)
        headers = {
            "Content-Disposition": f"attachment; filename={service_type}.csv",
            "Content-Type": "text/csv",
        }
        # Return the response as a streaming response
        return StreamingResponse(io.StringIO(csv_string), media_type="text/csv", headers=headers)

    except Exception as e:
        logger.info( f"Error downloading {service_type}.csv: {str(e)}")
        return {"message": f"Error downloading {service_type}.csv: {str(e)}"}


@router.get('/vb64_lock_and_unlock_dealer/')
async def vb64_lock_and_unlock_dealer(dealer_code: str) -> LockUnlockDealerResponse:
    """
    The vb64_lock_and_unlock_dealer function is used to lock and unlock the dealer account.
        The function will check if there are any payments which have been pending 64vb for more than 15 days.
        If yes, then it will return a list of all such payments along with the message that your account has been locked due to 64 VB not verified.
        Else, it will return a message that your account has been unlocked.

    :param dealer_code: str: Fetch the dealer code from the database
    :return: The following:
    """
    logger.info( f"lock and unlock dealer: {dealer_code} according to vb64 status")
    service_url = SERVICE_CREDENTIALS["dataverse"][
                      "dns"] + f"/api/v1/transaction_type/"

    transaction_type_resp = await AsyncHttpClient.get(url=service_url)
    transaction_type_dict = {transaction_type['id']: transaction_type['name'] for transaction_type in
                             transaction_type_resp}
    vb64_pending_id = (await PaymentState.fetch_by_code(code="vb64_pending")).id
    vb64_failure_id = (await PaymentState.fetch_by_code(code="vb64_not_verified")).id
    payments = (
        await sqldb.execute(
            select(
                Payment
            ).where(
                Payment.payment_state.in_((vb64_failure_id, vb64_pending_id)), Payment.dealer_code == dealer_code
            )
        )
    ).scalars().all()
    locked_due_to_64vb_not_verified = []

    for payment in payments:
        if payment.modified_at + timedelta(days=15) <= datetime.utcnow():
            locked_due_to_64vb_not_verified.append(payment)

    if locked_due_to_64vb_not_verified:
        payment_dict = {}
        for payment in locked_due_to_64vb_not_verified:
            key_to_check = (payment.transaction_type_id, payment.insurer_code)
            transaction_type_name = transaction_type_dict.get(payment.transaction_type_id)
            if key_to_check in payment_dict:
                payment_dict[key_to_check]['cheque_count'] += 1
            else:
                payment_dict[key_to_check] = {
                    "insurer_code": payment.insurer_code,
                    "transaction_type_id": payment.transaction_type_id,
                    "transaction_type_name": transaction_type_name,
                    "cheque_count": 1
                }
        logger.info(f"account is locked as 64 VB is pending against dealer_code: {dealer_code}")
        return LockUnlockDealerResponse(
            message="Dear user your account is locked as 64 VB is pending for below mentioned policies .",
            issue_type="vb64_not_verified",
            payments=list(payment_dict.values()),
            status_code=200
        )

    else:
        # If all payments are unlocked
        logger.info(f"account is unlocked against dealer_code: {dealer_code}")
        return LockUnlockDealerResponse(
            message="Dear user your account is unlocked.",
            issue_type=None,
            payments=None,
            status_code=200
        )


@router.post("/vb64_certificate_data/")
async def get_vb64_certificate_payment_data(policy_numbers: dict) -> List[dict]:
    logger.info("Fetching vb64 certificate payment data for requested policy numbers ")
    results = await sqldb.execute(
        select(VB64Record).filter(VB64Record.policy_number.in_(policy_numbers['policy_numbers'])))
    vb64_records = results.scalars().all()
    record_list = []
    result_dict = {}
    for record in vb64_records:
        results = await sqldb.execute(
            select(Payment.payment_amount).where(Payment.policy_number == record.policy_number))
        payment_amount = results.scalars().first()
        result_dict[record.policy_number] = {"vb64_certificate_url": record.vb64_certificate_url,
                                             "premium": payment_amount}
        record_list.append(result_dict)
    logger.info("successfully fetched vb64 certificate payment data for requested policy numbers")
    return record_list
