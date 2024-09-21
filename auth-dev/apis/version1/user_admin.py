import logging
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import paginate, Page
from fastapi_users import exceptions

from rb_utils.database import sqldb

from sqlalchemy import func, cast, String
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from schemas.admin_role import AdminGroupResponse, AdminRoleResponse, ModuleResponse, \
    ManagerResponse, UserListRequest, UserListResponse
from settings import AUTO_LOGOUT_TIMER
from db.models.rbac import MispUserMapping, RelationManagerUserMapping, Reportee, RoleModulePermission, User, \
    UserMetaData, Permission, \
    Modules, Role, AdminRole, Group
from db.session import async_db_session
from schemas.user import UserModulePermissionResponse, UserRead, ModulePermission, AdminRoleRequest, UserEdit, \
    UserEditResponse, UserRoleListResponse, UserMetaDataResponse
from utils.exceptions import InvalidRoleException, InvalidModuleCodeException

router = APIRouter()


@router.get("/get_role_list/", response_model=List[UserRoleListResponse])
async def get_role_list(role_id: int = None):
    logger = logging.getLogger("api.version.get_role_list")
    if role_id:
        role = await Role.get_by_id(role_id)
        return UserRoleListResponse(**role.__dict__)
    role_list = await Role.get_all()
    return [UserRoleListResponse(**role.__dict__) for role in role_list]


@router.get("/get_user_details/", status_code=status.HTTP_200_OK, response_model=UserModulePermissionResponse)
async def get_user_details(user_id: UUID):
    logger = logging.getLogger("api.version.get_user_details")
    try:
        module_list = []
        user = (await async_db_session.execute(select(User).filter(User.id == user_id))).scalars().first()
        if not user:
            raise exceptions.UserNotExists
        if not user.admin_role_id:
            user_permission = (await async_db_session.execute(
                select(Permission).filter(Permission.role_id == user.role_id,
                                          Permission.is_active.is_(True)))).scalars().all()
        else:
            user_permission = (await async_db_session.execute(
                select(RoleModulePermission).filter(RoleModulePermission.admin_role_id == user.admin_role_id,
                                                    RoleModulePermission.is_active.is_(True)))).scalars().all()

        for module in user_permission:
            modules = await Modules.get_by_id(module.module_id)
            module_list.append(ModulePermission(module_name=modules.name, module_code=modules.module_code,
                                                group_name=modules.group_name, module_url=modules.module_url,
                                                group_url=modules.group_url, group_code=modules.group_code))

        user_metadata = (await async_db_session.execute(
            select(UserMetaData).filter(UserMetaData.user_id == user_id))).scalars().first()
        user_metadata_dict = user_metadata.__dict__
        user_metadata_dict.update(user.__dict__)
        if user_metadata_dict.get('misp_code') and user_metadata_dict.get('dealer_code'):
            misp_user_id = (await async_db_session.execute(select(MispUserMapping.misp_user_id).filter(
                MispUserMapping.misp_code == user_metadata_dict.get('misp_code'),
                MispUserMapping.dealer_code == user_metadata_dict.get('dealer_code')))).scalars().first()
            misp_user_details = (
                await async_db_session.execute(select(User).filter(User.id == misp_user_id))).scalars().first()
            user_metadata_dict.update({"misp_details": misp_user_details.__dict__})
        return UserModulePermissionResponse(user_details=UserRead(**user_metadata_dict), module_permission=module_list,
                                            auto_logout_timer=AUTO_LOGOUT_TIMER)

    except exceptions.UserNotExists:
        await async_db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_NOT_EXIST",
        )


# TODO: add_role api needs to update once user creation on admin portal is complete
@router.post("/add_role/", status_code=status.HTTP_200_OK)
async def add_role(role_request: AdminRoleRequest):
    logger = logging.getLogger("api.version.add_role")
    role_session = await async_db_session.execute(select(Role).filter(Role.id == role_request.role_id))
    role = role_session.scalars().first()
    if not role:
        raise InvalidRoleException(name='user_admin.add_role', message="ROLE_NOT_EXIST")
    for module in role_request.module:
        module_code = module.dict()['module_code']
        module_code_session = await async_db_session.execute(select(Modules).filter(Modules.code == module_code))
        module_obj = module_code_session.scalars().first()
        if not module_obj:
            raise InvalidModuleCodeException(name='user_admin.add_role', message="MODULE_CODE_NOT_EXIST")
    return Permission.create(**role_request)


