from typing import Optional, List

from pydantic import BaseModel, EmailStr


class AddCityRequest(BaseModel):
    state_id: int
    city_name: str
    is_active: Optional[bool]


class AddResponse(BaseModel):
    msg: str


class AddStateRequest(BaseModel):
    region_id: Optional[int]
    state_name: str
    is_active: Optional[bool]
    gst_code: Optional[str]


class AddPincodeRequest(BaseModel):
    city_id: int
    state_id: Optional[int]
    pincode: str
    is_active: Optional[bool]


class AddModelRequest(BaseModel):
    model_name: str
    is_active: Optional[bool]


class AddVariantRequest(BaseModel):
    model_id: int
    variant_name: str
    fuel_type_id: int
    cubic_capacity: int
    seating_capacity: int
    kilowatt_range: Optional[int]
    is_bifuel: bool
    is_active: bool
    color: str
    tone: str


class ExShowroomPriceRequest(BaseModel):
    variant_id: Optional[int]
    state_id: Optional[int]
    exShowRoomPrice: int
    charges_price: Optional[int]


class RtoRequest(BaseModel):
    city_id: int
    state_id: int
    rto_name: str
    is_active: bool


class RtoZoneRequest(BaseModel):
    zone_name: str
    is_active: bool


class RegionRequest(BaseModel):
    region_name: str
    rto_zone_id: int
    is_active: bool


class CityClusterRequest(BaseModel):
    # state_id: int
    city_id: List[int]
    code: Optional[str]
    name: str
    is_active: bool


class RtoClusterRequest(BaseModel):
    rto_id: List[int]
    code: Optional[str]
    name: str
    is_active: bool


class BankRequest(BaseModel):
    name: str
    code: Optional[str]
    is_active: bool


class FinancierRequest(BaseModel):
    name: str
    code: Optional[str]
    is_active: bool


class UserInfoRequest(BaseModel):
    insurer_code: Optional[str]
    salutation: str
    first_name: str
    middle_name: str = None
    last_name: str
    role_id: int
    designation: str
    landline_no: str
    mobile_no: str
    email: EmailStr
    is_active: bool


class InsurerRequest(BaseModel):
    name: str
    code: Optional[str]
    uin: str
    cin: str
    servicing_office_address: Optional[str]
    insurer_logo: Optional[str]
    is_active: bool
    ic_address_1: str
    ic_address_2: Optional[str]
    ic_address_3: Optional[str]
    state_id: int
    city_id: int
    pincode_id: int
    landline_no: Optional[str]
    helpdesk_no: Optional[str]
    ic_email: str
    website_address: str
    service_tax_code_no: str
    service_tax_registration_no: str
    pan_number: str
    irda_registration_no: str
    authorized_signatory_name: str
    authorized_signatory_designation: str
    digital_signature: str
    grievance_clause: str
    agency_name: str
    agency_code: str
    deposit_bank_id: int
    deposit_account_no: str
    account_type_id: int
    payment_collection_address: str
    payment_collection_landline_no: Optional[str]
    payment_collection_mobile_no: str
    transfer_fee: int
    endorsment_charge: int
    endorsment_status: bool
    cancellation_email: str
    claim_email: str
    endorsment_email: str
    ncb_carry_forward_email: str
    break_in_case_email: str
    master_email: str
    cms_bank_name_id: Optional[int]
    cms_client_code: Optional[str]
    registered_office_address: Optional[str]
    gstin_number: Optional[str]
    limitations_as_to_us: Optional[str]
    drivers_clause: Optional[str]
    disclaimer: Optional[str]
    important_notice: Optional[str]
    note: Optional[str]
    fastag_clause: Optional[str]
    puc_clause: Optional[str]
    limits_of_liability_clause: Optional[str]
    description_of_service: Optional[str]
    invoice_number: Optional[str]


class IcUserInfoRequest(BaseModel):
    ic_request: InsurerRequest
    user_info_request: UserInfoRequest


