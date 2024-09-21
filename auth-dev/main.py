from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from rb_utils.database import initiate_database
from fastapi_pagination import add_pagination



from sqladmin import Admin

from admin import *
from apis.base import api_router
from db.session import async_db_session
from settings import CONNECTION_CONFIG

app = FastAPI(title="Auth Service")
app.include_router(api_router)
add_pagination(app)

@app.get("/")
def health_check():
    return {
        "status": 1,
        "message": "Auth Service is up and running fine."
    }


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    try:
        await async_db_session.rollback()
    except:
        pass
    return JSONResponse(
        status_code=400,
        content={
            'message': f'{exc}'
        }
    )


@app.on_event("startup")
async def startup_event():
    await async_db_session.init()
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)

    admin = Admin(app, async_db_session.get_engine())
    register_admin_models(admin)


def register_admin_models(admin):
    admin.register_model(UserAdmin)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
