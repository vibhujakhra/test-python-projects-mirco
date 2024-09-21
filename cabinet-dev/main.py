import aiohttp
import logging.config
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.param_functions import Form
from settings import AUTH_LOGIN_URL

from apis.base import api_router

app = FastAPI(title="Doc upload to S3")

app.include_router(api_router)


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
        title="Cabinet",
        version="1.0.0",
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