from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import DATE, Column, ForeignKey, Integer, Boolean, VARCHAR, DateTime
from sqlalchemy.orm import relationship


from app.models.location import City, State, Pincode
from app.models.financier import Bank, AccountType
from app.models.vehicle_details import Oem, Dealer


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class UserRole(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "user_role"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    # code = Column(VARCHAR, unique=False, nullable=True)


class Insurer(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "insurer"
    # ic details
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR, unique=False, nullable=False)
    ic_address_1 = Column(VARCHAR, nullable=True)
    ic_address_2 = Column(VARCHAR, nullable=True)
    ic_address_3 = Column(VARCHAR, nullable=True)
    state_id = Column(Integer, ForeignKey(State.id))
    city_id = Column(Integer, ForeignKey(City.id))
    pincode_id = Column(Integer, ForeignKey(Pincode.id))
    landline_no = Column(VARCHAR, nullable=True)
    helpdesk_no = Column(VARCHAR, nullable=True)
    ic_email = Column(VARCHAR, nullable=True)
    website_address = Column(VARCHAR, nullable=True)
    service_tax_code_no = Column(VARCHAR, nullable=True)
    service_tax_registration_no = Column(VARCHAR, nullable=True)
    cin = Column(VARCHAR, unique=True, nullable=True)
    uin = Column(VARCHAR, unique=True, nullable=True)
    servicing_office_address = Column(VARCHAR, nullable=True)
    registered_office_address = Column(VARCHAR, nullable=True)
    hsn_sac = Column(VARCHAR, nullable=True)
    irda_registration_no = Column(VARCHAR, unique=True, nullable=False)
    insurer_logo = Column(VARCHAR, nullable=True)
    pan_number = Column(VARCHAR, nullable=True)
    gstin_number = Column(VARCHAR, nullable=True)
    description_of_service = Column(VARCHAR, nullable=True)
    place_of_supply = Column(VARCHAR, nullable=True)
    invoice_number = Column(VARCHAR, nullable=True)
    # authorized signatory
    digital_signature = Column(VARCHAR, nullable=True)
    authorized_signatory_name = Column(VARCHAR, nullable=True)
    authorized_signatory_designation = Column(VARCHAR, nullable=True)
    limitations_as_to_us = Column(VARCHAR, nullable=True)
    drivers_clause = Column(VARCHAR, nullable=True)
    grievance_clause = Column(VARCHAR, nullable=True)
    disclaimer = Column(VARCHAR, nullable=True)
    important_notice = Column(VARCHAR, nullable=True)
    note = Column(VARCHAR, nullable=True)
    fastag_clause = Column(VARCHAR, nullable=True)
    puc_clause = Column(VARCHAR, nullable=True)
    limits_of_liability_clause = Column(VARCHAR, nullable=True)
    compulsory_deductible = Column(Integer, nullable=True)
    cpa_sum_insured_for_liability_clause = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    # payment collection agency
    agency_name = Column(VARCHAR, nullable=True)
    agency_code = Column(VARCHAR, nullable=True)
    deposit_bank_id = Column(Integer, ForeignKey(Bank.id))
    deposit_account_no = Column(VARCHAR, nullable=True)
    account_type_id = Column(Integer, ForeignKey(AccountType.id))
    payment_collection_address = Column(VARCHAR, nullable=True)
    payment_collection_landline_no = Column(VARCHAR, nullable=True)
    payment_collection_mobile_no = Column(VARCHAR, nullable=True)
    # endorsment  details
    transfer_fee = Column(Integer, nullable=True)
    endorsment_charge = Column(Integer, nullable=True)
    endorsment_status = Column(Boolean, nullable=True)
    # email contacts
    cancellation_email = Column(VARCHAR, nullable=True)
    claim_email = Column(VARCHAR, nullable=True)
    endorsment_email = Column(VARCHAR, nullable=True)
    ncb_carry_forward_email = Column(VARCHAR, nullable=True)
    break_in_case_email = Column(VARCHAR, nullable=True)
    master_email = Column(VARCHAR, nullable=True)
    # user details
    user_obj_id = Column(VARCHAR, nullable=True)
    # cms details
    cms_bank_name_id = Column(Integer, ForeignKey(Bank.id))
    cms_client_code = Column(VARCHAR, nullable=True)
    # breakin case inspection
    is_inspection_required = Column(Boolean, default=False)
    # insurer integration flags
    is_quotation_integrated = Column(Boolean, default=False)
    is_renewal_integrated = Column(Boolean, default=False)
    is_proposal_integrated = Column(Boolean, default=False)
    is_policy_integrated = Column(Boolean, default=False)
    is_payment_integrated = Column(Boolean, default=False)
    is_feedfile_requested = Column(Boolean, default=False)


class InsurerLocalOffice(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "insurer_local_office"
    id = Column(Integer, primary_key=True, autoincrement=True)
    insurer_id = Column(Integer, ForeignKey(Insurer.id))
    local_office_code = Column(VARCHAR, nullable=True)
    gst_in = Column(VARCHAR, nullable=True)
    address_1 = Column(VARCHAR, nullable=True)
    address_2 = Column(VARCHAR, nullable=True)
    address_3 = Column(VARCHAR, nullable=True)
    state_id = Column(Integer, ForeignKey(State.id))
    state = relationship('State')
    city_id = Column(Integer, ForeignKey(City.id))
    city = relationship('City')
    pincode_id = Column(Integer, ForeignKey(Pincode.id))
    pincode = relationship('Pincode')
    email = Column(VARCHAR, nullable=True)
    landline_no = Column(VARCHAR, nullable=True)
    mobile_no = Column(VARCHAR, nullable=True)
    helpdesk_no = Column(VARCHAR, nullable=True)
    is_active = Column(Boolean, default=True)


class ICDealerMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "ic_dealer_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    insurer_id = Column(Integer, ForeignKey(Insurer.id))
    dealer_id = Column(Integer, ForeignKey(Dealer.id))
    local_office_id = Column(Integer, ForeignKey(InsurerLocalOffice.id))
    payment_mode_code_new = Column(Integer, nullable=True)
    payment_mode_code_renew = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_12_days_delayed = Column(Boolean, default=False)  # payment delayed for 12 days after payment tag


class OemInsurer(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "oem_insurer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    insurer_id = Column(Integer, ForeignKey(Insurer.id))
    oem = Column(Integer, ForeignKey(Oem.id))
    is_active = Column(Boolean, default=True)
