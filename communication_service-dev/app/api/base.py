from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status": 1,
        "message": "Service is up and running."
    }
