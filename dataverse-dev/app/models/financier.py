from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, Integer, Boolean, VARCHAR, DateTime


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class Financier(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "financier"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(VARCHAR, index=True)
    code = Column(VARCHAR, unique=False, nullable=True)
    is_active = Column(Boolean, default=True)


class Bank(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "bank"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False, nullable=True)
    is_active = Column(Boolean, default=True)


class AccountType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "account_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=True)
