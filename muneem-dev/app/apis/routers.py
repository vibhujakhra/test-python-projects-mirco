from fastapi import APIRouter

from app.apis.version1.payment import router as payment_router
from app.apis.version1.pay_in_slip import router as pay_in_slip_router
from app.apis.version1.vb64 import router as vb64_router
from app.apis.version1.billing import router as billing_router
from app.apis.version1.dashboard_analytics import router as dashboard_router
from app.apis.version1.reports_analytics import router as reports_router
from app.apis.version1.payment_gateway import router as pg_router
from app.apis.version1.lock_and_unlock import router as lock_unlock_router

api_router = APIRouter()

api_router.include_router(payment_router, prefix="/api/v1", tags=["Payment"])
api_router.include_router(pay_in_slip_router, prefix='/api/v1', tags=["pay_in_slip"])
api_router.include_router(billing_router, prefix='/api/v1', tags=["Billing"])
api_router.include_router(vb64_router, prefix='/api/v1', tags=["VB64"])
api_router.include_router(dashboard_router, prefix='/api/v1', tags=["dashboard_analytics"])
api_router.include_router(reports_router, prefix='/api/v1', tags=["reports_analytics"])
api_router.include_router(pg_router, prefix='/api/v1', tags=["payment_gateway"])
api_router.include_router(lock_unlock_router, prefix='/api/v1', tags=["lock_and_unlock"])
