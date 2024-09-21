from typing import List, Optional

from pydantic import BaseModel


class AddonResponse(BaseModel):
    id: int
    name: str


class BundleResponse(BaseModel):
    insurer_id: int
    bundle_list: List[int]


class AddonBundleResponse(BaseModel):
    bundle_name: Optional[str]
    addon_list: Optional[List[dict]]


class OemAddonResponse(BaseModel):
    id: int
    oem: int
    addon: int


class AddonUinResponse(BaseModel):
    id: int
    name: str
    insurer_code: str
    is_active: bool
    saod_uin: Optional[str]
    satp_uin: Optional[str]
    bundle_uin: Optional[str]
    comprehensive_uin: Optional[str]
