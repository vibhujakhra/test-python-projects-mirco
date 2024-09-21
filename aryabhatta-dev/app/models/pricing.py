from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, Integer, Boolean, VARCHAR, TIMESTAMP, Float, DateTime


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class CoverRate(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "cover_rate"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, nullable=False)
    max_amount = Column(Integer, nullable=False, default=0)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    cover_type = Column(VARCHAR, nullable=False)
    cover_percent = Column(Float, nullable=False, default=0.0)


class ODRate(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "od_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fuel_type = Column(Integer, nullable=True)
    vehicle_type = Column(Integer, nullable=True)
    min_vehicle_age = Column(Integer, nullable=True)
    max_vehicle_age = Column(Integer, nullable=True)
    rto_zone = Column(Integer, nullable=True)
    min_cc = Column(Integer, nullable=True)
    max_cc = Column(Integer, nullable=True)
    od_term = Column(Integer, nullable=True)
    rate_percent = Column(Float, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    min_kw = Column(Integer, nullable=True)
    max_kw = Column(Integer, nullable=True)


class TPRate(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "tp_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type = Column(Integer, nullable=True)
    vehicle_category = Column(Integer, nullable=True)
    fuel_type = Column(Integer, nullable=True)
    min_cc = Column(Integer, nullable=True)
    max_cc = Column(Integer, nullable=True)
    tp_term = Column(Integer, nullable=True)
    rate = Column(Float, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    min_kw = Column(Integer, nullable=True)
    max_kw = Column(Integer, nullable=True)


class Depreciation(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "depreciation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    min_vehicle_age = Column(Integer, nullable=True)
    max_vehicle_age = Column(Integer, nullable=True)
    depreciation_rate = Column(Float, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)


class VoluntaryDeductible(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "voluntary_deductible"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type = Column(Integer, nullable=True)
    name = Column(Integer, nullable=True)
    deductible = Column(Integer, nullable=True)
    discount_percent = Column(Integer, nullable=True)
    max_discount = Column(Integer, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)


class PARate(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "pa_rate"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type = Column(Integer, nullable=True)
    cover_code = Column(VARCHAR, nullable=True)
    tp_tenure = Column(Integer, nullable=True)
    per_10k_rate = Column(Float, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)


class NCB(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "ncb"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_type = Column(Integer, nullable=True)
    prev_policy_type = Column(Integer, nullable=True)
    is_claimed_last_year = Column(Boolean, default=False)
    last_year_ncb = Column(Integer, nullable=True)
    claim_count = Column(Integer, nullable=True)
    applicable_ncb = Column(Integer, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)


class Discount(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "discount"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(Integer, nullable=True)
    city_id = Column(Integer, nullable=True)
    city_cluster = Column(Integer, nullable=True)
    rto_code = Column(Integer, nullable=True)
    rto_cluster = Column(Integer, nullable=True)
    business_type = Column(Integer, nullable=True)
    dealer_code = Column(VARCHAR, nullable=True)
    vin_no = Column(VARCHAR, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    fuel_type_id = Column(Integer, nullable=True)
    renewal_type = Column(VARCHAR, nullable=True)
    model_id = Column(VARCHAR, nullable=True)
    variant_id = Column(Integer, nullable=True)
    min_ncb = Column(Integer, nullable=True)
    max_ncb = Column(Integer, nullable=True)
    vehicle_type = Column(Integer, nullable=True)
    vehicle_min_age = Column(Integer, nullable=True)
    vehicle_max_age = Column(Integer, nullable=True)
    min_cc = Column(Integer, nullable=True)
    max_cc = Column(Integer, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    discount_precent = Column(Float, nullable=False)


class AddOnBundlePrice(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "addon_bundle_price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    addon_bundle_id = Column(Integer, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    variant_id = Column(Integer, nullable=True)
    vehicle_type_id = Column(Integer, nullable=True)
    is_ncb = Column(Boolean, default=False)
    add_on_prev_policy = Column(Boolean, default=False)
    vehicle_min_age = Column(Integer, nullable=True)
    vehicle_max_age = Column(Integer, nullable=True)
    min_cc = Column(Integer, nullable=True)
    max_cc = Column(Integer, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    bundle_premium = Column(Integer, nullable=True)


class AddOnPrice(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "addon_price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    addon_id = Column(Integer, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    variant_id = Column(Integer, nullable=True)
    vehicle_type_id = Column(Integer, nullable=True)
    is_ncb = Column(Boolean, default=False)
    add_on_prev_policy = Column(Boolean, default=False)
    vehicle_min_age = Column(Integer, nullable=True)
    vehicle_max_age = Column(Integer, nullable=True)
    min_cc = Column(Integer, nullable=True)
    max_cc = Column(Integer, nullable=True)
    valid_from = Column(TIMESTAMP, nullable=True)
    valid_till = Column(TIMESTAMP, nullable=True)
    addon_premium = Column(Integer, nullable=True)
    addon_percent = Column(Float, nullable=True)