class InsurerLocalOfficeRequest(BaseModel):
    insurer_id: int
    local_office_code: str
    gst_in: str
    address_1: str
    address_2: Optional[str]
    address_3: Optional[str]
    dealer_state_id: int
    dealer_city_id: int
    pincode_id: int
    email: str
    landline_no: Optional[str]
    mobile_no: Optional[str]
    helpdesk_no: str
    is_active: bool


class ICDealerMappingRequest(BaseModel):
    insurer_id: List[int]
    dealer_name: str
    dealer_code: str
    dealer_state: int
    dealer_city: int
    local_office_state: int
    local_office_code: int
    payment_mode_code_new: int
    payment_mode_code_renew: int
    is_active: bool


class UpdateStateRequest(BaseModel):
    state_name: str
    region_id: Optional[int]
    is_active: Optional[bool]
    gst_code: Optional[str]


class UpdateCityRequest(BaseModel):
    state_id: int
    city_name: str
    is_active: Optional[bool]


class UpdateRtoZoneRequest(BaseModel):
    rto_zone_name: str
    is_active: Optional[bool]


class UpdateRegionRequest(BaseModel):
    region_name: str
    rto_zone_id: int
    is_active: Optional[bool]


class UpdateRtoRequest(BaseModel):
    state_id: int
    city_id: int
    rto_name: str
    is_active: Optional[bool]


class UpdatePincodeRequest(BaseModel):
    state_id: int
    city_id: int
    pincode: str
    is_active: Optional[bool]


class UpdateRtoClusterRequest(BaseModel):
    rto_id: List[int]
    code: Optional[str]
    name: str
    is_active: bool


class UpdateCityClusterRequest(BaseModel):
    city_id: List[int]
    code: Optional[str]
    name: str
    is_active: bool


class UpdateBankRequest(BaseModel):
    bank_name: str
    is_active: Optional[bool]


class UpdateFinancierRequest(BaseModel):
    financier_name: str
    is_active: Optional[bool]


class UpdateInsurerRequest(BaseModel):
    name: str
    is_active: bool
    insurer_logo: Optional[str]
    cin: Optional[str]
    uin: Optional[str]
    servicing_office_address: Optional[str]
    ic_address_1: str
    ic_address_2: Optional[str]
    ic_address_3: Optional[str]
    state_id: int
    city_id: int
    pincode_id: int
    landline_no: Optional[str]
    helpdesk_no: Optional[str]
    ic_email: str
    website_address: str
    service_tax_code_no: str
    service_tax_registration_no: str
    pan_number: str
    irda_registration_no: str
    authorized_signatory_name: str
    authorized_signatory_designation: str
    digital_signature: str
    grievance_clause: str
    agency_name: str
    agency_code: str
    deposit_bank_id: int
    deposit_account_no: str
    account_type_id: int
    payment_collection_address: str
    payment_collection_landline_no: Optional[str]
    payment_collection_mobile_no: str
    transfer_fee: int
    endorsment_charge: int
    endorsment_status: bool
    cancellation_email: str
    claim_email: str
    endorsment_email: str
    ncb_carry_forward_email: str
    break_in_case_email: str
    master_email: str
    cms_bank_name_id: int
    cms_client_code: str
    registered_office_address: Optional[str]
    gstin_number: Optional[str]
    limitations_as_to_us: Optional[str]
    drivers_clause: Optional[str]
    disclaimer: Optional[str]
    important_notice: Optional[str]
    note: Optional[str]
    fastag_clause: Optional[str]
    puc_clause: Optional[str]
    limits_of_liability_clause: Optional[str]
    description_of_service: Optional[str]
    invoice_number: Optional[str]


class UpdateIcUserInfo(BaseModel):
    ic_request: UpdateInsurerRequest
    user_info_request: UserInfoRequest


class UpdateInsurerLocalOffice(BaseModel):
    insurer_id: int
    local_office_code: str
    gst_in: str
    address_1: str
    address_2: Optional[str]
    address_3: Optional[str]
    dealer_state_id: int
    dealer_city_id: int
    pincode_id: int
    email: str
    landline_no: Optional[str]
    mobile_no: Optional[str]
    helpdesk_no: str
    is_active: bool


