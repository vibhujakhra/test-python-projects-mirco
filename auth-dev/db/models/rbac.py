import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Column, VARCHAR, Integer, String, ForeignKey,\
     Boolean, JSON, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud

from db.models.base import BaseDB

from db.session import Base


class Role(Base, BaseDB):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('role.id'), index=True)
    parent = relationship(lambda: Role, remote_side=id, backref='sub_roles')
    misp_user_sub_type = Column(Integer,
                                nullable=True)  # creating this column to fetch role id because signup api gives us user_sub_type as 1, 2 or 3


class User(SQLAlchemyBaseUserTableUUID, SQLBaseCrud, Base, BaseDB):
    salutation = Column(VARCHAR)
    first_name = Column(VARCHAR, nullable=False)
    middle_name = Column(VARCHAR)
    last_name = Column(VARCHAR)
    mobile_no = Column(VARCHAR, nullable=False)
    landline_no = Column(VARCHAR)
    email = Column(VARCHAR, nullable=False)
    role_id = Column(Integer, ForeignKey(Role.id), index=True)
    address = Column(VARCHAR)
    city = Column(VARCHAR)
    state = Column(VARCHAR)
    pincode = Column(VARCHAR)
    designation = Column(VARCHAR)
    employee_code = Column(VARCHAR)
    admin_role_id = Column(Integer, ForeignKey('admin_role.id'), index=True)
    admin_role = relationship("AdminRole", foreign_keys=[admin_role_id])
    region = Column(VARCHAR)

    user_meta_data = relationship("UserMetaData", back_populates="user")


    @property
    def full_name(self):
        name = self.first_name
        if self.middle_name:
            name += " " + self.middle_name
        if self.last_name:
            name += " " + self.last_name
        return name


class UserMetaData(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "user_meta_data"
    id = Column(Integer, primary_key=True)
    user_id = Column(GUID, ForeignKey(User.id), index=True)
    user = relationship("User", back_populates="user_meta_data")
    ams_code = Column(VARCHAR)
    oem_code = Column(VARCHAR)
    broker_code = Column(VARCHAR)
    dealer_code = Column(VARCHAR)
    workshop_code = Column(VARCHAR)
    insurer_code = Column(VARCHAR)
    misp_code = Column(VARCHAR)
    designated_person_code = Column(VARCHAR)


class MispUserMapping(Base, BaseDB):
    __tablename__ = "misp_user_mapping"
    id = Column(Integer, primary_key=True)
    dealer_code = Column(VARCHAR)
    misp_code = Column(VARCHAR)
    misp_user_id = Column(GUID, ForeignKey(User.id), index=True)


class Modules(Base, BaseDB, SQLBaseCrud):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    module_code = Column(VARCHAR, nullable=False)
    group_name = Column(VARCHAR)
    group_url = Column(VARCHAR)
    module_url = Column(VARCHAR)
    group_code = Column(VARCHAR)
    module_full_name = Column(VARCHAR)
    is_active = Column(Boolean, default=True)


class Permission(Base, BaseDB):
    __tablename__ = "permission"
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), index=True)
    module_id = Column(Integer, ForeignKey(Modules.id))
    is_active = Column(Boolean, default=True)


class InsurerDetails(Base, BaseDB):
    __tablename__ = "insurer_details"
    id = Column(Integer, primary_key=True)
    user_id = Column(GUID, ForeignKey(User.id), index=True)
    code = Column(VARCHAR, nullable=False)

    def is_allowed(self, method: str) -> bool:
        # TODO: extend it properly during Phase 2, dealer user management.
        if method == "GET" and not self.can_view:
            return False
        if method == "POST" and not self.can_add:
            return False
        if method in ["PATCH", "PUT"] and not self.can_edit:
            return False
        if method == "DELETE" and not self.can_delete:
            return False
        return True


class DealerDetails(Base, BaseDB):
    __tablename__ = "dealer_details"
    id = Column(Integer, primary_key=True)
    outlet_name = Column(VARCHAR)	
    outlet_code	= Column(VARCHAR)
    primary_address	= Column(VARCHAR)
    outlet_city	= Column(VARCHAR)
    outlet_pincode = Column(VARCHAR)
    misp_code = Column(VARCHAR)


class Reportee(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "reportee"
    id = Column(Integer, primary_key = True)
    user_id =  Column(GUID, ForeignKey(User.id), index=True, unique=True)
    manager_id = Column(GUID, ForeignKey(User.id), index=True)
    is_active = Column(Boolean)


class Group(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(VARCHAR, nullable=False)
    is_active = Column(Boolean, default=True)


class AdminRole(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "admin_role"
    id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey(Group.id), index=True)
    creator_editor = Column(GUID, ForeignKey(User.id), index=True)
    has_create_update_access = Column(Boolean, default=False)
    group = relationship("Group")
    is_active = Column(Boolean, default=True)
    role_permissions = relationship("RoleModulePermission", back_populates="admin_role")



class RoleModulePermission(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "role_module_permission"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey(Modules.id), index=True)
    module = relationship("Modules")
    admin_role_id = Column(Integer, ForeignKey(AdminRole.id), index=True)
    admin_role = relationship("AdminRole", back_populates="role_permissions")
    is_active = Column(Boolean, default=True)


class ChangeLogMixin:
    id = Column(Integer, primary_key=True)
    old_data = Column(JSON)
    new_data = Column(JSON)
    created_at = Column(DateTime)

    @declared_attr
    def creator_editor(cls):
        return Column(GUID, ForeignKey('user.id'), index=True)

class RoleChangeLog(Base, SQLBaseCrud, BaseDB, ChangeLogMixin):
    __tablename__ = "role_change_log"
    role_id = Column(Integer, ForeignKey("admin_role.id"), index=True)


class UserChangeLog(Base, SQLBaseCrud, BaseDB, ChangeLogMixin):
    __tablename__ = "user_change_log"
    user_id = Column(GUID, ForeignKey('user.id'), index=True)


class RelationManagerUserMapping(Base, SQLBaseCrud, BaseDB):
    __tablename__ = "relation_manager_user_mapping"
    id = Column(Integer, primary_key=True)
    relationship_manager_id = Column(GUID, ForeignKey('user.id'), index=True)
    user_id = Column(GUID, ForeignKey('user.id'), index=True, unique=True)
