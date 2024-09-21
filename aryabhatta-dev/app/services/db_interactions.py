import logging
from typing import List

from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select
from sqlalchemy.sql import func

from app.models.pricing import AddOnBundlePrice, AddOnPrice, Discount, ODRate, TPRate, \
    Depreciation, PARate
from app.schema.pricing import AddonResponse, CommunicationResponse, DiscountResponse
from app.settings import SERVICE_CREDENTIALS
from app.utils.exceptions import *


class Pricing:

    @classmethod
    async def get_od_premium_rate(cls, vehicle_data: dict, tenure: int) -> CommunicationResponse:
        """
        :param vehicle_data:
        :param tenure:
        :return: this return the rate in percentage:
        """
        logger = logging.getLogger("app.db.db_calls.get_tp_premium")
        try:
            query = select(ODRate).filter(
                ODRate.od_term == tenure,
                ODRate.rto_zone == vehicle_data["rto_zone"],
                ODRate.vehicle_type == vehicle_data["vehicle_type"],
                ODRate.min_vehicle_age <= vehicle_data["vehicle_age"],
                ODRate.max_vehicle_age > vehicle_data["vehicle_age"],
            )
            if vehicle_data["cubic_capacity"] != 0:
                query = query.filter(
                    ODRate.min_cc < vehicle_data["cubic_capacity"],
                    ODRate.max_cc > vehicle_data["cubic_capacity"])
            if vehicle_data["kilowatt_range"] != 0:
                query = query.filter(
                    ODRate.min_kw < vehicle_data["kilowatt_range"],
                    ODRate.max_kw > vehicle_data["kilowatt_range"])

            result = await sqldb.execute(query)
            result = result.scalars().first()
            response_dict = {"od_premium": result.rate_percent}
            return CommunicationResponse(status=1, response_data=response_dict)
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_data}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_tp_premium(cls, vehicle_data: dict, tenure: int) -> CommunicationResponse:
        """
        :param vehicle_data:
        :param tenure:
        :return: this return the rate in rupees:
        """
        logger = logging.getLogger("app.db.db_calls.get_tp_premium")
        try:
            query = select(TPRate).filter(
                TPRate.tp_term == tenure,
                TPRate.fuel_type == vehicle_data["fuel_type_id"],
                TPRate.vehicle_type == vehicle_data["vehicle_type"],
            )
            if vehicle_data["cubic_capacity"] != 0:
                query = query.filter(
                    TPRate.min_cc < vehicle_data["cubic_capacity"],
                    TPRate.max_cc > vehicle_data["cubic_capacity"])
            if vehicle_data["kilowatt_range"] != 0:
                query = query.filter(
                    TPRate.min_kw < vehicle_data["kilowatt_range"],
                    TPRate.max_kw > vehicle_data["kilowatt_range"])

            result = await sqldb.execute(query)
            result = result.scalars().first()
            response_dict = {"tp_premium": result.rate}
            return CommunicationResponse(status=1, response_data=response_dict)
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_data}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_vehicle_depreciation(cls, vehicle_age) -> CommunicationResponse:
        """
        :param vehicle_age:
        :return: this return the idv rate in percentage:
        """
        logger = logging.getLogger("app.db.db_calls.get_vehicle_depreciation")
        try:
            query = select(Depreciation).filter(
                Depreciation.min_vehicle_age <= vehicle_age,
                Depreciation.max_vehicle_age > vehicle_age,
            )
            result = await sqldb.execute(query)
            result = result.scalars().first()
            response_dict = {"depreciation_rate": result.depreciation_rate}
            return CommunicationResponse(status=1, response_data=response_dict)
        except Exception as e:
            await sqldb.rollback()
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_age}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_od_discount_rate(cls, vehicle_data) -> CommunicationResponse:
        """
        :param vehicle_data:
        :return: this return the discount rate in percentage:
        """
        logger = logging.getLogger("app.db.db_calls.get_tp_premium")
        try:
            query = select(Discount).filter(
                Discount.insurer_code == vehicle_data['insurer_code'],
            )
            result = await sqldb.execute(query)
            result = result.scalars().first()
            response_dict = {"rate_percent": result.discount_precent}
            return CommunicationResponse(status=1, response_data=response_dict)
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_data}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_addon_bundle_premium(cls, vehicle_data: dict) -> List[AddOnBundlePrice]:
        """
        :param vehicle_data:
        :return: this return the discount rates in percentage and rupees:
        """
        logger = logging.getLogger("app.db.db_calls.get_addon_bundle_premium")
        try:
            query = select(AddOnBundlePrice).filter(
                AddOnBundlePrice.variant_id == vehicle_data["variant_id"],
                AddOnBundlePrice.vehicle_type_id == vehicle_data["vehicle_type"],
                AddOnBundlePrice.vehicle_min_age <= vehicle_data["vehicle_age"],
                AddOnBundlePrice.vehicle_max_age > vehicle_data["vehicle_age"],
                AddOnBundlePrice.insurer_code == vehicle_data["insurer_code"]
            )
            if vehicle_data["cubic_capacity"] != 0:
                query = query.filter(
                    AddOnBundlePrice.min_cc < vehicle_data["cubic_capacity"],
                    AddOnBundlePrice.max_cc > vehicle_data["cubic_capacity"])
            result = await sqldb.execute(query)
            result = result.scalars().all()
            return result
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_data}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_addon_premium(cls, vehicle_data: dict, total_idv: float,
                                addon_id_list=None) -> List[AddonResponse]:
        """
        :param vehicle_data:
        :param addon_id_list:
        :param total_idv:
        :return: this return the discount rates in percentage and rupees:
        """
        logger = logging.getLogger("app.db.db_calls.get_addon_premium")
        try:
            query = select(AddOnPrice)
            if addon_id_list:
                query = query.filter(AddOnPrice.addon_id.in_(addon_id_list))

            query = query.filter(
                AddOnPrice.variant_id == vehicle_data["variant_id"],
                AddOnPrice.vehicle_type_id == vehicle_data["vehicle_type"],
                AddOnPrice.vehicle_min_age <= vehicle_data["vehicle_age"],
                AddOnPrice.vehicle_max_age > vehicle_data["vehicle_age"],
                AddOnPrice.insurer_code == vehicle_data["insurer_code"]
            )
            if vehicle_data["cubic_capacity"] != 0:
                query = query.filter(
                    AddOnPrice.min_cc < vehicle_data["cubic_capacity"],
                    AddOnPrice.max_cc > vehicle_data["cubic_capacity"])
            result = await sqldb.execute(query)
            result = result.scalars().all()

            response_data = []
            for addon in result:
                if addon.addon_premium:
                    response_data.append(AddonResponse(id=addon.addon_id, premium=addon.addon_premium))
                else:
                    response_data.append(
                        AddonResponse(id=addon.addon_id, premium=round(total_idv * addon.addon_percent / 100, 2)))
            return response_data
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_data}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_pa_rate(cls, tenure: int, vehicle_type: int, pa_type: str,
                          insurer_code: str) -> CommunicationResponse:
        """
        :param tenure:
        :param vehicle_type:
        :param pa_type:
        :param insurer_code:
        :return: this return the discount rates in percentage and rupees:
        """
        logger = logging.getLogger("app.db.db_calls.get_pa_rate")
        try:
            query = select(PARate).filter(
                PARate.vehicle_type == vehicle_type,
                PARate.cover_code == pa_type,
                PARate.tp_tenure == tenure,
                PARate.insurer_code == insurer_code
            )
            result = await sqldb.execute(query)
            result = result.scalars().first()
            response_dict = {"multiplier": result.per_10k_rate}
            return CommunicationResponse(status=1, response_data=response_dict)
        except Exception as e:
            error_message = f"Exception encounter {e} while fetching records with query {vehicle_type}."
            logger.exception(error_message)
            raise DatabaseConnectionException(logger.name, error_message)

    @classmethod
    async def get_od_discount_range(cls, discount_request) -> DiscountResponse:
        variant_service_url = SERVICE_CREDENTIALS["dataverse"][
                                  "dns"] + f"/api/v1/get_variant_by_id/{discount_request['variant_id']}"
        variant_details = await AsyncHttpClient.get(url=variant_service_url)
        max_value = select(func.max(Discount.discount_precent)).where(
            Discount.variant_id == variant_details["id"],
            Discount.model_id == str(variant_details["model_id"]),
            Discount.fuel_type_id == variant_details["fuel_type_id"])
        max_value = await sqldb.execute(max_value)
        max_value = max_value.scalars().first()
        response_data = {
            "min_discount": 0,
            "max_discount": max_value
        }
        return DiscountResponse(**response_data)
