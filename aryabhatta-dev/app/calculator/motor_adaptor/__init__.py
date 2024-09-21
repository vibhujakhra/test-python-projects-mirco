import logging
from datetime import datetime
from typing import Union

from pytz import timezone
from rb_utils.async_http_client import AsyncHttpClient

from app.calculator.base import Adaptor
from app.calculator.motor_adaptor.addon_premium_calculator import AddonPremiumCalculator
from app.calculator.motor_adaptor.component_calculation import ComponentCalculator
from app.calculator.motor_adaptor.od_premium_calculator import ODPremiumCalculator
from app.calculator.motor_adaptor.tp_premium_calculator import TPPremiumCalculator
from app.schema.pricing import PriceResponse
from app.settings import SERVICE_CREDENTIALS


class MotorAdaptor(Adaptor):
    component_calculator = ComponentCalculator()
    addon_premium = AddonPremiumCalculator()
    od_premium = ODPremiumCalculator()
    tp_premium = TPPremiumCalculator()

    @classmethod
    async def compute_premium(cls, vehicle_data: dict) -> Union[PriceResponse, None]:
        pricing_data = {
            "quote_request_id": vehicle_data["quote_request_id"],
            "quote_id": vehicle_data["quote_id"],
            "insurer_code": vehicle_data["insurer_code"],
            "insurer_logo": vehicle_data["insurer_logo"],
            "idv": vehicle_data["idv"],
            "total_idv": vehicle_data["idv"]
        }
        logger = logging.getLogger("app")
        net_premium = 0

        vehicle_data = await cls.infuse_model_data(vehicle_data)

        idv_depreciation_rate = await cls.component_calculator.get_idv_depreciation_rate(
            vehicle_age=vehicle_data["vehicle_age"])

        # depreciated_total_idv = vehicle_data["idv"] * idv_depreciation_rate.response_data["depreciation_rate"]
        depreciated_total_idv = vehicle_data["idv"]

        is_breakin, left_days = await cls.checking_isbreakin_case(vehicle_data)

        if vehicle_data["od_tenure"] != 0:
            basic_od_details = await cls.od_premium.calculate_basic_od_premium(
                vehicle_data=vehicle_data, vehicle_idv=vehicle_data["idv"],
                depreciation_rate=idv_depreciation_rate.response_data["depreciation_rate"], is_breakin=is_breakin,
                left_days=left_days)
            if not basic_od_details.status:
                logger.exception(f"Error encounter while calculating OD premium for vehicle data {vehicle_data}")
                return None
            basic_od_details = basic_od_details.basic_od_premium
            net_premium = net_premium + basic_od_details.net_od_premium
            pricing_data["od_premium"] = basic_od_details
            depreciated_total_idv = basic_od_details.total_idv
            pricing_data["total_idv"] = basic_od_details.total_idv

        if vehicle_data["tp_tenure"] != 0:
            basic_tp_details = await cls.tp_premium.calculate_basic_tp_premium(vehicle_data=vehicle_data,
                                                                               is_breakin=is_breakin)
            if not basic_tp_details.status:
                logger.exception(f"Error encounter while calculating TP premium for vehicle data {vehicle_data}")
                return None
            basic_tp_details = basic_tp_details.basic_tp_premium
            net_premium = net_premium + basic_tp_details.net_tp_premium
            pricing_data["tp_premium"] = basic_tp_details

        addonbundle_list = await cls.addon_premium.calculate_addon_bundle_premium(vehicle_data=vehicle_data,
                                                                                  total_idv=depreciated_total_idv)

        addon_list = await cls.addon_premium.calculate_addon_premium(vehicle_data=vehicle_data,
                                                                     total_idv=depreciated_total_idv)

        calculated_tax = cls.component_calculator.calculate_tax(net_premium)

        pricing_data["addon_bundles"] = addonbundle_list
        pricing_data["addons"] = addon_list
        pricing_data["net_premium"] = round(net_premium, 2)
        pricing_data["total_tax"] = calculated_tax
        pricing_data["total_premium"] = round((net_premium + calculated_tax), 2)
        pricing_data["is_breakin"] = is_breakin
        pricing_data["left_days"] = left_days
        logger.info(
            f"Computed pricing for insurer {vehicle_data['insurer_code']} with quote request id {vehicle_data['quote_request_id']} is {pricing_data}.")

        return PriceResponse(**pricing_data)

    @classmethod
    async def infuse_model_data(cls, vehicle_data):

        tenure_service_url = SERVICE_CREDENTIALS["dataverse"][
                                 "dns"] + f"/api/v1/vehicle_cover_by_id/?vehicle_cover_id={vehicle_data['vehicle_cover_id']}"
        tenure_details = await AsyncHttpClient.get(url=tenure_service_url)

        variant_service_url = SERVICE_CREDENTIALS["dataverse"][
                                  "dns"] + f"/api/v1/get_variant_by_id/{vehicle_data['variant_id']}"
        variant_details = await AsyncHttpClient.get(url=variant_service_url)

        sub_variant_service_url = SERVICE_CREDENTIALS["dataverse"][
                                      "dns"] + f"/api/v1/sub_variant/?variant_id={vehicle_data['variant_id']}"
        sub_variant_details = await AsyncHttpClient.get(url=sub_variant_service_url)
        sub_variant_details = sub_variant_details[0]
        sub_variant_id = sub_variant_details["id"]

        exshowroom_price_service_url = SERVICE_CREDENTIALS["dataverse"][
                                           "dns"] + f"/api/v1/exshowroom_price/?subvariant_id={sub_variant_id}"
        exshowroom_price_detail = await AsyncHttpClient.get(url=exshowroom_price_service_url)
        exshowroom_price_detail = exshowroom_price_detail[0]

        rto_location_service_url = SERVICE_CREDENTIALS["dataverse"][
                                       "dns"] + f"/api/v1/policy_summary/?rto_location_id={vehicle_data['rto_id']}"
        rto_zone_details = await AsyncHttpClient.get(url=rto_location_service_url)
        rto_zone_details = rto_zone_details.get("rto_location") or None

        vehicle_data["vehicle_class"] = variant_details["vehicle_class_id"]
        vehicle_data["vehicle_type"] = variant_details["vehicle_type_id"]
        vehicle_data["cubic_capacity"] = variant_details["cubic_capacity"]
        vehicle_data["seating_capacity"] = variant_details["seating_capacity"]
        vehicle_data["ex_showroom_price"] = exshowroom_price_detail["exShowRoomPrice"]
        vehicle_data["kilowatt_range"] = variant_details["kilowatt_range"]
        vehicle_data["rto_zone"] = rto_zone_details["rto_zone_id"] if rto_zone_details else None
        vehicle_data["fuel_type_id"] = variant_details["fuel_type_id"]
        vehicle_data["fuel_type_code"] = variant_details["fuel_type_code"]
        vehicle_data["od_tenure"] = tenure_details["od_tenure"]
        vehicle_data["tp_tenure"] = tenure_details["tp_tenure"]

        return vehicle_data

    @classmethod
    async def checking_isbreakin_case(cls, vehicle_data: dict):
        """
        The checking_isbreakin_case function checks if the policy is a break-in case or not.
            It returns a tuple of two values:
                1) A boolean value indicating whether the policy is a break-in case or not.
                2) An integer value indicating how many days are left for the previous policy to expire.

        :param cls: Pass the class object to the function
        :param vehicle_data: dict: Pass the vehicle data to the function
        :return: A tuple of two values
        """
        if vehicle_data['prev_policy_type'] == 3:
            return True, -100

        if vehicle_data['policy_type_id'] == 2:
            insurer_code = vehicle_data.get('insurer_code')
            vehicle_cover_id = vehicle_data.get('vehicle_cover_id')
            prev_od_policy_exp_date = datetime.strptime(vehicle_data['prev_od_policy_exp_date'], "%d-%m-%Y").date()
            prev_tp_policy_exp_date = datetime.strptime(vehicle_data['prev_tp_policy_exp_date'], "%d-%m-%Y").date()
            current_date = datetime.now(timezone('Asia/Kolkata')).date()

            policy_summary_url = f"{SERVICE_CREDENTIALS['dataverse']['dns']}/api/v1/policy_summary/?insurer_code=" \
                                 f"{insurer_code}&vehicle_cover_id={vehicle_cover_id}"
            policy_summary_response = await AsyncHttpClient.get(url=policy_summary_url)
            vehicle_cover = policy_summary_response['vehicle_cover']

            if vehicle_cover['od_tenure'] and not vehicle_cover['tp_tenure']:
                return prev_od_policy_exp_date < current_date, (prev_od_policy_exp_date - current_date).days

            if not vehicle_cover['od_tenure'] and vehicle_cover['tp_tenure']:
                return prev_tp_policy_exp_date < current_date, (prev_tp_policy_exp_date - current_date).days

            if vehicle_cover['od_tenure'] and vehicle_cover['tp_tenure']:
                return max(prev_od_policy_exp_date, prev_tp_policy_exp_date) < current_date, (
                        max(prev_od_policy_exp_date, prev_tp_policy_exp_date) - current_date).days

        return False, 0
