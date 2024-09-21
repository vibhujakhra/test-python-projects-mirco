import enum
from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, DateTime, VARCHAR, Enum, Integer, Boolean, ForeignKey


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now)


class Config:
    orm_mode = True


class StatusType(enum.Enum):
    received = 'received'
    processing = 'processing'
    sent = 'sent'
    error = 'error'


class ChannelType(enum.Enum):
    whatsapp = "WhatsApp"
    sms = "SMS"
    email = "Email"


class Templates(Base, Config, SQLBaseCrud):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_slug = Column(VARCHAR, nullable=False)
    email_template = Column(VARCHAR, nullable=True)
    is_dlt_approved = Column(Boolean, default=False)
    dlt_template_id = Column(VARCHAR, nullable=True)
    sms_template = Column(VARCHAR, nullable=True)
    whatsapp_template = Column(VARCHAR, nullable=True)
    is_active = Column(Boolean, default=True)


class CommunicationRequest(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "communication_request"
    id = Column(Integer, primary_key=True, autoincrement=True)
    templates_id = Column(Integer, ForeignKey(Templates.id))
    raw_request = Column(VARCHAR, nullable=True)
    raw_response = Column(VARCHAR, nullable=True)
    status = Column(Enum(StatusType))
    channel = Column(Enum(ChannelType))
    worker_id = Column(VARCHAR)
