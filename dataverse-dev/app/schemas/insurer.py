from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class OemInsurer(BaseModel):
    id: int
    name: str


class DealerPersonResponse(BaseModel):
    id: str
    dealer_person_name: Optional[str]
    code: str
    is_active: bool


class DesignatedPersonResponse(BaseModel):
    id: str
    designated_person_name: Optional[str]
    code: str
    is_active: bool


class SalesManagerResponse(BaseModel):
    id: str
    sales_manager_name: str
    code: str
    is_active: bool


class ICLocalOfficeResponse(BaseModel):
    id: str
    local_office_code: str


class BrokerResponse(BaseModel):
    id: int
    name: str
    cin: str
    validity: date
    irda_license_no: str
    address: str
    category: str
    mobile: str
    email: str


class InsurerResponse(BaseModel):
    id: int
    name: str
    code: str
    cin: Optional[str]
    uin: Optional[str]
    city_id: Optional[int]
    state_id: Optional[int]
    irda_registration_no: Optional[str]
    servicing_office_address: Optional[str]
    registered_office_address: Optional[str]
    hsn_sac: Optional[str]
    pan_number: Optional[str]
    gstin_number: Optional[str]
    insurer_logo: Optional[str]
    description_of_service: Optional[str]
    place_of_supply: Optional[str]
    invoice_number: Optional[str]
    authorized_signatory: Optional[str]
    limitations_as_to_us: Optional[str]
    drivers_clause: Optional[str]
    grievance_clause: Optional[str]
    disclaimer: Optional[str]
    important_notice: Optional[str]
    puc_clause: Optional[str]
    note: Optional[str]
    fastag_clause: Optional[str]
    digital_signature: Optional[str]
    limits_of_liability_clause: Optional[str]
    compulsory_deductible: Optional[int]
    cpa_sum_insured_for_liability_clause: Optional[int]
    is_active: Optional[bool]
    is_quotation_integrated: Optional[bool]
    is_proposal_integrated: Optional[bool]
    is_policy_integrated: Optional[bool]
    is_renewal_integrated: Optional[bool]
    is_payment_integrated: Optional[bool]
    is_inspection_required: Optional[bool]
    cms_bank_name_id: Optional[int]
    website_address: Optional[str]


class DealerListResponse(BaseModel):
    id: int
    dealer_name: str
    dealer_code: str


class ActiveInsurerResponse(BaseModel):
    code: str
    insurer_logo: str
    is_renewal_integrated: Optional[bool]


class DealerICMappingListResponse(BaseModel):
    dealer_code: str
    allowed_insurer_list: List[ActiveInsurerResponse]
