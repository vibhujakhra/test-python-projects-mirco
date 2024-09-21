import logging
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy import update, select

from db.session import async_db_session
from utils.exceptions import *


class BaseDB:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)

    @classmethod
    async def create(cls, **kwargs):
        logger = logging.getLogger("db.models.base.create")
        try:
            async_db_session.add(cls(**kwargs))
            await async_db_session.commit()
        except Exception as e:
            logger.exception(f"Not able to create record, exception encounter {e}.")
            raise InsertRecordException(logger.name, f"Not able to create record, exception encounter {e}.")

    @classmethod
    async def update(cls, _id, **kwargs):
        logger = logging.getLogger("db.models.base.update")
        try:
            query = (
                update(cls)
                .where(cls.id == _id)
                .values(**kwargs)
                .execution_options(synchronize_session="fetch")
            )
            await async_db_session.execute(query)
            await async_db_session.commit()
        except Exception as e:
            logger.exception(f"Not able to update recorde with id {_id}, exception encounter {e}.")
            raise UpdateRecordException(logger.name, f"Not able to update the record, exception encounter {e}.")

    @classmethod
    async def get_all(cls):
        logger = logging.getLogger("db.models.base.get_all")
        try:
            query = select(cls)
            results = await async_db_session.execute(query)
            return results.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_by_id(cls, _id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(cls).where(cls.id == int(_id))
            results = await async_db_session.execute(query)
            (result,) = results.one()
            return result
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def filter_by_user_id(cls, user_id):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(cls).where(cls.user_id == user_id)
            posts = await async_db_session.execute(query)
            return posts.scalars().all()
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")
