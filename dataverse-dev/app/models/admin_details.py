from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, Boolean, VARCHAR, DateTime, DATE

from app.models.location import City, State, RtoZone, Pincode, Region


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class Broker(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "broker"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    cin = Column(VARCHAR)
    validity = Column(DATE)
    irda_license_no = Column(VARCHAR, unique=True)
    address = Column(VARCHAR, nullable=True)
    category = Column(VARCHAR, nullable=True)
    mobile = Column(VARCHAR, nullable=True)
    email = Column(VARCHAR, nullable=True)


class Oem(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "oem"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False)
    is_active = Column(Boolean, default=True)


class Dealer(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "dealer"
    id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(VARCHAR)
    dealer_name = Column(VARCHAR, nullable=False)
    dealer_principle_name = Column(VARCHAR, nullable=False)
    dealer_code = Column(VARCHAR, unique=True)
    address_line_1 = Column(VARCHAR, nullable=False)
    address_line_2 = Column(VARCHAR)
    address_line_3 = Column(VARCHAR)
    email = Column(VARCHAR, nullable=False)
    mobile_no = Column(VARCHAR, nullable=False)
    landline_no = Column(VARCHAR)
    state_id = Column(Integer, ForeignKey(State.id))
    city_id = Column(Integer, ForeignKey(City.id))
    pincode_id = Column(Integer, ForeignKey(Pincode.id))
    region_id = Column(Integer, ForeignKey(Region.id))
    dealer_zone = Column(Integer, ForeignKey(RtoZone.id))
    pan_no = Column(VARCHAR, nullable=False)
    gstin = Column(VARCHAR)
    misp_code = Column(VARCHAR)
    dealer_category = Column(VARCHAR)
    broker_zone = Column(Integer, ForeignKey(RtoZone.id))
    oem_zone = Column(Integer, ForeignKey(RtoZone.id))
    oem_id = Column(Integer, ForeignKey(Oem.id))
    relationship_manager = Column(VARCHAR)
    designated_person = Column(VARCHAR)
    is_active = Column(Boolean, default=True)


class Workshop(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "workshop"
    id = Column(Integer, primary_key=True)
    adviser_name = Column(VARCHAR, nullable=False)
    adviser_mobile_no = Column(VARCHAR, nullable=False)
    adviser_email = Column(VARCHAR, nullable=False)
    address_line_1 = Column(VARCHAR, nullable=False)
    address_line_2 = Column(VARCHAR)
    address_line_3 = Column(VARCHAR)
    code = Column(VARCHAR, nullable=False)
    dealer_id = Column(Integer, ForeignKey(Dealer.id))
    is_active = Column(Boolean, default=True)


class WorkshopBeneficiaryDetails(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "workshop_beneficiary_details"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR)
    pan_no = Column(VARCHAR)
    aadhaar_no = Column(VARCHAR)
    bank_account_no = Column(VARCHAR)
    account_type = Column(VARCHAR)
    ifsc_code = Column(VARCHAR)
    micr_no = Column(VARCHAR)
    bank_name = Column(VARCHAR)
    bank_branch = Column(VARCHAR)
    bank_address = Column(VARCHAR)


class DesignatedPerson(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "designated_person"
    id = Column(Integer, primary_key=True)
    designated_person_name = Column(VARCHAR, nullable=False)
    oem_id = Column(Integer, ForeignKey(Oem.id))
    dealer_id = Column(Integer, ForeignKey(Dealer.id))
    code = Column(VARCHAR)
    is_active = Column(Boolean, default=True)


class SalesManager(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "sales_manager"
    id = Column(VARCHAR, primary_key=True)
    sales_manager_name = Column(VARCHAR, nullable=False)
    oem_id = Column(Integer, ForeignKey(Oem.id))
    dealer_id = Column(Integer, ForeignKey(Dealer.id))
    designated_person_id = Column(Integer, ForeignKey(DesignatedPerson.id))
    code = Column(VARCHAR)
    is_active = Column(Boolean, default=True)
