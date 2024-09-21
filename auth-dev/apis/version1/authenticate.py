import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users import exceptions
from sqlalchemy.future import select

from apis.version1.reset_password import get_reset_password_router
from apis.version1.user_manager import auth_backend, current_active_user, fastapi_users
from apis.version1.user_register import get_register_router
from db.models.rbac import User, Role, InsurerDetails
from db.session import async_db_session
from schemas.user import UserCreate, UserRead
from settings import JWT_ALGORITHM
from utils.exceptions import InvalidRoleException
from utils.verification import decode_jwt
from db.models.rbac import UserMetaData, Group, AdminRole


router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


# Commenting the users route as we don't need it at the moment.
# router.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )

@router.get("/authenticate/")
async def authenticate(request: Request, response: Response, user: User = Depends(current_active_user)):
    logger = logging.getLogger("api.authenticated_route")
    try:
        path = request.url.path
        method = request.method
        client_host = request.client.host
        if user.admin_role_id:
            admin_role = await AdminRole.get_by_id(user.admin_role_id)
            role = await Group.get_by_id(admin_role.group_id)
        else:
            role = await Role.get_by_id(user.role_id)
        if not role:
            logger.exception(f"Role not specified by user {role}")
            raise InvalidRoleException(name='authenticate', message="ROLE_NOT_EXIST")

        return_dict = {
            "path": path,
            "user": user.email,
            "method": method,
            "role": role.name,
            "user_id": user.id,
            "client_host": client_host,
            "headers": request.headers
        }
        if role.name == "insurer":
            insurer_code = await async_db_session.execute(
                select(UserMetaData.insurer_code).where(UserMetaData.user_id == user.id)
            )
            insurer_code = insurer_code.scalars().first()
            response.headers["X-INSURER-CODE"] = insurer_code

        response.headers["X-ROLE"] = role.name
        response.headers["X-USER"] = user.email
        response.headers["X-USER-ID"] = str(user.id)

        logger.info(f"Request successfully authenticated. details -> {return_dict}")
        return return_dict

    except Exception as e:
        logger.exception(f"Exception encounter {e} while fetching records.")
        await async_db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED_USER",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/verify-reset-token/", status_code=status.HTTP_202_ACCEPTED, )
async def verify_reset_token(token: str):
    logger = logging.getLogger("api.authenticated_route")

    try:
        reset_token_dict = decode_jwt(token, JWT_ALGORITHM)

        email_query = select(User).filter(User.email == reset_token_dict['email'])
        email_session = await async_db_session.execute(email_query)
        email = email_session.scalars().first()

        reset_token_expiry = reset_token_dict['exp_time']
        if email and (reset_token_expiry > datetime.datetime.now().timestamp()):
            return "Token verified"
        else:
            raise exceptions.InvalidResetPasswordToken

    except exceptions.InvalidResetPasswordToken:
        await async_db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RESET_PASSWORD_BAD_TOKEN",
        )
