from urllib.request import Request

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from rb_utils.database import initiate_database, sqldb
from sqladmin import Admin

from app.admin.users_admin import UserAdmin
from app.apis.routers import api_router
from app.settings import CONNECTION_CONFIG
from app.utils.exceptions import *

app = FastAPI(title="User Service")
app.include_router(api_router)


@app.get("/")
def health_check():
    """
    The health_check function is used to check the health of the payment service.
        ---
        tags:
          - Health Check API

    :return: A dictionary that contains the status and message
    
    """
    return {
        "status": 1,
        "message": "Payment service is up and running fine."
    }


@app.on_event("startup")
async def startup_event():
    """
    The startup_event function is a coroutine that runs when the bot starts up.
    It initiates the database and registers all of our models with Flask-Admin.

    :return: A list of tasks to run when the server starts
    
    """
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


@app.exception_handler(ColumnMisMatchError)
async def column_mismatch_error(request: Request, exc: ColumnMisMatchError):
    """
    The column_mismatch_error function is a custom error handler for the ColumnMisMatchError exception.
    It returns a JSONResponse with status code 400 and an appropriate message.

    :param request:Request: Pass the request object to the function
    :param exc:ColumnMisMatchError: Catch the exception that is raised when a column mismatch occurs
    :return: A jsonresponse with a status_code of 400 and the message from the exception
    
    """
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


@app.exception_handler(InvalidInputException)
async def invalid_input_exception(request: Request, exc: InvalidInputException):
    """
    The invalid_input_exception function is a custom exception handler that returns a JSON response with the status
    code 400 and an error message.

    :param request:Request: Access the request object
    :param exc:InvalidInputException: Get the message from the exception
    :return: A jsonresponse with a status code of 400 and an error message
    
    """
    return JSONResponse(
        status_code=400,
        content={
            'message': exc.message
        }
    )


def register_admin_models(admin):
    """
    The register_admin_models function is a helper function that registers all of the models in our application with
    the admin interface. This allows us to easily add, edit, and delete objects from the database through the admin
    interface.

    :param admin: Register the models with the admin site
    :return: The admin object

    """
    admin.register_model(UserAdmin)
