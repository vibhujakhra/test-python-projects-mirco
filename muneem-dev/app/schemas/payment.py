from datetime import date, datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel, validator


class BaseResponse(BaseModel):
    id: int
    name: str


class ConsentTypeResponse(BaseResponse):
    code: str


class ConsentStateResponse(BaseResponse):
    pass


class PaymentStateResponse(BaseResponse):
    id: int
    name: str
    code: Optional[str]
    amount: Optional[int]
    order_id: Optional[str]


class PaymentModeResponse(BaseResponse):
    id: int
    name: str
    code: Optional[str]


class PaymentStatusResponse(BaseResponse):
    pass


class ConsentResponse(BaseModel):
    consent_id: int
    consent_type: str
    consent_state: str


class PaymentResponse(BaseModel):
    payment_id: int
    transaction_id: str
    insurer_code: str
    payment_state_id: int = None
    payment_state: Optional[str]
    payment_status: Optional[str]
    payment_mode_id: int = None
    dealer_person: Optional[str]
    sales_manager: Optional[str]
    consent_id: int = None
    payment_amount: int
    proposal_number: Optional[str]
    payment_mode: Optional[str]
    policy_number: Optional[str]
    policy_document_url: Optional[str]
    endorsement_number: Optional[str] = None
    endorsement_document_url: Optional[str]
    policy_type_id: Optional[int]
    vehicle_cover_id: Optional[int]
    pay_in_slip_details: Optional[dict]


class PaymentUpdateFailResponse(BaseModel):
    payment_id: int
    error_message: str


class CustomerChequeResponse(BaseModel):
    payment_id: int
    cheque_number: str
    cheque_date: date
    account_number: int
    bank_id: int
    city_id: int


class CustomerChequeRequest(BaseModel):
    # payment_mode: int
    payment_id: int
    cheque_number: str
    cheque_date: date
    account_number: int
    bank_id: int
    city_id: int


class CreatePaymentRequest(BaseModel):
    transaction_id: str
    insurer_code: str
    consent_id: Optional[int]
    consent_type_code: str
    dealer_person: str
    sales_manager: str
    payment_amount: float

    @validator("payment_amount", pre=True)
    def return_round_value(cls, value):
        return round(value) if value else 0


class UpdatePaymentRequest(BaseModel):
    payment_mode: int
    payment_id: int
    transaction_id: str
    policy_type_id: int
    insurer_code: str
    model: str
    variant: str
    insured_name: str
    payment_amount: float
    proposal_type: str
    dealer_code: str
    dealer_name: str
    insurer_name: str
    create_policy: bool
    create_endorsement: bool
    proposal_number: str
    engine_number: str
    chassis_number: str
    registration_number: Optional[str]
    cheque_number: Optional[str]
    cheque_date: Optional[str]
    account_number: Optional[str]
    bank_id: Optional[int]
    bank_branch_and_city: Optional[str]
    policy_period: int
    vehicle_cover_id: int
    policy_start_date: str
    policy_end_date: str
    payment_amount: Optional[int]
    payment_state_id: Optional[int]
    ckyc_approval_id: Optional[int]
    policy_number: Optional[str]

    @validator("payment_amount", pre=True)
    def return_round_value(cls, value):
        return round(value) if value else 0


class CommunicationResponse(BaseModel):
    status: int = 0
    error_message: str = ""
    response_data: dict = {}


class SendEmailRequest(BaseModel):
    to: List[str]
    payment_id: int
    cc: Optional[List[str]]
    bcc: Optional[List[str]]


class SendEmailResponse(BaseModel):
    status_code: int
    message: str
    consent_id: int


class UpdateConsentStateSchema(BaseModel):
    status_code: int
    message: str


class BillingPaymentResponse(BaseModel):
    policy_number: str
    insured_name: str
    insurer_code: str
    model: str
    variant: str
    payment_amount: int
    policy_issuance_date: date
    policy_start_date: date
    policy_end_date: date
    endorsement_number: Optional[str]

    @validator("policy_issuance_date", "policy_start_date", "policy_end_date")
    def date_to_str(cls, value):
        return value.strftime("%d-%m-%Y") if value else None


