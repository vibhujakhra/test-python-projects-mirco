from typing import List

from pydantic import BaseModel


class InsurerWisePremiumResponse(BaseModel):
    insurer_code: str
    premium: float


class MultipleInsurerWisePremiumResponse(BaseModel):
    data: List[InsurerWisePremiumResponse]
    total_premium: int


class DailyPolicyTrendResponse(BaseModel):
    policy_type: str
    premium: float


class MultipleDailyPolicyTrendResponse(BaseModel):
    data: List[DailyPolicyTrendResponse]
    total_premium: int


class PlanWisePolicyCountResponse(BaseModel):
    vehicle_cover_type: str
    policy_count: int


class MultiplePlanWisePolicyCountResponse(BaseModel):
    data: List[PlanWisePolicyCountResponse]
    total_policy: int


class PlanWisePremiumResponse(BaseModel):
    vehicle_cover_type: str
    premium: int


class MultiplePlanWisePremiumResponse(BaseModel):
    data: List[PlanWisePremiumResponse]
    total_premium: int
