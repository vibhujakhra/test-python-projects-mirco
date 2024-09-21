import logging
from typing import Union

from fastapi import APIRouter

from app.calculator.motor_adaptor import MotorAdaptor
from app.schema.pricing import DiscountRequest, DiscountResponse, PriceRequest, PriceResponse, \
    IdvRangeResponse
from app.utils.code_utils import calculate_vehicle_age
from app.services.db_interactions import Pricing

router = APIRouter()
logger = logging.getLogger("api")


@router.post("/calculate_premium/", response_model=Union[PriceResponse, None])
async def calculate_premium(price_request: PriceRequest):
    """
    this method calculate the price for passed quote request for specific insurer
    and return premium breakup for the same

    :param price_request
    :return: dict: {"quote_request_id": uuid, "quote_id": uuid, "premium_details": premium breakup}
    """
    price_request = price_request.dict()
    logger.info("Pricing request received to compute premium for transaction id: {} - {}"
                "".format(price_request.get("quote_request_id"), price_request))

    vehicle_premium = await MotorAdaptor().compute_premium(vehicle_data=price_request)
    return vehicle_premium


@router.get("/idv_range/", response_model=IdvRangeResponse)
async def get_idv_range(invoice_date: str, exshowroom_price: int):
    idv_depreciation_rate = await MotorAdaptor().component_calculator.get_idv_depreciation_rate(
        vehicle_age=calculate_vehicle_age(invoice_date))
    vehicle_idv_range = MotorAdaptor().component_calculator.calculate_vehicle_idv(
        depreciation_rate=idv_depreciation_rate.response_data["depreciation_rate"],
        ex_showroom_price=exshowroom_price)

    return vehicle_idv_range


@router.post("/discount_range/", response_model=DiscountResponse)
async def get_discount_range(discount_request: DiscountRequest):
    response_data = await Pricing.get_od_discount_range(discount_request=discount_request.__dict__)
    return response_data
