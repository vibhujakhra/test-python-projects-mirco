from fastapi import FastAPI
from rb_utils.database import sqldb, initiate_database
from sqladmin import Admin

from app.admin.admin import *
from app.api.base import router
from app.settings import CONNECTION_CONFIG

app = FastAPI(title="Communication_service")

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
    admin = Admin(app, sqldb.get_engine())
    register_admin_models(admin)


def register_admin_models(admin):
    admin.register_model(CommunicationRequestAdmin)
    admin.register_model(TemplatesAdmin)