class UpdateInsurerDealerMapping(BaseModel):
    insurer_id: List[int]
    dealer_name: str
    dealer_code: str
    dealer_state: int
    dealer_city: int
    local_office_state: int
    local_office_code: int
    payment_mode_code_new: int
    payment_mode_code_renew: int
    is_active: bool


class UpdateModelRequest(BaseModel):
    model_name: str
    is_active: Optional[bool]


class UpdateVehicleVariantRequest(BaseModel):
    model_id: int
    name: str
    fuel_type_id: int
    cubic_capacity: int
    kilowatt_range: Optional[int]
    seating_capacity: int
    is_bifuel: bool
    is_active: Optional[bool]
    color: Optional[str]
    tone: Optional[str]


class UpdateVehicleVariantPriceRequest(BaseModel):
    variant_name: str
    state_id: str
    exShowRoomPrice: int
    charges_price: int
    state_name: str


class AssestUploadResponse(BaseModel):
    status_code: int
    document_url: Optional[str]
    error_message: Optional[str]


class ValidationResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str]


class SearchRegionResponse(BaseModel):
    name: str
    rto_zone_name: str
    is_active: Optional[bool]


class SearchICDealerMappingRequest(BaseModel):
    insurer_name: str
    dealer_name: str
    dealer_code: str
    dealer_state: int
    dealer_city: int
    local_office_state: int
    local_office_code: int
    local_office_code_name: str
    payment_mode_code_new: int
    payment_mode_code_renew: int
    is_active: bool


class SearchStateResponse(BaseModel):
    region_name: str
    name: str
    is_active: bool


class SearchCityResponse(BaseModel):
    state_name: str
    name: str
    is_active: Optional[bool]


class SearchPincodeResponse(BaseModel):
    city_name: str
    state_name: str
    name: str
    is_active: bool


class SearchCityClusterRequest(BaseModel):
    city_name: List[int]


class SearchRtoResponse(BaseModel):
    city_name: str
    state_name: str
    name: str
    code: Optional[str]
    is_active: bool


class SearchRtoClusterResponse(BaseModel):
    state_name: str
    city_name: str
    rto_name: str
    name: str
    is_active: bool


class SearchVehicleModelResponse(BaseModel):
    oem_name: str
    name: str
    is_active: bool


class SearchVehicleVariantResponse(BaseModel):
    oem_name: str
    model_name: str
    name: str
    fuel_type_name: str
    cubic_capacity: int
    seating_capacity: int
    color: str
    tone: str
    is_bifuel: bool
    is_active: bool


class SearchVehicleVariantPriceResponse(BaseModel):
    state_name: str
    variant_name: str
    charges_price: Optional[int]
    exShowRoomPrice: int


class SearchInsurerLocalOfficeResponse(BaseModel):
    insurer_name: str
    local_office_code: str
    address_1: str
    dealer_state_name: str
    dealer_city_name: str
    is_active: bool


class SearchBankResponse(BaseModel):
    id: int
    bank_name: str
    is_active: bool


class SearchFinancierResponse(BaseModel):
    id: int
    financier_name: str
    is_active: bool


class StateTableResponse(BaseModel):
    id: Optional[int]
    name: str
    zone: Optional[str]
    gst_code: Optional[str]
    is_active: Optional[bool]
    code: Optional[str]
    region: Optional[int]
    country_id: Optional[int]
    region_name: Optional[str]


class CityTableResponse(BaseModel):
    id: Optional[int]
    name: str
    code: Optional[str]
    state_id: Optional[int]
    state_name: Optional[str]
    is_active: Optional[bool]


class PincodeTableResponse(BaseModel):
    id: Optional[int]
    name: str
    city_id: Optional[int]
    state_id: Optional[int]
    city_name: Optional[str]
    state_name: Optional[str]
    is_active: Optional[bool]


class RtoTableResponse(BaseModel):
    id: Optional[int]
    code: Optional[str]
    name: str
    city_id: Optional[int]
    state_id: Optional[int]
    rto_zone_id: Optional[int]
    city_name: Optional[str]
    state_name: Optional[str]
    is_active: Optional[bool]


