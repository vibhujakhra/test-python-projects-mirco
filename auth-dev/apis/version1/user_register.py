import bcrypt
from typing import Type
import logging

from db.session import async_db_session
from fastapi import APIRouter, Depends, HTTPException, Request, status, Response, Form
from fastapi_users import exceptions, models, schemas
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode
from apis.version1.user_manager import get_user_manager
from sqlalchemy.future import select
from db.models.rbac import MispUserMapping, Role, User, UserMetaData
from schemas.user import RegisteredUser, LoginResponse, UserCreate
from utils.verification import encode_jwt, get_token_expiry
from utils.exceptions import InvalidRoleException
from settings import JWT_TOKEN_TIME


def get_register_router(
    user_schema: Type[schemas.U],
    user_create_schema: UserCreate,
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        name="register:register"
    )
    async def register(
        request: Request,
        user_create: user_create_schema,  # type: ignore
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            misp_sub_type = user_create.user_sub_type
            if misp_sub_type:
                role_query= select(Role.id).where(Role.misp_user_sub_type == misp_sub_type)
                role_session = await async_db_session.execute(role_query)
                misp_role_id = role_session.scalars().first()
                user_create.role_id = misp_role_id
            updated_user_create = RegisteredUser(**user_create.__dict__)
            created_user = await user_manager.create(updated_user_create, safe=True, request=request)
            role_code_dict = {
                "dealer_code":user_create.dealer_code, 
                "ams_code": user_create.ams_id, 
                "insurer_code":user_create.insurer_code, 
                "user_id":created_user.id,
                "workshop_code":user_create.workshop_code,
                "oem_code":user_create.oem_code,
                "misp_code": user_create.misp_code
                }
            await UserMetaData.create(**role_code_dict)
            if role_code_dict['misp_code']:
                misp_details = await async_db_session.execute(select(UserMetaData.user_id).where(UserMetaData.misp_code == role_code_dict['misp_code']))
                user_id=misp_details.scalars().first()
                misp_user_dict = {
                    "misp_code":role_code_dict['misp_code'],
                    "dealer_code":role_code_dict['dealer_code'],
                    "misp_user_id": user_id
                }
                await MispUserMapping.create(**misp_user_dict)
            return user_schema.from_orm(created_user)
        
        except exceptions.UserAlreadyExists:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except exceptions.InvalidPasswordException as e:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )


    @router.post(
        "/verify/user/ams/{}",
        status_code=status.HTTP_202_ACCEPTED,
        name="user:ams_user",
    )
    async def update_user(ams_id: str = None):
        logger = logging.getLogger("api.update_user")
        get_user = select(User).filter(User.ams_id == ams_id)
        try:
            user_obj = await async_db_session.execute(get_user)
            (user_obj,) = user_obj.one()
            user_obj.is_verified = True
            await async_db_session.commit()
            return Response(f"User has been updated for Email {user_obj.email}")
        except Exception as e:
            logger.exception(f"User not exists in our database for {ams_id}")
            await async_db_session.rollback()
            raise HTTPException(    
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="USER_NOT_EXISTS",
            )

    @router.post("/login",
        status_code=status.HTTP_200_OK,
        name="login:login")
    async def login(username: str = Form(), password: str = Form()) -> dict:
        try:
            user_email = select(User).filter(User.email == username)
            user_session = await async_db_session.execute(user_email)
            user = user_session.scalars().first()
            if not user:
                raise exceptions.UserNotExists
            
            user_hashed_password = user.hashed_password
            #encoding user password
            hashed_password = user_hashed_password.encode('utf-8')
            # Taking user entered password 
            user_password = password
            # encoding user password
            user_bytes = user_password.encode('utf-8')
            # checking password
            if not user or not bcrypt.checkpw(user_bytes, hashed_password):
                raise exceptions.UserNotExists

            payload_data = {
                "user_id": str(user.id),
                "exp_time": get_token_expiry(JWT_TOKEN_TIME)
            }
            access_token = encode_jwt(payload_data=payload_data)

            return LoginResponse(access_token=access_token, token_type="bearer")

        except exceptions.UserNotExists:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='LOGIN_BAD_CREDENTIALS',
            )
    return router    
   