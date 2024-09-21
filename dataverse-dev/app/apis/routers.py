from fastapi import APIRouter

from app.apis.version1 import individual_db_entry, master_upload, service_communication_api, dataverse_api, \
    update_db_entry, search_in_table

api_router = APIRouter()

api_router.include_router(dataverse_api.router, prefix="/api/v1", tags=["Fetching Meta data"])
api_router.include_router(master_upload.router, prefix="/api/v1", tags=["Upload Bulk Master data"])
api_router.include_router(individual_db_entry.router, prefix="/api/v1", tags=["Single Data Entry in DB"])
api_router.include_router(update_db_entry.router, prefix="/api/v1", tags=["Update data in DB"])
api_router.include_router(search_in_table.router, prefix="/api/v1", tags=["search data in DB"])
api_router.include_router(service_communication_api.router, prefix="/api/v1/service_communication",
                          tags=["Service communication"])
api_router.include_router(dataverse_api.search_router, prefix="/api/v1/search",
                          tags=["Smart Search"])
