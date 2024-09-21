from typing import Optional

from pydantic import BaseModel


class PolicyTypeResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]


class PolicySummaryRequest(BaseModel):
    oem_id: Optional[int]
    oem_code: Optional[str]
    salutation_id: Optional[int]
    appointee_relation_id: Optional[int]
    nominee_relation_id: Optional[int]
    vehicle_model_id: Optional[int]
    variant_id: Optional[int]
    proposer_type_id: Optional[int]
    fuel_type_id: Optional[int]
    rto_location_id: Optional[int]
    vehicle_cover_id: Optional[int]
    pincode_id: Optional[int]
    state_id: Optional[int]
    vehicle_type_id: Optional[int]
    ncb_carry_forward_id: Optional[int]
    last_year_ncb_id: Optional[int]
    broker_id: Optional[int]
    insurer_code: Optional[str]
    city_id: Optional[int]
    voluntary_deductible_id: Optional[int]
    cpa_waiver_reason_id: Optional[int]
    geo_extension_id: Optional[int]
    prev_vehicle_cover_id: Optional[int]
    policy_type_id: Optional[int]
    prev_od_insurer_code: Optional[str]
    prev_tp_insurer_code: Optional[str]
    bank_id: Optional[int]
    rto_zone_id: Optional[int]
    user_details: Optional[str]
    sub_variant_id: Optional[int]
    pa_paid_driver_id: Optional[int]
    pa_unnamed_passenger_id: Optional[int]
    vehicle_class_id: Optional[int]
    financier_id: Optional[int]
    agreement_type_id: Optional[int]
    hypothecation_city_id: Optional[int]
    geo_extension_ids: Optional[str]
    dealer_code: Optional[str]
    designated_person_code: Optional[str]
    sales_manager_code: Optional[str]


class ProposerTypeResponse(BaseModel):
    id: int
    name: str


class TransactionTypeResponse(BaseModel):
    id: int
    name: str
    code: str


class AgreementTypeResponse(BaseModel):
    id: int
    name: str


class VB64TypeResponse(BaseModel):
    id: int
    name: str


class VehicleCoverByIdResponse(BaseModel):
    id: int
    name: str
    policy_type_id: Optional[int]
    full_name: Optional[str]
    od_tenure: Optional[int]
    tp_tenure: Optional[int]
    uin: Optional[str]
    insurer_code: Optional[str]
    vehicle_class_id: Optional[int]
    vehicle_type_id: Optional[int]


class VehicleCoverResponse(BaseModel):
    id: int
    name: str
    policy_type_id: Optional[int]
    od_tenure: Optional[int]
    tp_tenure: Optional[int]
    vehicle_class_id: Optional[int]
    vehicle_type_id: Optional[int]


class VehicleCoverRequest(BaseModel):
    policy_type_id: Optional[int]
    vehicle_class_id: Optional[int]
    vehicle_type_id: Optional[int]
    previous_policy_type_id: Optional[int]


class NewVehicleCoverResponse(BaseModel):
    id: int
    name: str


class VehicleCoverIDResponse(BaseModel):
    id: int
    name: str
    policy_type_id: int
    od_tenure: int
    tp_tenure: int


class NcbTypeResponse(BaseModel):
    id: int
    name: str


class ClaimYearResponse(BaseModel):
    id: int
    name: str


class ClaimCountResponse(BaseModel):
    id: int
    count: str


class IMTMappingResponse(BaseModel):
    key_name: str
    imt_code: str


class PaCoverResponse(BaseModel):
    text: str
    value: str
    vehicle_class_id: int
    vehicle_type: int


class DealerResponse(BaseModel):
    group_name: Optional[str]
    dealer_name: Optional[str]
    dealer_principle_name: Optional[str]
    dealer_code: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    address_line_3: Optional[str]
    email: Optional[str]
    mobile_no: Optional[str]
    landline_no: Optional[str]
    state_id: Optional[str]
    city_id: Optional[int]
    pincode_id: Optional[int]
    region_id: Optional[int]
    dealer_zone: Optional[str]
    pan_no: Optional[str]
    gstin: Optional[str]
    misp_code: Optional[str]
    dealer_category: Optional[str]
    broker_zone: Optional[str]
    oem_zone: Optional[str]
    oem_id: Optional[int]
    relationship_manager: Optional[str]
    designated_person: Optional[str]
    is_active: Optional[bool]
