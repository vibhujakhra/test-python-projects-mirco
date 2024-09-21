from app.schema.pricing import CommunicationResponse, IdvRangeResponse
from app.services.db_interactions import Pricing


class ComponentCalculator:

    @classmethod
    def calculate_vehicle_idv(cls, depreciation_rate: int, ex_showroom_price: int) -> IdvRangeResponse:
        mean_idv_value = ex_showroom_price * (100 - depreciation_rate) / 100
        minimum_idv_value = mean_idv_value * (100 - depreciation_rate) / 100
        maximum_idv_value = mean_idv_value * (100 + depreciation_rate) / 100
        vehicle_idv_range = {
            "mean_idv": int(mean_idv_value),
            "min_idv": int(minimum_idv_value),
            "max_idv": int(maximum_idv_value)
        }

        return IdvRangeResponse(**vehicle_idv_range)

    @classmethod
    def calculate_tax(cls, net_premium: int) -> float:
        return net_premium * 0.18

    @classmethod
    async def get_idv_depreciation_rate(cls, vehicle_age: int) -> CommunicationResponse:
        depreciation_percent = await Pricing.get_vehicle_depreciation(vehicle_age)
        return depreciation_percent