class VehicleModelTableResponse(BaseModel):
    id: Optional[int]
    code: Optional[str]
    name: str
    oem_id: Optional[int]
    oem_name: Optional[str]
    is_active: Optional[bool]


class VehicleVariantTableResponse(BaseModel):
    id: int
    name: str
    oem_name: str
    model_name: str
    model_id: Optional[int]
    cubic_capacity: Optional[int]
    seating_capacity: Optional[int]
    license_carrying_capacity: Optional[int]
    body_type: Optional[str]
    fuel_type_id: int
    segment_type: Optional[str]
    carrying_capacity: Optional[int]
    variant_code: Optional[str]
    is_active: Optional[bool]
    is_bifuel: Optional[bool]
    kilowatt_range: Optional[int]
    fuel_name: str
    sub_variant_id: Optional[int]
    color: Optional[str]
    tone: Optional[str]


class VehicleVariantPriceTableResponse(BaseModel):
    ex_showroom_price_id: int
    model_name: str
    variant_name: str
    state_name: Optional[str]
    color: Optional[str]
    tone: Optional[str]
    exShowRoomPrice: Optional[int]
    charges_price: Optional[int]


class RtoZoneTableResponse(BaseModel):
    id: Optional[int]
    zone_name: str
    is_active: Optional[bool]


class RegionTableResponse(BaseModel):
    id: Optional[int]
    name: str
    rto_zone_id: Optional[int]
    rto_zone_name: Optional[str]
    is_active: Optional[bool]


class RtoClusterTableResponse(BaseModel):
    rto_cluster_id: int
    is_active: bool
    rto_cluster_name: str
    cluster_rto: List[dict]


class CityClusterTableResponse(BaseModel):
    city_cluster_id: int
    is_active: bool
    city_cluster_name: str
    cluster_cities: List[dict]


class InsurerTableResponse(BaseModel):
    # TODO REMOVE OPTIONAL FROM SOME FIELDS
    id: int
    name: str
    cin: str
    gstin_number: Optional[str]
    servicing_office_address: Optional[str]
    code: Optional[str]
    insurer_logo: Optional[str]
    uin: Optional[str]
    is_active: bool
    ic_address_1: Optional[str]
    ic_address_2: Optional[str]
    ic_address_3: Optional[str]
    state_id: Optional[int]
    city_id: Optional[int]
    pincode_id: Optional[int]
    landline_no: Optional[str]
    helpdesk_no: Optional[str]
    ic_email: Optional[str]
    website_address: Optional[str]
    service_tax_code_no: Optional[str]
    service_tax_registration_no: Optional[str]
    pan_number: Optional[str]
    irda_registration_no: Optional[str]
    authorized_signatory_name: Optional[str]
    authorized_signatory_designation: Optional[str]
    digital_signature: Optional[str]
    grievance_clause: Optional[str]
    agency_name: Optional[str]
    agency_code: Optional[str]
    deposit_bank_id: Optional[int]
    deposit_account_no: Optional[str]
    account_type_id: Optional[int]
    payment_collection_address: Optional[str]
    payment_collection_landline_no: Optional[str]
    payment_collection_mobile_no: Optional[str]
    transfer_fee: Optional[int]
    endorsment_charge: Optional[int]
    endorsment_status: Optional[bool]
    cancellation_email: Optional[str]
    claim_email: Optional[str]
    endorsment_email: Optional[str]
    ncb_carry_forward_email: Optional[str]
    break_in_case_email: Optional[str]
    master_email: Optional[str]
    limitations_as_to_us: Optional[str]
    drivers_clause: Optional[str]
    disclaimer: Optional[str]
    important_notice: Optional[str]
    note: Optional[str]
    fastag_clause: Optional[str]
    puc_clause: Optional[str]
    limits_of_liability_clause: Optional[str]
    description_of_service: Optional[str]
    invoice_number: Optional[str]
    salutation: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    user_role_id: Optional[int]
    designation: Optional[str]
    user_landline_no: Optional[str]
    user_mobile_no: Optional[str]
    user_email: Optional[str]
    user_status: Optional[bool]
    cms_bank_name_id: Optional[int]
    cms_client_code: Optional[str]


