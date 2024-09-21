import logging
from typing import Optional

import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.param_functions import Form
from fastapi.responses import JSONResponse
from rb_utils.database import initiate_database, sqldb
from sqladmin import Admin

from app.admin import TemplateAdmin, DocumentStatusAdmin
from app.apis.base import api_router
from app.settings import CONNECTION_CONFIG, AUTH_LOGIN_URL
from app.utils.exceptions import KafkaPublishToQueueException, PDFGenerationException, GetAPIException

app = FastAPI(title="Documentic")
app.include_router(api_router)


@app.get("/")
def health_check():
    """
    The health_check function is used to check the health of the service.
        ---
        tags: [health]

    :return: A dictionary with the status and message
    """
    return {
        "status": 1,
        "message": "Service is up and running fine."
    }


@app.on_event("startup")
async def startup_event():
    """
    The startup_event function is a coroutine that runs when the bot starts up.
    It initializes the database and registers all of our models with Flask-Admin.

    :return: A list of tasks
    """
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


def register_admin_models(admin):
    """
    The register_admin_models function is called by the admin.py module in the root of this project.
    It registers all models that should be available to the Django Admin interface with a custom
    admin class, if one exists for that model.

    :param admin: Register the models with the admin site
    :return: The admin object
    """
    admin.register_model(TemplateAdmin)
    admin.register_model(DocumentStatusAdmin)


@app.exception_handler(KafkaPublishToQueueException)
async def kafka_publish_to_queue_exception_handler(exc: KafkaPublishToQueueException):
    """
    The kafka_publish_to_queue_exception_handler function is a custom exception handler for the KafkaPublishToQueueException.
    It logs the error and returns a JSONResponse with status code 500 and an appropriate message.

    :param exc: KafkaPublishToQueueException: Catch the exception and handle it
    :return: A jsonresponse with the error message
    """
    logger = logging.getLogger("main")
    logger.exception(exc.name, exc.message)
    return JSONResponse(
        status_code=500,
        content={
            'message': f'{exc.message}'
        }
    )


@app.exception_handler(PDFGenerationException)
async def kafka_publish_to_queue_exception_handler(exc: PDFGenerationException):
    """
    The kafka_publish_to_queue_exception_handler function is a custom exception handler for the kafka_publish_to_queue function.
    It will catch any exceptions raised by the kafka_publish_to queue function and return an appropriate response to the client.

    :param exc: PDFGenerationException: Catch the exception that is thrown from the kafka_publish_to_queue function
    :return: The following json response:
    """
    logger = logging.getLogger("main")
    logger.exception(exc.name, exc.message)
    return JSONResponse(
        status_code=500,
        content={
            'message': f'{exc.message}'
        }
    )


@app.exception_handler(GetAPIException)
async def exception_handler(exc: GetAPIException):
    """
    The exception_handler function is a custom exception handler that will be called when an exception occurs in the
    application. It returns a JSON response with status code 404 and message 'Not Found'. The function takes one argument,
    exc, which is the exception object.

    :param exc: GetAPIException: Pass the exception to the function
    :return: A jsonresponse object with a 404 status code and the error message
    """
    return JSONResponse(
        status_code=404,
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
    """
    The authenticate_user function is used to authenticate a user.
        It takes in the following parameters:
            grant_type (str): The type of authentication being performed.  This should be set to &quot;password&quot; for this function.
            username (str): The username of the user attempting to log in.
            password (str): The password of the user attempting to log in.

    :param grant_type: str: Determine which grant type to use
    :param regex: Validate the input
    :param username: str: Specify the username of the user to be authenticated
    :param password: str: Get the password from the user
    :param scope: str: Specify the scope of the token
    :param client_id: Optional[str]: Identify the client that is making the request
    :param client_secret: Optional[str]: Pass the client_secret to the authenticate_user function
    :param : Get the user_id from the token
    :return: A dictionary with the following keys:
    """
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
    """
    The custom_openapi function is used to add security definitions to the OpenAPI schema.

    :return: The openapi schema with security
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Documentic",
        version="1.0.0",
        description="This service creates the policy schedule (i.e policy document) for the given transaction",
        routes=app.routes,
    )
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema['paths'][path][method]["security"] = [
                {
                    "OAuth2PasswordBearer": []
                }
            ]
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
