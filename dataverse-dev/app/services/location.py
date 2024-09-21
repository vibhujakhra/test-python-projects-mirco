import logging
from typing import List
from typing import Optional

from rb_utils.database import sqldb
from sqlalchemy import select
from sqlalchemy.future import select

from app.models.location import City, State, Pincode, Rto, RtoZone
from app.utils.exceptions import *


class LocationRepository:

    @classmethod
    async def get_state(cls, country_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(State).where(State.country_id == country_id).order_by("name")
            state = await sqldb.execute(query)
            return state.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_pincode(cls, q: str):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(Pincode).filter(Pincode.name.like('%' + q + '%')).order_by("name")
            pincode = await sqldb.execute(query)
            return pincode.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_city(cls, state_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(City).where(City.state_id == state_id).order_by("name")
            city = await sqldb.execute(query)
            return city.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_rto_zone(cls) -> List[RtoZone]:
        rto_zone = await sqldb.execute(select(RtoZone).order_by("name"))
        return rto_zone.scalars().all()

    @classmethod
    async def get_rto(cls, rto_zone_id: Optional[int], city_id: Optional[int]) -> List[Rto]:
        if rto_zone_id:
            return await RtoZone.fetch(key=rto_zone_id)
        if city_id:
            rto_location = await sqldb.execute(select(Rto).where(Rto.city_id == city_id)).order_by("name")
            return rto_location.scalars().all()

    @classmethod
    async def get_state_and_city(cls, pincode_id: Optional[int]):
        pincode = await sqldb.execute(select(Pincode)).where(Pincode.id == pincode_id).order_by("name")
        return pincode.scalars().all()
