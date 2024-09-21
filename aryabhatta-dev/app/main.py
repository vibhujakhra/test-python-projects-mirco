import logging
from logging import config
from fastapi import FastAPI, HTTPException
from sqladmin import Admin
from app import settings
from app.admin import CoverRateAdmin, TPRateAdmin, PARateAdmin, ODRateAdmin, DepreciationAdmin, AddOnBundlePriceAdmin, \
    DiscountAdmin, NCBAdmin, DeductibleAdmin
from app.api.routers import api_router
from rb_utils.database import initiate_database, sqldb

from typing import Optional
import aiohttp
from fastapi.openapi.utils import get_openapi
from fastapi.param_functions import Form
from app.settings import AUTH_LOGIN_URL, CONNECTION_CONFIG

app = FastAPI(title="Pricing Service")

app.include_router(router=api_router, prefix="/api")

logging.config.fileConfig(settings.LOGGER_CONFIG_PATH)


@app.on_event("startup")
async def startup_event():
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


def register_admin_models(admin):
    admin.register_model(CoverRateAdmin)
    admin.register_model(TPRateAdmin)
    admin.register_model(PARateAdmin)
    admin.register_model(DepreciationAdmin)
    admin.register_model(ODRateAdmin)
    admin.register_model(DiscountAdmin)
    admin.register_model(AddOnBundlePriceAdmin)
    admin.register_model(NCBAdmin)
    admin.register_model(DeductibleAdmin)


@app.post("/my-authenticate/")
async def authenticate_user(grant_type: str = Form(default=None, regex="password"),
                            username: str = Form(),
                            password: str = Form(),
                            scope: str = Form(default=""),
                            client_id: Optional[str] = Form(default=None),
                            client_secret: Optional[str] = Form(default=None),):

    logger = logging.getLogger("api")
    json_body = {
        "grant_type": grant_type,
        "username": username,
        "password": password,
        "scope": scope,
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
        title="Aryabhatta",
        version="1.0.0",
        description="Pricing service is used for internal calculations. Addon premium, bundle premium, Discount "
                    "calculations are handled by this service.",
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
