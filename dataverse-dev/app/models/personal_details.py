from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, Integer, VARCHAR, DateTime


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class Salutation(Base, Config, SQLBaseCrud):
    __tablename__ = "salutation"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    salutation_type = Column(VARCHAR)


class Designation(Base, Config, SQLBaseCrud):
    __tablename__ = "designation"
    id = Column(Integer, autoincrement=True, primary_key=True)
    # code = Column(VARCHAR, unique=False, nullable=True)
    name = Column(VARCHAR, nullable=False)


class Relation(Base, Config, SQLBaseCrud):
    __tablename__ = "relation"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
