from rb_utils.database import sqldb
from sqlalchemy.future import select

from app.models.location import Pincode


class PersonalDetailRepository:

    @classmethod
    async def get_city_and_state(cls, pincode_id: int):
        city_and_state = await sqldb.execute(select(Pincode.city_id, Pincode.state_id)).where(id=pincode_id).order_by("name")
        return city_and_state.scalars().all()