class CreateBillingRequest(BaseModel):
    transaction_type_id: Optional[int]
    payment_mode: Optional[int]
    insurer_code: str
    cheque_number: Optional[str]
    account_number: Optional[str]
    cheque_date: Optional[date]
    cheque_amount: int
    bank_id: Optional[int]
    city_id: Optional[int]
    bank_branch_and_city: Optional[str]
    payment_ids: List[int]
    dealer_code: Optional[str]
    dealer_name: Optional[str]

    @validator("cheque_date", pre=True)
    def str_to_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date() if value else None


class CreateBillingResponse(BaseModel):
    billing_id: int
    status_code: int
    message: str


class UploadVB64Request(BaseModel):
    vb64_type_id: int
    uploaded_by: Optional[str]
    document_file: UploadFile


class SuccessResponse(BaseModel):
    status_code: int
    message: str
    failure_download_url: Optional[str]


class Get64VBResponse(BaseModel):
    file_location: str
    upload_date: date
    uploaded_by: str = None
    success_records: int
    failed_records: int
    total_records: int

    @validator("upload_date")
    def date_to_str(cls, value):
        return value.strftime("%d-%m-%Y") if value else None


class Get64VBRequest(BaseModel):
    vb64_type_id: int
    start_date: str
    end_date: str

    @validator("start_date", "end_date")
    def str_to_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date() if value else None


class PaymentStatusRequest(BaseModel):
    transaction_type_id: int
    payment_mode: int
    policy_number: Optional[str]
    cheque_number: Optional[str]
    order_id: Optional[str]
    payment_status: Optional[int]
    start_date: Optional[str]
    end_date: Optional[str]

    @validator("start_date", "end_date")
    def str_to_date(cls, value):
        return datetime.strptime(value, "%d-%m-%Y").date() if value else None


class ChequeStatusResponse(BaseModel):
    transaction_type: str
    transaction_date: date
    amount: int
    payment_mode: str
    cheque_number: str
    status: str
    remark: str

    @validator("transaction_date")
    def date_to_str(cls, value):
        return value.strftime("%d-%m-%Y") if value else None


class ChequeDetailsResponse(BaseModel):
    transaction_type_id: str
    cheque_number: str
    cheque_date: str
    bank_name: str
    bank_branch_and_city: str
    account_number: str
    cheque_type: str
    unique_reference_number: str
    cheque_amount: int
    clearance_date: Optional[str]


class ApprovalDetailsRequest(BaseModel):
    transaction_id: str
    policy_number: str


class PaymentDealerRequest(BaseModel):
    payment_mode_code: List[str]
    dealer_code: str


class OnlineToChequeRequest(BaseModel):
    payment_id: int


class ExpiredOnlinePaymentResponse(BaseModel):
    id: int
    policy_start_date: str
    policy_number: str = None
    insured_name: str
    insurer_code: str

    @validator("policy_start_date", pre=True)
    def date_to_str(cls, value):
        return value.strftime("%d-%m-%Y") if value else None


class ValidCheckPaymentStatusResponse(BaseModel):
    payment_status: str


class PaymentStatusAndModeResponse(BaseModel):
    payment_status: str
    payment_mode: str


class InValidResponse(BaseModel):
    error_message: str


class AllPaymentDetailsResponse(BaseModel):
    payment_id: int
    amount: int
    policy_number: str = None
    cheque_number: str = None
    payment_mode: str
    order_id: str = None
    payment_status: str = None
    transaction_type: str
    transaction_date: str = None
    cheque_date: str = None
    verify_status: str
    vb64_status: str
    vb64_remarks: str

    @validator("transaction_date", "cheque_date", pre=True)
    def date_to_str(cls, value):
        return value.strftime("%d-%m-%Y") if value else None


class DelayedPaymentDetailsResponse(BaseModel):
    transaction_count: int
    insurer_code: str
    dealer_code: str = None
    is_vb64_verified: bool

class PaymentIdsRequest(BaseModel):
    payment_ids: List[str]
