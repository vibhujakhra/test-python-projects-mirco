import enum

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, Integer, VARCHAR, Enum, DateTime, DATE, Boolean


class TimeStamp:
    created_at = Column(DateTime)
    modified_at = Column(DateTime)


class Config:
    orm = True


class USER_TYPE_ENUM(enum.Enum):
    SUPER_USER = 1
    ADMIN = 2
    END_USER = 3


class GENDER_ENUM(enum.Enum):
    FEMALE = 1
    MALE = 2
    OTHER = 3


class Users(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(VARCHAR, unique=True, nullable=False)
    first_name = Column(VARCHAR, nullable=False)
    middle_name = Column(VARCHAR, nullable=True)
    last_name = Column(VARCHAR, nullable=False)
    address_line_1 = Column(VARCHAR, nullable=False)
    address_line_2 = Column(VARCHAR, nullable=True)
    address_line_3 = Column(VARCHAR, nullable=True)
    phone_number = Column(VARCHAR, nullable=True)
    email = Column(VARCHAR, nullable=True)
    date_of_birth = Column(DATE, nullable=False)
    user_type = Column(Enum(USER_TYPE_ENUM))
    gender = Column(Enum(GENDER_ENUM))
    is_active = Column(Boolean, default=True)
