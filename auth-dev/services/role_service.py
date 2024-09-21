import uuid
import json
from datetime import datetime
from sqlalchemy.future import select
from db.models.rbac import AdminRole, Group, RoleChangeLog, RoleModulePermission
from sqlalchemy.orm import selectinload
from rb_utils.database import sqldb
from schemas.admin_role import RoleListResponse
from utils.exceptions import DatabaseConnectionException


class RoleRepository:

    @classmethod
    async def create_role(cls, role_data):
        """
        The create_role function creates a new role in the database.
            Args:
                cls (class): The class object of the AdminRole model.
                role_data (object): An object containing all of the data needed to create a new admin role.

        :param cls: Pass the class object
        :param role_data: Pass the data to be inserted into the database
        :return: A dictionary
        """
        try:
            group_id = await sqldb.execute(select(Group.id).where(Group.code == role_data.group_type))
            group_id = group_id.first().id
            push_data = {
                "group_id": group_id,
                "role_name": role_data.role_name,
                "is_active": role_data.is_active,
                "creator_editor": uuid.UUID(role_data.creator_editor),
                "has_create_update_access": role_data.has_create_update_access
            }
            role_obj = await AdminRole.create(**push_data)
            module_data = []
            for id in role_data.module_ids:
                module_data.append({
                    "module_id": id,
                    "admin_role_id": role_obj.id,
                    "is_active": True
                })
            await sqldb.execute(RoleModulePermission.__table__.insert().values(module_data))
            return {"msg": f"Role has been successfully created for role type {role_data.role_name}"}
        except Exception as e:
            raise DatabaseConnectionException(f"Exception encounter {str(e)} while creating records.")

    @classmethod
    async def update_role(cls, update_data):

        """
        The update_role function updates the role in the database.
            Args:
                update_data (dict): The data to be updated.

        :param cls: Pass the class object to the function
        :param update_data: Update the role
        :return: A dictionary with a msg key
        """
        try:
            module_id = await sqldb.execute(
                select(RoleModulePermission.module_id).where(RoleModulePermission.admin_role_id == update_data.role_id))
            module_id = module_id.scalars().all()
            old_data = await sqldb.execute(select(AdminRole).where(AdminRole.id == update_data.role_id))
            old_data = old_data.scalars().one()
            old_data_dict = old_data.__dict__.copy()
            created_at = old_data_dict.get("created_at")
            modified_at = old_data_dict.get("modified_at")
            old_creator_editor = old_data_dict.get("creator_editor")
            old_data_dict.update({"created_at": datetime.strftime(created_at, "%Y-%m-%d"), "module_ids": module_id, "creator_editor": str(old_creator_editor), "modified_at": datetime.strftime(modified_at, "%Y-%m-%d")})
            old_dict = old_data_dict.pop("_sa_instance_state")
            role_data = {
                "has_create_update_access": update_data.has_create_update_access,
                "is_active": update_data.is_active
            }
            await AdminRole.update(key=update_data.role_id, **role_data)
            prev_set = set(module_id)
            new_set = set(update_data.module_ids)
            set_intesection = prev_set.intersection(new_set)
            left_set = prev_set.difference(new_set)
            right_set = new_set.difference(prev_set)
            for id in left_set:
                module_id = await sqldb.execute(
                    select(RoleModulePermission.id).where(RoleModulePermission.admin_role_id == update_data.role_id,
                                                          RoleModulePermission.module_id == id))
                module_id = module_id.first().id
                await RoleModulePermission.update(module_id, **{"is_active": False})
            for id in set_intesection:
                module = await sqldb.execute(
                    select(RoleModulePermission).where(RoleModulePermission.admin_role_id == update_data.role_id,
                                                       RoleModulePermission.module_id == id))
                module = module.scalars().first()
                if module.is_active == False:
                    await RoleModulePermission.update(module.id, **{"is_active": True})
            for id in right_set:
                module_data = {
                    "module_id": id,
                    "admin_role_id": update_data.role_id,
                    "is_active": True
                }
                await RoleModulePermission.create(**module_data)
            
            new_data = await sqldb.execute(select(AdminRole).where(AdminRole.id == update_data.role_id))
            new_data = new_data.scalars().first()
            new_data_dict = new_data.__dict__.copy()
            new_created_at = new_data_dict.get("created_at")
            new_creator_editor = new_data_dict.get("creator_editor")
            new_modified_at = new_data_dict.get("modified_at")
            new_data_dict.update({"created_at": datetime.strftime(new_created_at, "%Y-%m-%d"), "module_ids": update_data.module_ids, "creator_editor": str(new_creator_editor), "modified_at": datetime.strftime(new_modified_at, "%Y-%m-%d")})
            new_dict = new_data_dict.pop("_sa_instance_state")
            log_maintainer = {
                "role_id": update_data.role_id,
                "old_data": json.dumps(old_data_dict),
                "new_data": json.dumps(new_data_dict),
                "creator_editor": update_data.creator_editor
            }
            await RoleChangeLog.create(**log_maintainer)
            return {"msg": f"Role has been successfully updated for role type {update_data.role_id}"}
        except Exception as e:
            raise DatabaseConnectionException(f"Exception encounter {str(e)} while updating records.")

    @classmethod
    async def get_existing_role(cls, group_code) -> RoleListResponse:
        """
        The get_existing_role function is used to fetch all the roles that are already created.
            It takes in a group_code as an argument and returns a list of AdminRole objects.
        :param cls: Pass the class object to the function
        :param group_code: Filter the roles by group
        :return: A list of admin role objects
        """
        try:
            allroles = select(AdminRole).options(selectinload(AdminRole.group)).options(selectinload(AdminRole.role_permissions)).order_by(AdminRole.created_at.desc())
            if group_code:
                group_id = await Group.fetch_by_code(code=group_code)
                allroles = allroles.where(AdminRole.group_id == group_id.id)
            allroles = await sqldb.execute(allroles)
            return allroles.scalars().all()
        except Exception as e:
            raise DatabaseConnectionException(f"Exception encounter {str(e)} while fetching records.")