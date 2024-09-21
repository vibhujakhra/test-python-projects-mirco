from typing import Optional

from pydantic import BaseModel


class OemResponse(BaseModel):
    id: int
    name: str
    code: str


class VehicleModelResponse(BaseModel):
    id: int
    name: str
    oem_code: str
    vehicle_class_id: int
    vehicle_type_id: int


class FuelTypeResponse(BaseModel):
    id: int
    name: str


class VehicleVariantResponse(BaseModel):
    id: int
    name: str
    model_id: int
    cubic_capacity: int
    variant_code: Optional[str]
    kilowatt_range: Optional[float]
    seating_capacity: int
    fuel_type_id: int


class SubVariantResponse(BaseModel):
    id: int
    tone: str
    color: str
    variant_id: int


class ExShowRoomPriceResponse(BaseModel):
    id: int
    sub_variant_id: int
    city: int
    exShowRoomPrice: int


class ModelDetailResponse(BaseModel):
    id: int
    model_id: int
    fuel_type_id: int


class PolicySummaryResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]


class VehicleClassSchema(BaseModel):
    id: int
    name: str
    code: Optional[str]


class VariantSummaryResponse(BaseModel):
    id: int
    name: str
    seating_capacity: Optional[int]
    cubic_capacity: Optional[int]
    kilowatt_range: Optional[int]
    model_id: int
    kilowatt_range: Optional[float]
    variant_code: Optional[str]
    license_carrying_capacity: Optional[int]
    carrying_capacity: Optional[int]
    body_type: Optional[str]
    segment_type: Optional[str]


class VariantByIdResponse(BaseModel):
    id: int
    name: str
    variant_code: Optional[str]
    model_id: int
    is_active: bool
    cubic_capacity: int
    kilowatt_range: Optional[float]
    seating_capacity: int
    fuel_type_id: int
    fuel_type_code: str
    vehicle_type_id: int
    vehicle_class_id: int
    license_carrying_capacity: Optional[int]
    carrying_capacity: Optional[int]
    body_type: Optional[str]
    segment_type: Optional[str]


class PreviousPolicyTypeResponse(BaseModel):
    id: int
    name: str


class ModelResponse(BaseModel):
    id: int
    name: str


class ModelSummaryResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]


class VariantResponse(BaseModel):
    id: int
    name: str


class VehicleTypeResponse(BaseModel):
    id: int
    name: str
    vehicle_class_id: int
    oem_code: str


class VehicleClassResponse(BaseModel):
    id: int
    code: str
    name: str
    oem_code: str


class LocalOfficeResponse(BaseModel):
    servicing_office_address: Optional[str]
