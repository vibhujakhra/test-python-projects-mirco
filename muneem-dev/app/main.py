import logging
from typing import Optional
from logging import config
from urllib.request import Request

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.param_functions import Form
from fastapi.responses import JSONResponse
from rb_utils.database import initiate_database, sqldb
from sqladmin import Admin

from app import settings
from app.admin.payment_admin import *
from app.apis.routers import api_router
from app.settings import AUTH_LOGIN_URL, CONNECTION_CONFIG
from app.utils.exceptions import *

app = FastAPI(title="PaymentService")
app.include_router(api_router)

logging.config.fileConfig(settings.LOGGER_CONFIG_PATH)
logger = logging.getLogger("app.main")
@app.get("/")
def health_check():
    return {
        "status": 1,
        "message": "Payment service is up and running fine."
    }


@app.on_event("startup")
async def startup_event():
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


@app.exception_handler(ConsentNotFoundException)
async def validation_error_handler(request: Request, exc: ConsentNotFoundException):
    return JSONResponse(
        status_code=200,
        content={
            'message': "consent type id 2 is working right now i.e mandate form, please pass 2 as consent type id"
        }
    )


@app.exception_handler(ConsentNotUpdatedException)
async def consent_validation_error(request: Request, exc: ConsentNotUpdatedException):
    return JSONResponse(
        status_code=400,
        content={
            'message': 'unable to create policy as consent is not done yet'
        }
    )


@app.exception_handler(PayInSlipAlreadyGeneratedException)
async def pay_in_slip_already_generated_error(request: Request, exc: PayInSlipAlreadyGeneratedException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(ColumnMisMatchError)
async def column_mismatch_error(request: Request, exc: ColumnMisMatchError):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(DataverseNotRespondingError)
async def column_mismatch_error(request: Request, exc: DataverseNotRespondingError):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(PDFGenerationException)
async def pdf_generation_exception(request: Request, exc: PDFGenerationException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(EndorsementDataNotFoundException)
async def pdf_generation_exception(request: Request, exc: EndorsementDataNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(InvalidInputException)
async def invalid_input_exception(request: Request, exc: InvalidInputException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(EndorsementNumberNotFoundException)
async def invalid_input_exception(request: Request, exc: EndorsementNumberNotFoundException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(ChequeNotFoundException)
async def pdf_generation_exception(request: Request, exc: ChequeNotFoundException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(FinalizedPaymentStatus)
async def pdf_generation_exception(request: Request, exc: FinalizedPaymentStatus):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(BillingStatusNotMappedException)
async def pdf_generation_exception(request: Request, exc: BillingStatusNotMappedException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(PaymentNotFoundException)
async def pdf_generation_exception(request: Request, exc: PaymentNotFoundException):
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


def register_admin_models(admin):
    admin.register_model(PaymentStateAdmin)
    admin.register_model(ConsentStateAdmin)
    admin.register_model(ConsentAdmin)
    admin.register_model(ConsentTypeAdmin)
    admin.register_model(PaymentAdmin)
    admin.register_model(ChequeDetailsAdmin)
    admin.register_model(VerificationLinkAdmin)
    admin.register_model(MandateFormAdmin)
    admin.register_model(InsurerCallLogAdmin)
    admin.register_model(HistoryAdmin)
    admin.register_model(PaymentStatusAdmin)
    admin.register_model(PaymentModeAdmin)
    admin.register_model(VB64Admin)
    admin.register_model(BillingAdmin)
    admin.register_model(VB64RecordAdmin)
    admin.register_model(PayInSlipAdmin)


@app.post("/my-authenticate/")
async def authenticate_user(grant_type: str = Form(default=None, regex="password"),
                            username: str = Form(),
                            password: str = Form(),
                            scope: str = Form(default=""),
                            client_id: Optional[str] = Form(default=None),
                            client_secret: Optional[str] = Form(default=None), ):
    logger = logging.getLogger("api")
    json_body = {
        "grant_type": grant_type,
        "username": username,
        "password": password,
        "scope": scope
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=AUTH_LOGIN_URL, data=json_body) as response:
                response_dict = await response.json()
    except Exception as e:
        logger.exception(f"Exception encounter {e} while authenticate user.")
        raise HTTPException(
            status_code=400,
            detail="BAD_CREDENTIALS",
        )
    return response_dict


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Muneem",
        version="1.0.0",
        description="This service stores all the data regarding the payments for a given transaction",
        routes=app.routes,
    )
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema['paths'][path][method]["security"] = [
                {
                    "OAuth2PasswordBearer": []
                }
            ]
            pass
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "scopes": {},
                    "tokenUrl": "/my-authenticate/"
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
