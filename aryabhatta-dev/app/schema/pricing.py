from typing import Optional, List

from pydantic import BaseModel


class PriceRequest(BaseModel):
    bi_fuel_kit_idv: Optional[int]
    cpa_tenure_id: Optional[int]
    cpa_waiver_reason_id: Optional[int]
    dealer_code: str
    discount_percent: Optional[int]
    electrical_accessories_idv: Optional[int]
    fuel_type_id: int
    geo_extension_ids: Optional[List[int]]
    is_cpa: Optional[bool]
    idv: Optional[int]
    insurer_code: str
    insurer_logo: Optional[str]
    is_aai_member: bool
    is_antitheft: bool
    is_handicapped: bool
    is_endorsement: Optional[bool]
    legal_liability_paid_driver: bool
    legal_liability_employees_id: Optional[int]
    ncb_carry_forward_id: Optional[int]
    non_electrical_accessories_idv: Optional[int]
    pa_paid_driver_id: Optional[int]
    pa_unnamed_passenger_id: Optional[int]
    policy_end_date: str
    policy_start_date: str
    quote_id: str
    registration_date: Optional[str]
    rto_id: int
    last_year_ncb_id: Optional[int]
    selected_addon_bundles: Optional[List[int]]
    selected_addons: Optional[List[int]]
    total_idv: int
    quote_request_id: str
    variant_id: int
    vehicle_age: int
    vehicle_cover_id: int
    vin_number: Optional[str]
    voluntary_deductible_id: Optional[int]
    prev_policy_type: Optional[int]
    prev_policy_number: Optional[str]
    prev_vehicle_cover_id: Optional[int]
    prev_insurance_company: Optional[int]
    prev_od_policy_exp_date: Optional[str]
    prev_tp_policy_exp_date: Optional[str]
    is_transfer_case: Optional[bool]
    is_claim_case: Optional[bool]
    ncb_type: Optional[int]
    addons_prev_policy_id: Optional[List[int]]
    policy_type_id: Optional[int]


class ODPremium(BaseModel):
    basic_od: float
    bi_fuel_kit_od_price: float
    discounted_od: Optional[float]
    non_electrical_accessories_price: float
    electrical_accessories_price: float
    geo_extension_od_price: float
    voluntary_deductible_price: float
    anti_theft_price: float
    aai_membership_price: float
    handicap_discount: float
    ncb_price: float
    net_od_premium: float
    od_tenure: int
    od_start_date: str
    od_end_date: str
    non_electrical_accessories_idv: float
    electrical_accessories_idv: float
    bi_fuel_kit_idv: float
    voluntary_deductible_id: float
    sub_total_od_premium: float
    sub_total_deduction_premium: float
    od_premium_per_day: float
    od_discount_rate: float
    total_idv: float
    idv: float


class ODPremiumResponse(BaseModel):
    status: int = 0
    error_message: str = ""
    basic_od_premium: Optional[ODPremium]


class TPPremium(BaseModel):
    basic_liability: float
    bi_fuel_kit_tp_price: float
    geo_extension_tp_price: float
    pa_paid_driver_price: float
    pa_unnamed_passenger_price: float
    cpa_price: float
    ll_paid_driver_price: float
    ll_employees_price: float
    net_tp_premium: float
    tp_tenure: int
    tp_start_date: str
    tp_end_date: str
    total_tp_liability: float
    total_pa_cover: float
    total_ll_cover: float
    pa_unnamed_passenger_id: Optional[int]
    pa_paid_driver_id: Optional[int]
    legal_liability_employees_id: Optional[int]
    legal_liability_paid_driver: Optional[int]
    cpa_tenure_id: Optional[int]
    is_cpa: Optional[bool]
    cpa_waiver_reason_id: Optional[int]
    tp_premium_per_day: float


class TPPremiumResponse(BaseModel):
    status: int = 0
    error_message: str = ""
    basic_tp_premium: Optional[TPPremium]


class AddonResponse(BaseModel):
    id: int
    premium: float


class AddonBundleResponse(BaseModel):
    id: int
    premium: float


class PriceResponse(BaseModel):
    quote_request_id: str
    quote_id: str
    insurer_code: str
    insurer_logo: Optional[str]
    total_premium: float
    net_premium: float
    od_premium: Optional[ODPremium]
    tp_premium: Optional[TPPremium]
    total_tax: int
    idv: float
    total_idv: float
    is_breakin: bool
    left_days: int
    addons: Optional[List[AddonResponse]]
    addon_bundles: Optional[List[AddonBundleResponse]]


class IdvRequest(BaseModel):
    invoice_date: str
    exshowroom_price: int


class IdvRangeResponse(BaseModel):
    min_idv: int
    mean_idv: int
    max_idv: int


class DiscountRequest(BaseModel):
    variant_id: int
    vin_no: Optional[str]
    rto_id: int
    dealer_code: str
    is_ncb: bool
    registration_date: str
    policy_start_date: str


class DiscountResponse(BaseModel):
    min_discount: float
    max_discount: float


class CommunicationResponse(BaseModel):
    status: int = 0
    error_message: str = ""
    response_data: dict = {}
