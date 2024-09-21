import enum

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import (Column, Integer, VARCHAR, ForeignKey,
                        JSON, Enum, Boolean, DateTime)


class PolicyPDFStatus(enum.Enum):
    REQUEST_RECEIVED = 1
    VALIDATION_ERROR = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    FAILED = 5


class DocType(Base, SQLBaseCrud):
    __tablename__ = "doctype"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)


class Templates(Base, SQLBaseCrud):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    html = Column(VARCHAR, nullable=True)
    insurer_code = Column(VARCHAR, nullable=True)
    doctype_id = Column(Integer, ForeignKey(DocType.id))
    is_active = Column(Boolean, default=True)


class DocumentStatus(Base, SQLBaseCrud):
    __tablename__ = "documentstatus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(VARCHAR, nullable=False)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    current_state = Column(Enum(PolicyPDFStatus), nullable=False)
    policy_uuid = Column(VARCHAR, nullable=True)
    url = Column(VARCHAR, nullable=True)
    extra_data = Column(JSON, nullable=True)