class InsurerLocalOfficeTableResponse(BaseModel):
    # TODO REMOVE OPTIONAL FROM SOME FIELDS
    id: int
    insurer_id: Optional[int]
    local_office_code: Optional[str]
    gst_in: Optional[str]
    address_1: Optional[str]
    address_2: Optional[str]
    address_3: Optional[str]
    dealer_state_id: Optional[int]
    dealer_city_id: Optional[int]
    pincode_id: Optional[int]
    email: Optional[str]
    landline_no: Optional[str]
    mobile_no: Optional[str]
    helpdesk_no: Optional[str]
    is_active: Optional[bool]
    insurer_name: Optional[str]
    dealer_state_name: Optional[str]
    dealer_city_name: Optional[str]


class ICDealerMappingResponse(BaseModel):
    id: int
    insurer_id: int
    dealer_name: str
    dealer_code: str
    dealer_state: int
    dealer_city: int
    local_office_state: int
    local_office_code: int
    payment_mode_code_new: int
    payment_mode_code_renew: int
    is_active: bool
    insurer_name: str
    local_office_code_name: str


class BankResponse(BaseModel):
    id: int
    bank_name: str
    code: Optional[str]
    is_active: bool


class FinancierResponse(BaseModel):
    id: int
    financier_name: str
    code: Optional[str]
    is_active: Optional[bool]


class SubVariantAndVariantResponse(BaseModel):
    id: Optional[int]
    variant_id: int
    variant_name: str
    color: str
    tone: str
    is_active: Optional[bool]


class DealerRequest(BaseModel):
    group_name: Optional[str]
    dealer_name: str
    dealer_code: str
    state_id: int
    city_id: int
    pincode: int
    address_line_1: str
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    email: str
    mobile_no: str
    landline_no: str
    misp_code: str
    broker_zone: int
    relationship_manager: Optional[str]
    oem_zone: int
    is_active: bool


class BusinessDetailRequest(BaseModel):
    vehicle_class: int
    vehicle_type: int


class WorkshopRequest(BaseModel):
    code: str
    adviser_name: str
    adviser_mobile_no: str
    adviser_email: str
    address_line_1: str
    address_line_2: str = None
    address_line_3: str = None


class WorkshopBeneficiaryRequest(BaseModel):
    name: Optional[str]
    pan_no: Optional[str]
    aadhaar_no: Optional[str]
    bank_account_no: Optional[str]
    account_type: Optional[str]
    ifsc_code: Optional[str]
    micr_no: Optional[str]
    bank_name: Optional[str]
    bank_branch: Optional[str]
    bank_address: Optional[str]


class UserInfoRequest(BaseModel):
    email: EmailStr
    salutation: str
    role_id: int
    first_name: str
    middle_name: str = None
    last_name: str
    mobile_no: str
    landline_no: str = None
    designation: str


class DealerUserInfoRequest(UserInfoRequest):
    pass


class WorkshopUserInfoRequest(UserInfoRequest):
    pass


class WorkshopBeneficiaryAndUserRequest(BaseModel):
    workshop: WorkshopRequest
    workshop_beneficiary: WorkshopBeneficiaryRequest
    workshop_user_info: WorkshopUserInfoRequest


class AdminDealerRequest(BaseModel):
    dealer: DealerRequest
    business_detail: BusinessDetailRequest
    dealer_user_info: DealerUserInfoRequest
    workshops: List[WorkshopBeneficiaryAndUserRequest]


class DealerTableResponse(BaseModel):
    dealer_name: str
    dealer_code: str
    workshop_code: List[str]
    state_name: str
    city_name: str
    is_active: bool


class UserInfoResponse(BaseModel):
    user_id: str
    message: str


class DealerResponse(BaseModel):
    dealer_code: str
    message: str    