from typing import List, Optional

from pydantic import BaseModel, root_validator


class VoluntaryDeductibleResponse(BaseModel):
    id: int
    text: str
    value: int
    vehicle_class_id: Optional[int]
    vehicle_type_id: Optional[int]


class NoClaimBonusResponse(BaseModel):
    id: int
    name: str
    value: int
    policy_type_id: int


class GeoExtensionResponse(BaseModel):
    id: int
    name: str


class PaCoverResponse(BaseModel):
    id: int
    text: str
    value: int
    vehicle_type_id: int
    vehicle_class_id: int


class CPAWavierResponse(BaseModel):
    id: int
    text: str


class AAIMembershipResponse(BaseModel):
    id: int
    name: str


class AccountTypeResponse(BaseModel):
    id: int
    name: str


class UserRoleResponse(BaseModel):
    id: int
    name: str


class DesignationResponse(BaseModel):
    id: int
    name: str


class CPATenureResponse(BaseModel):
    tenure: List[int]


class LastYearNCBResponse(BaseModel):
    id: int
    name: Optional[str]
    value: Optional[str]
    new_slab_value: int

    @root_validator
    def update_name(cls, value):
        value["name"] = f"{value['new_slab_value']}%"
        value['value'] = f"{value['value']}%"
        return value
