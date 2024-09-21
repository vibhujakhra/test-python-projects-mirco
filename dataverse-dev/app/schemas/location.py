from typing import Optional

from pydantic import BaseModel


class Country(BaseModel):
    id: int
    name: Optional[str]


class StateResponse(BaseModel):
    id: int
    name: str
    gst_code: Optional[str]


class RegionResponse(BaseModel):
    id: int
    name: str


class CityResponse(BaseModel):
    id: int
    name: str


class PincodeResponse(BaseModel):
    id: int
    name: str
    city_id: int
    state_id: int


class RtoZoneResponse(BaseModel):
    id: int
    zone_name: str


class RtoResponse(BaseModel):
    id: int
    name: str
    city_id: int
    code: str
    rto_zone_id: Optional[int]


class RtoZoneSummaryResponse(BaseModel):
    id: int
    zone_name: str


class RTOLocationResponse(BaseModel):
    id: int
    name: str
    code: str