@router.patch("/edit_user_detail/", status_code=status.HTTP_200_OK, response_model=UserEditResponse)
async def edit_user_details(user_detail_request: UserEdit, user_id: UUID):
    logger = logging.getLogger("api.version.edit_user_detail")
    try:
        user_details = user_detail_request.dict()
        user_session = await async_db_session.execute(select(User).filter(User.id == user_id))
        user = user_session.scalars().first()
        if not user:
            raise exceptions.UserNotExists
        role_session = await async_db_session.execute(select(Role).filter(Role.id == user_detail_request.role_id))
        role = role_session.scalars().first()
        if not role:
            raise InvalidRoleException(name='user_admin.edit_user_detail', message="ROLE_NOT_EXIST")
        user = await User.update(user_id, **user_details)
        return UserEditResponse(user_id=user_id, message="Data is updated successfully.")

    except exceptions.UserNotExists:
        await async_db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USER_NOT_EXIST",
        )


@router.get("/get_user_codes/", status_code=status.HTTP_200_OK)
async def get_user_codes(dealer_code: str = None, insurer_code=None):
    logger = logging.getLogger("api.version.get_user_codes")
    if dealer_code or insurer_code:
        if dealer_code:
            session = await async_db_session.execute(
                select(UserMetaData).filter(UserMetaData.dealer_code == dealer_code))
        if insurer_code:
            session = await async_db_session.execute(
                select(UserMetaData).filter(UserMetaData.insurer_code == insurer_code))
        user_code = session.scalars().first()
        return UserMetaDataResponse(**user_code.__dict__)
    else:
        user_meta_data = await UserMetaData.get_all()
        return [UserMetaDataResponse(**user_code.__dict__) for user_code in user_meta_data]


@router.get("/get_group_list/", response_model=List[AdminGroupResponse])
async def get_role_list(group_id: int = None):
    """
    The get_role_list function returns a list of all the roles in the database.
    If a group_id is provided, it will return only that role.

    :param group_id: int: Specify the group_id of the group you want to get
    :return: A list of all groups
    """
    if group_id:
        group = await Group.fetch(key=group_id)
        return [AdminGroupResponse(**group.__dict__)]
    group_list = await Group.fetch_all(is_active=True)
    return [AdminGroupResponse(**group.__dict__) for group in group_list]


@router.get("/get_module_list/", response_model=List[ModuleResponse])
async def get_module_list(module_id: int = None):
    """
    The get_module_list function returns a list of all modules in the database.
    If a module_id is provided, it will return only that module.

    :param module_id: int: Specify the id of the module to be returned
    :return: A list of module response objects
    """
    response = []
    if module_id:
        module = await Modules.fetch(key=module_id)
        return [ModuleResponse(name=module.module_full_name, **module.__dict__)]
    sorted_modules = sorted(await Modules.fetch_all(is_active=True), key=lambda x: x.module_full_name)
    for module_name in sorted_modules:
        modules = module_name.__dict__
        modules['name'] = module_name.module_full_name
        response.append(ModuleResponse(**modules))

    return response


@router.get("/get_role_name/", response_model=List[AdminRoleResponse])
async def get_role_name(group_id: int):
    """
    The get_role_name function returns a list of AdminRoleResponse objects, which contain the role_id and role_name
    of each admin role in the database. The function takes one parameter:
        - group_id: an integer representing admin group id

    :param group_id: int: Find the role_name in the database
    :return: A list of admin role response objects
    """
    admin_role_names = await sqldb.execute(select(AdminRole).where(AdminRole.group_id == group_id))
    return [AdminRoleResponse(**role_name.__dict__) for role_name in admin_role_names.scalars().all()]


