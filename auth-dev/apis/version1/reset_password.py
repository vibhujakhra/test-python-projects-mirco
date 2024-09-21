from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode
from pydantic import EmailStr
from sqlalchemy import update
from sdk.producer import AsyncKafkaProducer
from starlette.background import BackgroundTasks

from apis.version1.token_expiry import check_token_expiry
from apis.version1.user_manager import get_user_manager
from db.models.rbac import User
from db.session import async_db_session
from settings import JWT_ALGORITHM, VERIFICATION_EMAIL_SUBJECT, RESET_DOMAIN_ADDRESS, RESET_PASSWORD_JWT_TOKEN_TIME
from utils.verification import decode_jwt, encode_jwt, get_hashed_password, get_token_expiry


def get_reset_password_router() -> APIRouter:
    """Generate a router with the reset password routes."""
    router = APIRouter()

    @router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
    )
    async def forgot_password(background_tasks: BackgroundTasks, email: EmailStr = Body(..., embed=True),
                               user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):
        try:
            user = await user_manager.get_by_email(email)
            payload_data = {
                "email": email,
                "exp_time": get_token_expiry(RESET_PASSWORD_JWT_TOKEN_TIME)
            }
            token = encode_jwt(payload_data=payload_data)
            email_request = {
                "template_format_kwargs": {
                    "reset_password_link": f'{RESET_DOMAIN_ADDRESS}/reset-password?'f'token={token}',
                    "user_name": user.full_name
                },
                "template_slug":"reset_password",
                "subject": VERIFICATION_EMAIL_SUBJECT,
                "email": [email]
            }
            background_tasks.add_task(AsyncKafkaProducer.push_email_to_kafka_topic, data=email_request)

        except exceptions.UserNotExists:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="USER_NOT_EXISTS",
            )
        return f"Email sent successfully. f'{RESET_DOMAIN_ADDRESS}/reset-password?token={token}"

    @router.post("/reset-password")
    async def reset_password(token: str = Body(...), password: str = Body(...)):
        try:
            # decode the token for verification
            reset_token_dict = decode_jwt(token=token, jwt_algorithm=JWT_ALGORITHM)
            check_token_expiry(reset_token_dict)
            # Now converting given password to hashed password using bcrypt
            hashed_password_into_string = get_hashed_password(password)
            # Updating Database with new password(hashed_password)
            email = reset_token_dict.get("email")
            update_hashed_password = update(User).where(User.email == email).values(
                hashed_password=hashed_password_into_string)
            await async_db_session.execute(update_hashed_password)
            await async_db_session.commit()
            
            return "Password has been changed successfully!"

        except exceptions.InvalidResetPasswordToken:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="INVALID_CREDENTIALS",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except (exceptions.InvalidResetPasswordToken, exceptions.UserNotExists, exceptions.UserInactive,):
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )
        except exceptions.InvalidPasswordException as e:
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

    return router





