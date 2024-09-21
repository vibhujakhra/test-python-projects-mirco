from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, VARCHAR, DateTime, Boolean

from app.models.policy_details import PolicyType
from app.models.vehicle_details import VehicleType, VehicleClass


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class PaCover(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "pa_cover"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(VARCHAR)
    value = Column(Integer)
    vehicle_type = Column(Integer, ForeignKey(VehicleType.id))
    vehicle_class_id = Column(Integer, ForeignKey(VehicleClass.id))


class VoluntaryDeductible(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "voluntary_deductible"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(VARCHAR)
    value = Column(Integer, nullable=False)
    vehicle_class_id = Column(Integer, ForeignKey(VehicleClass.id))
    vehicle_type_id = Column(Integer, ForeignKey(VehicleType.id))


class ncb(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "no_claim_bonus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    value = Column(Integer)
    new_slab_value = Column(Integer)
    policy_type_id = Column(Integer, ForeignKey(PolicyType.id))
    allowed_previous_policy = Column(Boolean)
    allowed_reserving_letter = Column(Boolean)


class GeoExtension(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "geo_extension"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)


class CPAWavierReason(Base, Config, SQLBaseCrud):
    __tablename__ = "cpa_wavier_reason"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)


class AAIMembership(Base, Config, SQLBaseCrud):
    __tablename__ = "aai_membership"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