@router.get("/get_user_list/", response_model=Page[UserListResponse])
async def get_user_list(user_request: UserListRequest = Depends()):
    """
    The get_user_list function returns a list of users.
    The user_request parameter is an object that contains the following fields:
    email - A string containing the email address of a user. If this field is present, only users with this email address will be returned in the response.
    first_name - A string containing the first name of a user. If this field is present, only users with this first name will be returned in the response (case insensitive).
    group_type_id - An integer representing an AdminGroupType id. If this field is present

    :param user_request: UserListRequest: Pass the request parameters to the function
    :return: A list of users
    """
    logger = logging.getLogger("api.get_user_list")
    try:
        user_query = select(User)
        if user_request.email:
            user_query = user_query.where(User.email == user_request.email)
        if user_request.user_name:
            user_query = user_query.where(func.lower(User.first_name) == user_request.user_name.lower())
        user_query = user_query.outerjoin(AdminRole, AdminRole.id == User.admin_role_id)
        if user_request.user_role_id:
            user_query = user_query.where(AdminRole.id == user_request.user_role_id)
        elif user_request.group_code:
            group_type_id = (await Group.fetch_by_code(code=user_request.group_code)).id
            user_query = user_query.where(AdminRole.group_id == group_type_id)
        user_list = (await sqldb.execute(user_query.options(
            selectinload(User.user_meta_data),
            selectinload(User.admin_role).selectinload(AdminRole.group)))).scalars().all()
        if not user_list:
            raise Exception("DATA NOT FOUND FOR THE ENTERED FILTER")

        response = []
        for user in user_list:
            full_name = user.full_name
            user_data = user.__dict__.copy()
            user_data.update({
                "id": str(user.id),
                "user_name": full_name,
                "insurer_local_office": user_data.get("address"),
                "group_id": user.admin_role.group_id if user.admin_role else None,
                "group_code": user.admin_role.group.code if user.admin_role else None,
                "dealer_code": user.user_meta_data[-1].dealer_code if user.user_meta_data else None,
                "workshop_code": user.user_meta_data[-1].workshop_code if user.user_meta_data else None,
                "oem_code": user.user_meta_data[-1].oem_code if user.user_meta_data else None,
                "insurance_company": user.user_meta_data[-1].insurer_code if user.user_meta_data else None,
            })

            reportees = (
                await sqldb.execute(
                    select(cast(Reportee.user_id, String)).where(Reportee.manager_id == user.id)
                )
            ).scalars().all()
            reporting_manager = (await sqldb.execute(select(cast(Reportee.manager_id, String)).where(
                Reportee.user_id == user.id).order_by(Reportee.id.desc()))).scalars().first()
            print("reporting_manager=", reporting_manager)

            relationship_manager = (
                await sqldb.execute(select(cast(RelationManagerUserMapping.relationship_manager_id, String)).where(
                    RelationManagerUserMapping.user_id == user.id).order_by(
                    RelationManagerUserMapping.id.desc()))).scalars().first()
            user_data.update({
                "reportee_ids": reportees,
                "reporting_manager_id": reporting_manager,
                "relationship_manager_id": relationship_manager
            })
            response.append(user_data)

        return paginate([UserListResponse(**user) for user in response])
    except Exception as e:
        logger.exception(f"Exception encounter {e} while fetching all records.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/get_manager_list/", response_model=List[ManagerResponse])
async def get_manager_list(group_type_id: int, group_type_code: str) -> list:
    """
    The get_relationship_manager function returns a list of relationship managers.
    :return: A list of relationship manager response objects
    """
    try:
        user_query = select(User).outerjoin(AdminRole, AdminRole.id == User.admin_role_id)
        external_group = {'dealer', 'workshop', 'oem', 'insurer'}
        if group_type_code in external_group:
            group_type_id = (await Group.fetch_by_code(code='broking_sales')).id
        user_query = await sqldb.execute(user_query.where(AdminRole.group_id == group_type_id))
        return [ManagerResponse(id=str(group_type_user.id), user_name=group_type_user.full_name,
                                email=group_type_user.email) \
                for group_type_user in user_query.scalars().all()]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ENTERED GROUP TYPE CODE IS INVALID"
        )
