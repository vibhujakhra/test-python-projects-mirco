from typing import Optional, List

from pydantic import BaseModel


class PaymentDataSchema(BaseModel):
    payment_amount: int
    policy_number: str
    policy_period: str
    insured_name: str
    endorsement_number: Optional[str]


class PayInSlipDataSchema(BaseModel):
    policy_number: str
    cheque_number: str
    bank: str
    bank_id: int
    cheque_id: int
    billing_id: Optional[int]
    bank_branch_and_city: str
    sub_payment_count: int
    cheque_date: str
    account_number: str
    endorsement_number: str = None
    cheque_amount: int
    policy_period: str
    insured_name: str
    policy_number: str
    paid_by: str


class ChequeDetailSchema(BaseModel):
    is_endorsement: bool
    data: List[PayInSlipDataSchema]


class MultipleChequeDetailSchema(BaseModel):
    data: List[PaymentDataSchema]


class ViewRowDataResponse(BaseModel):
    unique_reference_number: Optional[str]
    cheque_number: Optional[str]
    cheque_date: Optional[str]
    insured_name: Optional[str]
    bank_name: Optional[str]
    bank_branch_and_city: Optional[str]
    city_id: Optional[int]
    cheque_amount: Optional[int]
    paid_by: Optional[str]
    policy_number: Optional[str]


class ViewPayInSlipResponse(BaseModel):
    pay_in_slip_id: Optional[int]
    pay_in_slip_number: Optional[str]
    insurer_name: Optional[str]
    insurer_logo: Optional[str]
    servicing_office_of_insurer: Optional[str]
    irda_registration_number: Optional[str]
    pay_in_slip_date: Optional[str]
    pay_in_slip_amount: Optional[int]
    pay_in_slip_amount_words: Optional[str]
    dealer_name: Optional[str]
    dealer_code: Optional[str]
    payment_mode: Optional[str]
    dealer_city_district: Optional[str]
    house_bank_name: Optional[str]
    cheque_data: Optional[List[ViewRowDataResponse]]


class MultipleViewPayInSlipResponse(BaseModel):
    data: List[ViewPayInSlipResponse]


class GeneratePayInSlipRequest(BaseModel):
    cheque_ids: List[int]
    insurer_code: str
    transaction_type_id: int


class GeneratePayInSlipResponse(BaseModel):
    pay_in_slip_id: int


class UpdateChequeRequest(BaseModel):
    cheque_id: int
    cheque_number: Optional[str]
    cheque_date: Optional[str]
    account_number: Optional[str]
    bank_id: Optional[int]
    bank_branch_and_city: Optional[str]


class UpdateChequeResponse(BaseModel):
    cheque_id: int
    cheque_number: str
    cheque_date: str
    account_number: str
    bank: str
    bank_branch_and_city: str


class ChequeIDRequest(BaseModel):
    cheque_id: int
    billing_id: Optional[int] = None


class GetPayInSlipQueryParam(BaseModel):
    insurer_code: Optional[str]
    dealer_code: Optional[str]
    transaction_type_id: Optional[int]
    pay_in_slip_number: Optional[str]
    policy_number: Optional[str]
    cheque_number: Optional[str]
    cheque_date_from: Optional[str]
    cheque_date_to: Optional[str]
    pay_in_slip_date_from: Optional[str]
    pay_in_slip_date_to: Optional[str]


class PDFURLResponse(BaseModel):
    pdf_url: str


class LockUnlockDealerResponse(BaseModel):
    message: str
    issue_type: str = None
    payments: list = None
    status_code: int
