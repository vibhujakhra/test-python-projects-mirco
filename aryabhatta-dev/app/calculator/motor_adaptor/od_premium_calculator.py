import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.pricing import CoverRate, VoluntaryDeductible
from app.schema.pricing import ODPremiumResponse, ODPremium
from app.services.db_interactions import Pricing
from app.settings import SERVICE_CREDENTIALS


class ODPremiumCalculator:
    logger = logging.getLogger("app")

    @classmethod
    async def calculate_basic_od_premium(cls, vehicle_data: dict, vehicle_idv: float,
                                         depreciation_rate: float, is_breakin: bool,
                                         left_days: int) -> ODPremiumResponse:
        try:
            tenure = vehicle_data["od_tenure"]
            od_discount_rate = await Pricing.get_od_discount_rate(vehicle_data=vehicle_data)
            if not od_discount_rate.status:
                raise Exception(od_discount_rate.error_message)
            od_discount_rate = od_discount_rate.response_data["rate_percent"]
            if vehicle_data["discount_percent"] and od_discount_rate < vehicle_data["discount_percent"]:
                raise Exception("Discount is out of range for this Request.")

            od_discount_rate = vehicle_data["discount_percent"] or od_discount_rate

            od_discount_rate = 1 - (od_discount_rate / 100)

            basic_od_rate = await Pricing.get_od_premium_rate(vehicle_data=vehicle_data, tenure=tenure)
            if not basic_od_rate.status:
                raise Exception(basic_od_rate.error_message)
            basic_od_rate = basic_od_rate.response_data["od_premium"] / 100  # 1.708

            discounted_od = vehicle_idv * od_discount_rate * basic_od_rate

            non_electrical_accessories = vehicle_data.get("non_electrical_accessories_idv") or 0
            if non_electrical_accessories:
                non_electrical_accessories = non_electrical_accessories * (
                        (100 - depreciation_rate) / 100) * od_discount_rate * basic_od_rate

            electrical_accessories = vehicle_data.get("electrical_accessories_idv") or 0
            if electrical_accessories:
                cover_object = await CoverRate.fetch_by_code(code="electrical_accessories")
                if cover_object.cover_percent and cover_object.max_amount:
                    electrical_accessories = min(
                        electrical_accessories * ((100 - depreciation_rate) / 100) * cover_object.cover_percent / 100,
                        cover_object.max_amount)
                else:
                    electrical_accessories = electrical_accessories * ((100 - depreciation_rate) / 100) * \
                                             cover_object.cover_percent / 100 or cover_object.max_amount

            bi_fuel_kit_premium = vehicle_data.get("bi_fuel_kit_idv") or 0
            if bi_fuel_kit_premium:
                cover_object = await CoverRate.fetch_by_code(code="external_bi_fuel_od")
                if cover_object.cover_percent and cover_object.max_amount:
                    bi_fuel_kit_premium = min(
                        bi_fuel_kit_premium * ((100 - depreciation_rate) / 100) * cover_object.cover_percent / 100,
                        cover_object.max_amount)
                else:
                    bi_fuel_kit_premium = bi_fuel_kit_premium * ((100 - depreciation_rate) / 100) * \
                                          cover_object.cover_percent / 100 or cover_object.max_amount

            geo_extension_amount = vehicle_data.get("geo_extension_ids") or 0
            if geo_extension_amount:
                cover_object = await CoverRate.fetch_by_code(code="od_geo_extension")
                if cover_object.cover_percent and cover_object.max_amount:
                    geo_extension_amount = min(cover_object.cover_percent / 100, cover_object.max_amount)
                else:
                    geo_extension_amount = cover_object.cover_percent / 100 or cover_object.max_amount

            basic_od = vehicle_idv * basic_od_rate
            if "cng" in vehicle_data["fuel_type_code"]:
                cover_object = await CoverRate.fetch_by_code(code="internal_bi_fuel_od")
                if cover_object.cover_percent and cover_object.max_amount:
                    bi_fuel_kit_premium = min((basic_od + non_electrical_accessories + electrical_accessories
                                               ) * cover_object.cover_percent / 100, cover_object.max_amount)
                else:
                    bi_fuel_kit_premium = (basic_od + non_electrical_accessories + electrical_accessories) * \
                                          cover_object.cover_percent / 100 or cover_object.max_amount

            premium_entities = {
                "basic_od": round(discounted_od, 2),
                "non_electrical_accessories_price": round(tenure * non_electrical_accessories, 2),
                "electrical_accessories_price": round(tenure * electrical_accessories, 2),
                "bi_fuel_kit_od_price": round(bi_fuel_kit_premium, 2)
            }

            anti_theft_premium = 0
            if vehicle_data.get("is_antitheft", False):
                cover_object = await CoverRate.fetch_by_code(code="anti_theft")
                if cover_object.cover_percent and cover_object.max_amount:
                    anti_theft_premium = min(sum(premium_entities.values()) * cover_object.cover_percent / 100,
                                             cover_object.max_amount)
                else:
                    anti_theft_premium = sum(
                        premium_entities.values()) * cover_object.cover_percent / 100 or cover_object.max_amount

            aai_membership_premium = 0
            if vehicle_data.get("is_aai_member", False):
                cover_object = await CoverRate.fetch_by_code(code="aai_membership")
                if cover_object.cover_percent and cover_object.max_amount:
                    aai_membership_premium = min(sum(premium_entities.values()) * cover_object.cover_percent / 100,
                                                 cover_object.max_amount)
                else:
                    aai_membership_premium = sum(
                        premium_entities.values()) * cover_object.cover_percent / 100 or cover_object.max_amount

            handicap_discount = 0
            if vehicle_data.get("is_handicapped", False):
                cover_object = await CoverRate.fetch_by_code(code="handicapped")
                if cover_object.cover_percent and cover_object.max_amount:
                    handicap_discount = min(sum(premium_entities.values()) * cover_object.cover_percent / 100,
                                            cover_object.max_amount)
                else:
                    handicap_discount = sum(
                        premium_entities.values()) * cover_object.cover_percent / 100 or cover_object.max_amount

            voluntary_deductible_detail = vehicle_data.get("voluntary_deductible_id") or 0
            if voluntary_deductible_detail:
                voluntary_deductible_detail = await cls.get_voluntary_deductible(
                    vehicle_data["vehicle_type"], vehicle_data["voluntary_deductible_id"],
                    sum(premium_entities.values()))

            discount_entities = {
                "anti_theft_price": round(tenure * anti_theft_premium, 2),
                "aai_membership_price": round(tenure * aai_membership_premium, 2),
                "handicap_discount": round(handicap_discount, 2),
                "voluntary_deductible_price": round(voluntary_deductible_detail, 2),
                "ncb_price": 0,
            }

            ncb_deduction = vehicle_data.get("ncb_carry_forward_id", 0) or vehicle_data.get("last_year_ncb_id", 0) or 0
            if ncb_deduction:
                discount_entities["ncb_price"] = await cls.get_ncb_deduction(
                    is_endoresment=vehicle_data.get("is_endorsement", False),
                    ncb_carry_forward_id=vehicle_data.get("ncb_carry_forward_id", 0),
                    last_year_ncb_id=vehicle_data.get("last_year_ncb_id", 0),
                    left_days=left_days, is_claim_case=vehicle_data.get("is_claim_case", False),
                    net_od=sum(premium_entities.values()) - sum(discount_entities.values()) + (
                            tenure * geo_extension_amount))

            response_dict = {
                "od_discount_rate": 100 - round(od_discount_rate * 100, 2),
                "basic_od": round(basic_od, 2),
                "discounted_od": round(discounted_od, 2),
                "geo_extension_od_price": round(tenure * geo_extension_amount, 2),
                "net_od_premium": round(sum(premium_entities.values()) - sum(discount_entities.values()) + (
                        tenure * geo_extension_amount), 2),
                "sub_total_od_premium": round(sum(premium_entities.values()), 2),
                "sub_total_deduction_premium": round(sum(discount_entities.values()), 2),
                "od_tenure": tenure,
                "od_start_date": (date.today() + timedelta(days=1)).strftime("%d-%m-%Y") if is_breakin else date.today().strftime("%d-%m-%Y"),
                "od_end_date": (date.today() + relativedelta(years=tenure)).strftime("%d-%m-%Y") if is_breakin else (date.today() + relativedelta(years=tenure) - timedelta(days=1)).strftime("%d-%m-%Y"),
                "non_electrical_accessories_idv": round((vehicle_data.get("non_electrical_accessories_idv") or 0) * (
                        (100 - depreciation_rate) / 100), 2),
                "electrical_accessories_idv": round((vehicle_data.get("electrical_accessories_idv") or 0) * (
                        (100 - depreciation_rate) / 100), 2),
                "bi_fuel_kit_idv": round(vehicle_data.get("bi_fuel_kit_idv") or 0 * (
                        (100 - depreciation_rate) / 100), 2),
                "voluntary_deductible_id": vehicle_data.get("voluntary_deductible_id") or 0,
                # "idv": round(vehicle_idv * ((100 - depreciation_rate) / 100))
                "idv": round(vehicle_idv, 2)
            }
            response_dict.update(discount_entities)
            response_dict.update(premium_entities)
            response_dict["od_premium_per_day"] = response_dict["net_od_premium"] / (365 * tenure)
            response_dict["total_idv"] = response_dict["idv"] + response_dict["non_electrical_accessories_idv"] + \
                                         response_dict["electrical_accessories_idv"] + response_dict["bi_fuel_kit_idv"]

            return ODPremiumResponse(status=1, basic_od_premium=ODPremium(**response_dict))

        except Exception as e:
            error_message = f"Exception encounter {e} while calculating TP pricing for {vehicle_data}."
            cls.logger.exception(error_message)
            return ODPremiumResponse(error_message=error_message)

    @classmethod
    async def get_ncb_deduction(cls,is_endoresment,  ncb_carry_forward_id, last_year_ncb_id, left_days, net_od, is_claim_case):
        if is_claim_case or left_days < -90:
            return 0
        ncb_value = 0
        if last_year_ncb_id:
                
            service_url = SERVICE_CREDENTIALS["dataverse"][
                              "dns"] + f"/api/v1/policy_summary/?last_year_ncb_id={last_year_ncb_id}"
            ncb_details = await AsyncHttpClient.get(url=service_url)
            ncb_value = int(ncb_details["last_year_ncb"]["value"].replace("%", "")) if is_endoresment else  ncb_details["last_year_ncb"]["new_slab_value"]
        if ncb_carry_forward_id:
            service_url = SERVICE_CREDENTIALS["dataverse"][
                              "dns"] + f"/api/v1/policy_summary/?ncb_carry_forward_id={ncb_carry_forward_id}"
            ncb_details = await AsyncHttpClient.get(url=service_url)
            ncb_value = ncb_details["ncb_carry_forward"]["value"]
        return round(net_od * int(ncb_value) / 100, 2)

    @classmethod
    async def get_voluntary_deductible(cls, vehicle_type, voluntary_deductible_id, premium_entities):
        service_url = SERVICE_CREDENTIALS["dataverse"][
                          "dns"] + f"/api/v1/voluntary_deductible/?id={voluntary_deductible_id}"
        voluntary_deductible_value = await AsyncHttpClient.get(url=service_url)

        query = select(VoluntaryDeductible).filter(
            VoluntaryDeductible.vehicle_type == vehicle_type,
            VoluntaryDeductible.deductible == voluntary_deductible_value[0]["value"]
        )
        voluntary_deductible_details = await sqldb.execute(query)
        voluntary_deductible_details = voluntary_deductible_details.scalars().first()
        return round(min(premium_entities * voluntary_deductible_details.discount_percent / 100,
                         voluntary_deductible_details.max_discount), 2)
