import enum
from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import (Column, Integer, Boolean, VARCHAR, ForeignKey,
                        Date, Enum, DateTime, JSON, BigInteger)
from sqlalchemy.orm import relationship



class TimeStamp:
    created_at = Column(DateTime)
    modified_at = Column(DateTime)


class Config:
    orm = True


class CHEQUE_TYPE_ENUM(enum.Enum):
    DEALER_CHEQUE = 1
    CUSTOMER_CHEQUE = 2


class PaymentState(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "payment_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)
    code = Column(VARCHAR)


class PaymentStatus(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "payment_status"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)
    code = Column(VARCHAR)
    payment = relationship("Payment", back_populates="payment_status_obj")


class PaymentMode(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "payment_mode"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)
    code = Column(VARCHAR)


class ConsentType(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "consent_type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)
    code = Column(VARCHAR)


class ConsentState(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "consent_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)
    code = Column(VARCHAR)


class Consent(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "consent"
    id = Column(Integer, primary_key=True, autoincrement=True)
    consent_type = Column(Integer, ForeignKey(ConsentType.id))
    consent_state = Column(Integer, ForeignKey(ConsentState.id))
    transaction_id = Column(VARCHAR, nullable=False)


class PayInSlip(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "pay_in_slip"
    id = Column(Integer, primary_key=True, autoincrement=True)
    download_url = Column(VARCHAR)
    slip_number = Column(VARCHAR)
    insurer_code = Column(VARCHAR, nullable=False)
    pay_in_slip_amount = Column(Integer, default=0)
    transaction_type_id = Column(Integer)


class ChequeDetails(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "cheque_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type_id = Column(Integer)
    cheque_number = Column(VARCHAR, nullable=False)
    cheque_date = Column(Date, nullable=False)
    bank_id = Column(Integer, nullable=False)
    bank_branch_and_city = Column(VARCHAR)
    account_number = Column(VARCHAR, nullable=False)
    cheque_type = Column(Enum(CHEQUE_TYPE_ENUM))
    pay_in_slip_id = Column(BigInteger, ForeignKey(PayInSlip.id))
    unique_reference_number = Column(VARCHAR)
    cheque_amount = Column(Integer, default=0)
    insurer_code = Column(VARCHAR)
    payment_status = Column(Integer, ForeignKey(PaymentStatus.id))
    clearance_date = Column(Date)
    dealer_code = Column(VARCHAR)
    dealer_name = Column(VARCHAR)
    city_id = Column(Integer)


class Billing(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, default=0)
    insurer_code = Column(VARCHAR, nullable=False)
    cheque_id = Column(Integer, ForeignKey(ChequeDetails.id))
    billing_status = Column(Integer, ForeignKey(PaymentStatus.id))


class Payment(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type_id = Column(Integer)
    transaction_id = Column(VARCHAR, nullable=False)
    insurer_code = Column(VARCHAR, nullable=False)
    dealer_person = Column(VARCHAR, nullable=True)
    dealer_code = Column(VARCHAR)
    sales_manager = Column(VARCHAR, nullable=True)
    payment_amount = Column(Integer, default=0)
    payment_state = Column(Integer, ForeignKey(PaymentState.id))
    consent_id = Column(Integer, ForeignKey(Consent.id))
    payment_mode = Column(Integer, ForeignKey(PaymentMode.id))
    cheque_id = Column(Integer, ForeignKey(ChequeDetails.id))
    billing_id = Column(BigInteger, ForeignKey(Billing.id))
    policy_number = Column(VARCHAR)
    model = Column(VARCHAR)
    variant = Column(VARCHAR)
    insurer_name = Column(VARCHAR)
    insured_name = Column(VARCHAR)
    policy_start_date = Column(Date)
    policy_issuance_date = Column(Date)
    endorsement_number = Column(VARCHAR)
    policy_end_date = Column(Date)
    vehicle_cover_id = Column(Integer)
    policy_type_id = Column(Integer)
    order_id = Column(VARCHAR)
    payment_status = Column(Integer, ForeignKey(PaymentStatus.id))
    payment_status_obj = relationship("PaymentStatus", back_populates="payment")
    bank_ref_no = Column(VARCHAR)
    transaction_date = Column(DateTime)


class VB64(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "vb64"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vb64_type_id = Column(Integer)
    upload_date = Column(Date)
    uploaded_by = Column(VARCHAR)
    file_location = Column(VARCHAR)
    success_records = Column(Integer)
    failed_records = Column(Integer)
    total_records = Column(Integer)
    vb64_records = relationship("VB64Record", back_populates="vb64")


class VB64Record(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "vb64record"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vb64_id = Column(BigInteger, ForeignKey(VB64.id))
    vb64 = relationship("VB64", back_populates="vb64_records")
    endorsement_number = Column(VARCHAR, nullable=True)
    policy_number = Column(VARCHAR)
    bank_name = Column(VARCHAR)
    cheque_number = Column(VARCHAR)
    upload_status = Column(VARCHAR)
    remarks = Column(VARCHAR)
    clearance_date = Column(Date)
    clearance_status = Column(VARCHAR)
    file_name = Column(VARCHAR)
    vb64_certificate_url = Column(VARCHAR)


class VerificationLink(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "verification_link"
    id = Column(Integer, primary_key=True, autoincrement=True)
    consent_id = Column(Integer, ForeignKey(Consent.id))
    link_ttl_seconds = Column(Integer, nullable=False)


class MandateForm(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "mandate_form"
    id = Column(Integer, primary_key=True, autoincrement=True)
    consent_id = Column(BigInteger, ForeignKey(Consent.id))
    document_url = Column(VARCHAR, nullable=False)


class InsurerCallLog(Base, SQLBaseCrud):
    __tablename__ = "insurer_call_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey(Payment.id))
    raw_request = Column(VARCHAR, nullable=True)
    raw_response = Column(VARCHAR, nullable=True)
    parsed_response = Column(VARCHAR, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class History(Base, SQLBaseCrud):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_name = Column(VARCHAR, nullable=True)
    record_id = Column(VARCHAR, nullable=True)
    changed_values = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class OTP(Base, SQLBaseCrud, TimeStamp):
    __tablename__ = "otp"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(VARCHAR, nullable=False)
    otp = Column(VARCHAR, nullable=False)
    valid_till = Column(DateTime, nullable=False)


class DealerPaymentMapping(Base, Config, SQLBaseCrud, TimeStamp):
    __tablename__ = "dealer_payment_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_mode_id = Column(Integer, ForeignKey(PaymentMode.id))
    dealer_code = Column(VARCHAR, nullable=True)
    is_active = Column(Boolean, default=True)

class VB64Status(Base, SQLBaseCrud):
    __tablename__ = "vb64_status"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    code = Column(VARCHAR)
