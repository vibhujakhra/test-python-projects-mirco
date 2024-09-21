import aiohttp
import logging.config
from typing import Optional
from urllib.request import Request

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.param_functions import Form
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from rb_utils.database import initiate_database, sqldb
from sqladmin import Admin

from app.admin.addon_detail import *
from app.admin.location_details import *
from app.admin.personal_detail import *
from app.admin.policy_detail import *
from app.admin.vehicle_details import *
from app.apis.routers import api_router
from app.settings import AUTH_LOGIN_URL, CONNECTION_CONFIG
from app.utils.exceptions import DatabaseException

app = FastAPI(title="Dataverse")

app.include_router(api_router)

add_pagination(app)


# logging.config.fileConfig("../logger.ini")


@app.get("/")
def health_check():
    return {
        "status": 1,
        "message": "Dataverse service is up and running fine."
    }


@app.on_event("startup")
async def startup_event():
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


def register_admin_models(admin):
    admin.register_model(OemDetailAdmin)
    admin.register_model(VehicleDetailAdmin)
    admin.register_model(VehicleVariantDetailAdmin)
    admin.register_model(SubVariantDetailAdmin)
    admin.register_model(PolicyDetailAdmin)
    admin.register_model(VehicleTypeDetailAdmin)
    admin.register_model(FuelTypeDetailAdmin)
    admin.register_model(ExshowroomPriceDetailAdmin)
    admin.register_model(CountryDetailAdmin)
    admin.register_model(StateDetailAdmin)
    admin.register_model(CityDetailAdmin)
    admin.register_model(RtoDetailAdmin)
    admin.register_model(RtoZoneDetailAdmin)
    admin.register_model(GeoExtensionDetailAdmin)
    admin.register_model(VoluntaryDeductibleDetailAdmin)
    admin.register_model(NCBDetailAdmin)
    admin.register_model(PaCoverDetailAdmin)
    admin.register_model(SalutationDetailAdmin)
    admin.register_model(InsurerDetailAdmin)
    admin.register_model(InsurerBundleDetailAdmin)
    admin.register_model(FinancierDetailAdmin)
    admin.register_model(BankDetailAdmin)
    admin.register_model(DealerDetailAdmin)
    admin.register_model(DesignatedPersonDetailAdmin)
    admin.register_model(SalesManagerDetailAdmin)
    admin.register_model(RelationDetailAdmin)
    admin.register_model(TransactionTypeAdmin)
    admin.register_model(AgreementTypeAdmin)
    admin.register_model(VB64TypeAdmin)


@app.exception_handler(DatabaseException)
async def unicorn_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=400,
        content={
            'message': f'{exc.message}'
        }
    )


@app.post("/my-authenticate/")
async def authenticate_user(grant_type: str = Form(default=None, regex="password"),
                            username: str = Form(),
                            password: str = Form(),
                            scope: str = Form(default=""),
                            client_id: Optional[str] = Form(default=None),
                            client_secret: Optional[str] = Form(default=None), ):
    logger = logging.getLogger("api")
    try:
        json_body = {
            "grant_type": grant_type,
            "username": username,
            "password": password,
            "scope": scope
        }
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
        title="Dataverse",
        version="1.0.0",
        description="The dataverse is central service which contains all the metadata(static data) required for all "
                    "the services, like Location, MMV Mapping etc.",
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

    uvicorn.run(app, host="0.0.0.0", port=8000)
