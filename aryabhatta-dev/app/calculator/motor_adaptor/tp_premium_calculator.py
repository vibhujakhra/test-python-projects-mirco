import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from rb_utils.async_http_client import AsyncHttpClient

from app.models.pricing import CoverRate
from app.schema.pricing import TPPremiumResponse, TPPremium
from app.services.db_interactions import Pricing
from app.settings import SERVICE_CREDENTIALS


class TPPremiumCalculator:
    logger = logging.getLogger("app")

    @classmethod
    async def calculate_basic_tp_premium(cls, vehicle_data: dict, is_breakin: bool) -> TPPremiumResponse:
        try:
            tenure = vehicle_data["tp_tenure"]

            basic_liability = await Pricing.get_tp_premium(vehicle_data=vehicle_data, tenure=tenure)
            if not basic_liability.status:
                return TPPremiumResponse(error_message=basic_liability.error_message)
            basic_liability = basic_liability.response_data["tp_premium"]

            bi_fuel_premium = 0
            if vehicle_data.get("bi_fuel_kit_idv"):
                cover_object = await CoverRate.fetch_by_code(code="bi_fuel_tp")
                bi_fuel_premium = max(cover_object.cover_percent / 100, cover_object.max_amount) * tenure

            geo_extension_amount = 0
            if vehicle_data.get("geo_extension_ids"):
                cover_object = await CoverRate.fetch_by_code(code="tp_geo_extension")
                geo_extension_amount = max(cover_object.cover_percent / 100, cover_object.max_amount) * tenure

            pa_paid_driver_cover = vehicle_data.get("pa_paid_driver_id") or 0
            if pa_paid_driver_cover:
                pa_paid_driver_cover = await cls.get_pa_cover_value(
                    tenure=tenure,
                    pa_cover_id=vehicle_data["pa_paid_driver_id"],
                    vehicle_type=vehicle_data["vehicle_type"],
                    pa_cover_type="paid_driver",
                    insurer_code=vehicle_data['insurer_code']
                )

            pa_unnamed_passenger_cover = vehicle_data.get("pa_unnamed_passenger_id") or 0
            if pa_unnamed_passenger_cover:
                pa_unnamed_passenger_cover = await cls.get_pa_cover_value(
                    tenure=tenure,
                    pa_cover_id=vehicle_data["pa_unnamed_passenger_id"],
                    vehicle_type=vehicle_data["vehicle_type"],
                    pa_cover_type="unnamed_passenger",
                    insurer_code=vehicle_data['insurer_code']
                )

            cpa_cover_premium = 0
            if vehicle_data.get("is_cpa", False):
                cpa_cover_premium = await cls.get_pa_cover_value(
                    tenure=vehicle_data["cpa_tenure_id"],
                    pa_cover_id=vehicle_data["cpa_tenure_id"],
                    vehicle_type=vehicle_data["vehicle_type"],
                    pa_cover_type="cpa_cover",
                    insurer_code=vehicle_data['insurer_code']
                )
                cpa_cover_premium = round(cpa_cover_premium)

            ll_paid_driver_premium = vehicle_data.get("legal_liability_paid_driver") or 0
            if ll_paid_driver_premium:
                cover_object = await CoverRate.fetch_by_code(code="ll_paid_driver")
                ll_paid_driver_premium = max(cover_object.cover_percent / 100, cover_object.max_amount) * tenure

            ll_employee_premium = vehicle_data.get("legal_liability_employees_id") or 0
            if ll_employee_premium:
                cover_object = await CoverRate.fetch_by_code(code="ll_employees")
                ll_employee_premium = max(cover_object.cover_percent / 100,
                                          cover_object.max_amount) * tenure * ll_employee_premium

            basic_tp_calculation = dict(
                basic_liability=round(basic_liability, 2), bi_fuel_kit_tp_price=round(bi_fuel_premium, 2),
                geo_extension_tp_price=round(geo_extension_amount, 2),
                pa_paid_driver_price=round(pa_paid_driver_cover, 2),
                pa_unnamed_passenger_price=round(pa_unnamed_passenger_cover, 2), cpa_price=round(cpa_cover_premium, 2),
                ll_paid_driver_price=round(ll_paid_driver_premium, 2), ll_employees_price=round(ll_employee_premium, 2))
            basic_tp_calculation["net_tp_premium"] = round(sum(basic_tp_calculation.values()), 2)
            basic_tp_calculation["tp_tenure"] = tenure
            basic_tp_calculation["tp_start_date"] = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y") if is_breakin else date.today().strftime("%d-%m-%Y")
            basic_tp_calculation["tp_end_date"] = (date.today() + relativedelta(years=tenure)).strftime("%d-%m-%Y") if is_breakin else (
                    date.today() + relativedelta(years=tenure) - timedelta(days=1)).strftime("%d-%m-%Y")
            basic_tp_calculation["total_tp_liability"] = basic_tp_calculation.get("basic_liability",
                                                                                  0) + basic_tp_calculation.get(
                "bi_fuel_kit_tp_price", 0) + basic_tp_calculation.get("geo_extension_tp_price", 0)
            basic_tp_calculation["total_pa_cover"] = basic_tp_calculation.get("pa_paid_driver_price",
                                                                              0) + basic_tp_calculation.get(
                "pa_unnamed_passenger_price", 0) + basic_tp_calculation.get("cpa_price", 0)
            basic_tp_calculation["total_ll_cover"] = basic_tp_calculation.get("ll_paid_driver_price",
                                                                              0) + basic_tp_calculation.get(
                "ll_employees_price", 0)
            basic_tp_calculation.update({
                "pa_unnamed_passenger_id": vehicle_data.get("pa_unnamed_passenger_id"),
                "pa_paid_driver_id": vehicle_data.get("pa_paid_driver_id"),
                "legal_liability_employees_id": vehicle_data.get("legal_liability_employees_id"),
                "legal_liability_paid_driver": vehicle_data.get("legal_liability_paid_driver"),
                "cpa_tenure_id": vehicle_data.get("cpa_tenure_id"),
                "is_cpa": vehicle_data.get("is_cpa"),
                "cpa_waiver_reason_id": vehicle_data.get("cpa_waiver_reason_id")
            })
            basic_tp_calculation["tp_premium_per_day"] = basic_tp_calculation["net_tp_premium"] / (365 * tenure)

            return TPPremiumResponse(status=1, basic_tp_premium=TPPremium(**basic_tp_calculation))

        except Exception as e:
            error_message = f"Exception encounter {e} while calculating TP pricing for {vehicle_data}."
            cls.logger.exception(error_message)
            return TPPremiumResponse(error_message=error_message)

    @classmethod
    async def get_pa_cover_value(cls, tenure, pa_cover_id, vehicle_type, pa_cover_type, insurer_code):
        pa_cover_value = 150
        if pa_cover_type != "cpa_cover":
            service_url = SERVICE_CREDENTIALS["dataverse"]["dns"] + f"/api/v1/pa_cover/?id={pa_cover_id}"
            pa_cover_value = await AsyncHttpClient.get(url=service_url)
            pa_cover_value = pa_cover_value[0].get("value", 0) / 10000
        pa_cover_multiplier = await Pricing.get_pa_rate(
            tenure=tenure, vehicle_type=vehicle_type, pa_type=pa_cover_type, insurer_code=insurer_code
        )
        if not pa_cover_multiplier.status:
            raise Exception(pa_cover_multiplier.error_message)
        return pa_cover_multiplier.response_data["multiplier"] * pa_cover_value * tenure
