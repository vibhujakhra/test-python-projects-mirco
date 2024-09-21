from typing import Optional

from pydantic import BaseModel


class GeneratePolicyRequest(BaseModel):
    transaction_id: str


class GeneratePolicyResponse(BaseModel):
    status: str
    policy_download_url: str


class GeneratePolicyValidationErrorResponse(BaseModel):
    status: str
    message: list


class PremiumBreakup(BaseModel):
    quote_request_id: str
    quote_id: str
    selected_addon_id: Optional[int]


class PremiumBreakupResponse(BaseModel):
    status: str
    premium_breakup_url: str
