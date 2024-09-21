from fastapi import APIRouter

from apis.version1.authenticate import router
from apis.version1 import user_admin, misp_kyc_data
from apis.version1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(router)
api_router.include_router(user_admin.router, tags=['ADMIN USER'], prefix="/api/v1")
api_router.include_router(admin_router, tags=['ADMIN ALL'], prefix="/api/v1")
api_router.include_router(misp_kyc_data.router, tags=['MISP KYC'], prefix="/api/v1")
