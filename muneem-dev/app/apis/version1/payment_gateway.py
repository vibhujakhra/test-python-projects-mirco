import logging
from typing import List

from fastapi import APIRouter

from app.models.payment_gateway import *
from app.schemas.payment_gateway import PGDetailResponse

router = APIRouter()
logger = logging.getLogger("api")


@router.get("/payment_gateway_list/")
async def get_consent_type() -> List[PGDetailResponse]:
    logger.info("Fetching Payment gateway list")
    payment_gateways = await PaymentGateways.fetch_all(is_active=True)
    return [PGDetailResponse(**payment_gateway.__dict__) for payment_gateway in payment_gateways]
