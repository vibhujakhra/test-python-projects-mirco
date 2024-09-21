import enum
from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, Boolean, VARCHAR, Enum, DateTime
from app.models.vehicle_details import VehicleClass, VehicleType, PreviousPolicyType


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class ODTPConditions(enum.Enum):
    OD_EXPIRY_EQ_TP_EXPIRY = 1
    OD_EXPIRY_GT_TP_EXPIRY = 2
    OD_EXPIRY_LT_TP_EXPIRY = 3
    OD_EXPIRY_DIFF_TP_EXPIRY_EQ_THREE = 4
    STANDALONE_OD = 5
    STANDALONE_TP = 6
    OD_EXPIRY_DIFF_TP_EXPIRY_EQ_FIVE = 7
    OD_EXPIRY_DIFF_TP_EXPIRY_EQ_ONE = 8
    OD_EXPIRY_DIFF_TP_EXPIRY_GT_ONE = 9 
    OD_EXPIRY_DIFF_TP_EXPIRY_EQ_ZERO = 10
    OD_EXPIRY_DIFF_TP_EXPIRY_LT_ZERO = 11
    OD_EXPIRY_DIFF_TP_EXPIRY_EQ_MINUS_ONE = 12
    OD_EXPIRY_DIFF_TP_EXPIRY_LT_MINUS_ONE = 13

class CurrentDateConditions(enum.Enum):
    CURRENT_DATE_EQ_TP_EXPIRY = 1
    CURRENT_DATE_GT_TP_EXPIRY = 2
    CURRENT_DATE_LT_TP_EXPIRY = 3
    CURRENT_DATE_EQ_OD_EXPIRY = 4
    CURRENT_DATE_GT_OD_EXPIRY = 5
    CURRENT_DATE_LT_OD_EXPIRY = 6
    CURRENT_DATE_LT_OD_EXPIRY_AND_TP_EXPIRY = 7
    CURRENT_DATE_LT_TP_EXPIRY_AND_GT_OD_EXPIRY = 8

class PolicyType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "policy_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)


class ProposerType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "proposer_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)


class TransactionType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "transaction_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)


class AgreementType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "agreement_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)


class VehicleCover(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vehicle_cover"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, unique=False)
    code = Column(VARCHAR)
    od_tenure = Column(Integer)
    tp_tenure = Column(Integer)
    is_active = Column(Boolean, default=True)

class PolicyTypeVehicleCoverMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "policy_type_vehicle_cover_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type_id = Column(Integer, ForeignKey(VehicleType.id))
    vehicle_class_id = Column(Integer, ForeignKey(VehicleClass.id))
    policy_type_id = Column(Integer, ForeignKey(PolicyType.id))
    prev_policy_type_id = Column(Integer, ForeignKey(PreviousPolicyType.id))
    vehicle_cover_id = Column(Integer, ForeignKey(VehicleCover.id))
    is_active = Column(Boolean, default=True)

# Use case of this table is for conditional mapping on policy type Renew.
class NewVehicleCoverMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = 'new_vehicle_cover'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_od_expired = Column(Boolean, default=True)
    is_tp_expired = Column(Boolean, default=True)
    od_tp_condition = Column(Enum(ODTPConditions), nullable=False)
    current_date_conditions = Column(Enum(CurrentDateConditions), nullable=True)
    policy_type_vehicle_cover_mapping_id = Column(Integer, ForeignKey(PolicyTypeVehicleCoverMapping.id))
    old_vehicle_cover_id = Column(Integer, ForeignKey(PolicyTypeVehicleCoverMapping.id))
    is_active = Column(Boolean, default=True)


class VB64Type(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vb64_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)


class VehicleCoverageVehicleType(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "vehicle_coverage_vehicle_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_cover_id = Column(Integer, ForeignKey(VehicleCover.id))
    vehicle_type_id = Column(Integer, ForeignKey(VehicleType.id))
    is_active = Column(Boolean, default=True)


class InsurerVehicleCoverMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "insurer_vehicle_cover_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(VARCHAR, nullable=True)
    insurer_code = Column(VARCHAR)
    uin = Column(VARCHAR, unique=True, nullable=True)
    policy_type_vehicle_cover_id = Column(Integer, ForeignKey(PolicyTypeVehicleCoverMapping.id))
    is_active = Column(Boolean, default=True)


