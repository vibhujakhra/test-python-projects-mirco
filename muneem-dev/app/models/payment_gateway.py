from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import (Column, DateTime, VARCHAR, Boolean, Integer)


class TimeStamp:
    created_at = Column(DateTime)
    modified_at = Column(DateTime)


class Config:
    orm = True


class PaymentGateways(Base, Config, SQLBaseCrud):
    __tablename__ = "payment_gateways"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False)
    logo_url = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=False)
