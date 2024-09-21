from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, Boolean, VARCHAR, DateTime

from app.models.insurer import Insurer


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class Bundle(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "bundle"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    insurer_id = Column(Integer, ForeignKey(Insurer.id))
    code = Column(VARCHAR, unique=False, nullable=True)
    is_active = Column(Boolean, default=True)


class Addon(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "addon"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False, nullable=True)
    insurer_code = Column(VARCHAR)
    is_active = Column(Boolean, default=True)
    saod_uin = Column(VARCHAR, unique=True, nullable=True)
    satp_uin = Column(VARCHAR, unique=True, nullable=True)
    bundle_uin = Column(VARCHAR, unique=True, nullable=True)
    comprehensive_uin = Column(VARCHAR, unique=True, nullable=True)


class AddonBundle(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "addon_bundle"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bundle_id = Column(Integer, ForeignKey(Bundle.id))
    addon_id = Column(Integer, ForeignKey(Addon.id))
    is_active = Column(Boolean, default=True)


class IMTMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "imt_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    key_name = Column(VARCHAR, nullable=True)
    imt_code = Column(VARCHAR, unique=True, nullable=False)
    addon_imt_code = Column(VARCHAR, unique=True, nullable=False)
