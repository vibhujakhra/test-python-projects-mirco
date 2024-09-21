import logging
from typing import List

from rb_utils.async_http_client import AsyncHttpClient

from app.schema.pricing import AddonBundleResponse, AddonResponse
from app.services.db_interactions import Pricing
from app.settings import SERVICE_CREDENTIALS


class AddonPremiumCalculator:
    logger = logging.getLogger("app")

    @classmethod
    async def calculate_addon_bundle_premium(cls, vehicle_data: dict, total_idv: float) -> List[AddonBundleResponse]:
        try:
            response_data = []
            addon_bundles = await Pricing.get_addon_bundle_premium(vehicle_data=vehicle_data)
            for addon_bundle in addon_bundles:
                if not addon_bundle.bundle_premium:
                    dataverse_url = f"{SERVICE_CREDENTIALS['dataverse']['dns']}/api/v1/bundle_addons/?addon_bundle_id={addon_bundle.addon_bundle_id}"
                    addon_bundle_detail = await AsyncHttpClient.get(dataverse_url)
                    bundle_addon_ids = [item.get("id") for item in addon_bundle_detail["bundle_list"][0]["addons_list"]]
                    addon = await Pricing.get_addon_premium(vehicle_data=vehicle_data, total_idv=total_idv,
                                                            addon_id_list=bundle_addon_ids)
                    bundle_premium = sum([round(item.premium, 2) for item in addon])
                    response_data.append(
                        AddonBundleResponse(id=addon_bundle.addon_bundle_id, premium=round(bundle_premium, 2)))
                else:
                    response_data.append(
                        AddonBundleResponse(id=addon_bundle.addon_bundle_id, premium=addon_bundle.bundle_premium))

            return response_data

        except Exception as e:
            error_message = f"Exception encounter {e} while calculating Addon bundle pricing for {vehicle_data}."
            cls.logger.exception(error_message)

    @classmethod
    async def calculate_addon_premium(cls, vehicle_data: dict, total_idv: float) -> List[AddonResponse]:
        try:
            addon = await Pricing.get_addon_premium(vehicle_data=vehicle_data, total_idv=total_idv)
            return addon

        except Exception as e:
            error_message = f"Exception encounter {e} while calculating Addon pricing for {vehicle_data}."
            cls.logger.exception(error_message)
