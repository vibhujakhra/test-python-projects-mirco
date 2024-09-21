from fastapi import APIRouter

from app.api.version1 import pricing

api_router = APIRouter()


@api_router.get("/health_check")
def health_check() -> dict:
    return {
        "status": 0,
        "message": "Server is up and running fine."
    }


api_router.include_router(pricing.router, prefix="/v1", tags=["pricing"])
