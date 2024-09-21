from fastapi import APIRouter

from apis.version1.cabinet import router

api_router = APIRouter()

api_router.include_router(router, prefix="/api/v1", tags=["Cabinet"])
