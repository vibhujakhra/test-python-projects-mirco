from fastapi import APIRouter

from app.apis.version1.user_apis import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/api/v1", tags=["User"])
