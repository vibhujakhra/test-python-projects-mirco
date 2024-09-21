import logging

from rb_utils.database import sqldb
from sqlalchemy import select
from sqlalchemy.future import select

from app.models.admin_details import Oem
from app.models.vehicle_details import ExShowRoomPrice, SubVariant
from app.models.vehicle_details import VehicleModel, Variant
from app.utils.exceptions import *


class VehicleRepository:

    @classmethod
    async def get_oem(cls, oem_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(Oem).where(Oem.id == oem_id).order_by("name")
            oem = await sqldb.execute(query)
            oem_code = oem.scalars().first()

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

        return oem_code

    @classmethod
    async def get_vehicle_model(cls, oem_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(VehicleModel).where(VehicleModel.oem_id == oem_id).order_by("name")
            vehicle_model = await sqldb.execute(query)
            return vehicle_model.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_vehicle_variant(cls, model_id: int, oem_id: int = None):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(Variant).where(Variant.model_id == model_id, Variant.is_active.is_(True)).order_by("name")
            vehicle_variant_session = await sqldb.execute(query)
            vehicle_variant = vehicle_variant_session.scalars().all()

            if not len(vehicle_variant):
                raise Exception

            return vehicle_variant

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_exshowroom_price(cls, subvariant_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(ExShowRoomPrice).where(ExShowRoomPrice.sub_variant_id == subvariant_id)
            exshowroom_price_session = await sqldb.execute(query)
            exshowroom_price = exshowroom_price_session.scalars().all()

            if not len(exshowroom_price):
                raise Exception

            return exshowroom_price
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_details(cls, variant_code: str):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:

            variant = select(Variant).where(Variant.variant_code == variant_code).order_by("name")
            variant_session = await sqldb.execute(variant)
            variant_details = variant_session.scalars().first()
            if not variant_details:
                raise Exception

            return variant_details

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_color_tone(cls, variant_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(SubVariant).where(SubVariant.variant_id == variant_id)
            details = await sqldb.execute(query)
            color_tone = details.scalars().all()
            if not len(color_tone):
                raise Exception

            return color_tone
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_variants_and_sub_variant(cls, model_id: int):
        logger = logging.getLogger("db.models.base")
        try:
            response = []
            model_variant = await sqldb.execute(
                select(Variant).filter(Variant.model_id == model_id, Variant.is_active.is_(True))).order_by("name")
            variant_list = model_variant.scalars().all()
            for variant in variant_list:
                sub_variant = await sqldb.execute(
                    select(SubVariant).filter(SubVariant.variant_id == variant.id, SubVariant.is_active.is_(True))).order_by("name")
                sub_variant_obj = sub_variant.scalars().all()
                response.append(sub_variant_obj)
            return response

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_color_tone_for_variant_table(cls, variant_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(SubVariant).where(SubVariant.variant_id == variant_id).order_by("name")
            details = await sqldb.execute(query)
            color_tone = details.scalars().all()
            return color_tone
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")