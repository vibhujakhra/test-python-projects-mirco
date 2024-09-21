from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, Boolean, VARCHAR, String, DateTime, Float

from app.models.admin_details import Oem, Dealer
from app.models.location import City, State


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class VehicleClass(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vehicle_class"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=False)
    oem_id = Column(Integer, ForeignKey(Oem.id))
    is_active = Column(Boolean, default=True)


class VehicleType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vehicle_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False, nullable=True)
    vehicle_class_id = Column(Integer, ForeignKey(VehicleClass.id))
    oem_id = Column(Integer, ForeignKey(Oem.id))
    is_active = Column(Boolean, default=True)


class VehicleModel(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vehicle_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    oem_id = Column(Integer, ForeignKey(Oem.id), nullable=True)
    code = Column(String, unique=False, nullable=True)
    vehicle_class_id = Column(Integer, ForeignKey(VehicleClass.id))
    vehicle_type_id = Column(Integer, ForeignKey(VehicleType.id))
    is_active = Column(Boolean, default=True)


class FuelType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "fuel_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False, nullable=True)
    is_active = Column(Boolean, default=True)


class Variant(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "variant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    variant_code = Column(VARCHAR, unique=True, nullable=True)
    model_id = Column(Integer, ForeignKey(VehicleModel.id), nullable=False)
    is_active = Column(Boolean, default=True)
    cubic_capacity = Column(Integer)
    kilowatt_range = Column(Float)
    seating_capacity = Column(Integer)
    fuel_type_id = Column(Integer, ForeignKey(FuelType.id))
    license_carrying_capacity = Column(Integer)
    carrying_capacity = Column(Integer)
    body_type = Column(VARCHAR)
    is_bifuel = Column(Boolean, default=True, nullable=True)
    segment_type = Column(VARCHAR)


class SubVariant(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "sub_variant"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tone = Column(VARCHAR)
    color = Column(VARCHAR)
    variant_id = Column(Integer, ForeignKey(Variant.id))
    is_active = Column(Boolean, default=True)


class ExShowRoomPrice(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "ex_showroom_price"
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(Integer, ForeignKey(City.id))
    state_id = Column(Integer, ForeignKey(State.id))
    variant_id = Column(Integer, ForeignKey(Variant.id))
    sub_variant_id = Column(Integer, ForeignKey(SubVariant.id))
    charges_price = Column(Integer, nullable=True)
    exShowRoomPrice = Column(Integer)


class PreviousPolicyType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "previous_policy_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)


class NcbType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "ncb_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)


class ClaimYear(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "claim_year"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)


class ClaimCount(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "claim_count"
    id = Column(Integer, primary_key=True, autoincrement=True)
    count = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)


class BusinessDetail(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "business_detail"
    id = Column(Integer, primary_key=True)
    dealer_id = Column(Integer, ForeignKey(Dealer.id))
    vehicle_type = Column(Integer, ForeignKey(VehicleType.id)) 
    vehicle_class = Column(Integer, ForeignKey(VehicleClass.id))