from typing import Optional
from datetime import date
from pydantic import BaseModel


class VB64ReportRequest(BaseModel):
    start_date: str
    end_date: str
    zone_id: Optional[int]
    state_id: Optional[int]
    city_id: Optional[int]
    dealer_code: Optional[str]
    insurer_code: Optional[str]
    transaction_type_id: int
    vb64_status: Optional[str]
    created_date_from: Optional[str]
    created_date_to: Optional[str]

class VB64Reports(BaseModel):
    zone: Optional[str]
    state: Optional[str]
    city: Optional[str]
    dealer: Optional[str]
    insurance_company: Optional[str]
    policy_no: Optional[str]
    start_date: Optional[date]
    issuance_date: Optional[date]
    payment_id: Optional[int]
    cheque_no: Optional[int]
    unique_reference_no: Optional[str]
    cheque_date: Optional[date]
    bank_name: Optional[str]
    bank_city: Optional[str]
    customer_name: Optional[str]
    vb_64_status: Optional[str]
    pending_days_count: Optional[int]
    clearance_date: Optional[date]
    upload_date: Optional[date]
    gross_premium: Optional[str]
    approval_status: Optional[str]
    cancellation_status: Optional[str]
    premium_source: Optional[str]
    policy_payment_status: Optional[str]
    endorsement_no: Optional[str]
    type: Optional[str]
    

class NotDataFoundResponse(BaseModel):
    message: dict

class VB64StatusResponse(BaseModel):
    id: Optional[int]
    name: Optional[str]
    code: Optional[str]