from fastapi import APIRouter

from app.apis.version1.generate_cancellation import motor_cancellation_router
from app.apis.version1.generate_endorsemet import motor_endorsement_router
from app.apis.version1.generate_policy import motor_policy_router

api_router = APIRouter()

motor_router = "/api/v1/motor"

api_router.include_router(motor_policy_router, prefix=motor_router, tags=["policy_pdf"])
api_router.include_router(motor_endorsement_router, prefix=motor_router, tags=["endorsement_pdf"])
api_router.include_router(motor_cancellation_router, prefix=motor_router, tags=["cancellation_pdf"])
