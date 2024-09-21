import io
import logging
import pandas as pd
from fastapi import UploadFile
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from app.data_insertion.main import insert_bulk_data
from app.models.admin_details import Oem
from app.schemas.admin_db_details import AssestUploadResponse
from app.settings import ERROR_FILE_URL, S3_BUCKET_URL
from app.models.location import *
from app.models.insurer import *
from app.models.vehicle_details import *
from app.models.financier import *
from app.models.addons import *
from app.utils.service import write_sub_variant_into_csv
import pathlib
from botocore.client import BaseClient
from fastapi import APIRouter, Depends, status
from app.utils.code_utils import get_async_s3_client, check_validation

logger = logging.getLogger('api')
router = APIRouter()

path = 'app/templates/'


@router.post("/upload_master/{data_type}/")
async def upload_document(data_type: str, document_file: UploadFile):
    logger.info(f"Upload master csv request -> table_name: {data_type}")
    db_data = pd.read_csv(document_file.file)
    data = {"error": "Uploaded file is empty."}
    if not db_data.empty:
        data = await insert_bulk_data(data_type, db_data)
        if data.get('status'):
            # slicing prefix(temp_) and suffix(.csv)
            url = ERROR_FILE_URL.format(data['filename'][5:-4])
            return JSONResponse({"status": f"{data['error_rows_no']} Records are incorrect", "url": url})

    return JSONResponse(data)


@router.get("/download_error_report/")
async def download_error_report(file_name: str):
    file_path = f"/tmp/{file_name}.csv"
    return FileResponse(file_path, media_type='application/octet-stream', filename=file_path)


@router.get("/download_template/{data_type}/")
async def download_table_template(data_type: str):
    res = {
        "country": path + 'country.csv',
        "state": path + 'State_Master_Template.csv',
        "city": path + 'City_Master_Template.csv',
        "pincode": path + 'Pincode_Master_Template.csv',
        "rto_zone": path + 'Rto_Zone_Master_Template.csv',
        "rto": path + 'Rto_Master_Template.csv',
        "oem": path + 'oem.csv',
        "model": path + 'Model_Master_Template.csv',
        "variant": path + 'Variant_Master_Template.csv',
        "sub_variant": path + 'sub_variant.csv',
        "bank": path + 'Bank_Master_Template.csv',
        "financier": path + 'Financier_Master_Template.csv',
        "insurer": path + 'Insurer_Master_Template.csv',
        "addon": path + 'addon.csv',
        "bundle": path + 'bundle.csv',
        "addon_bundle": path + 'addon_bundle.csv',
        "ex_showroom_price": path + 'Exshowroom_Master_Template.csv',
        "region": path + 'Region_Master_Template.csv',
        "city_cluster": path + 'city_cluster.csv',
        "rto_cluster": path + 'rto_cluster.csv',
        "insurer_local_office": path + 'Insurer_Local_Office_Master_Template.csv',
        'insurer_dealer_mapping': path + 'Insurer_Dealer_Mapping_Master_Template.csv'
    }
    try:
        if data_type == "ex_showroom_price":
            loc = res[data_type]
            await write_sub_variant_into_csv(loc)
        template_loc = res[data_type]
        read_template = pd.read_csv(template_loc)
        df = pd.DataFrame(read_template)
        str_stream_obj = io.StringIO()
        df.to_csv(str_stream_obj, index=False)
        response = StreamingResponse(iter([str_stream_obj.getvalue()]),
                                     media_type="text/csv"
                                     )
        response.headers["Content-Disposition"] = f"attachment; filename={data_type}.csv"

        return response

    except Exception as e:
        logger.exception(str(e))
        return {"message": "Error occur while downloading the template file"}


@router.post("/upload_doc/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, product_slug: str, file_name: str,
                      async_s3_client: BaseClient = Depends(get_async_s3_client)):
    file_name = file_name.lower()
    if file:
        file_extension = pathlib.Path(file.filename).suffix
        validation_check = check_validation(product_slug=product_slug, file_name=file_name,
                                            file_extension=file_extension)
        file_path = f"assets/{product_slug}/{file_name}{file_extension}"
        if not validation_check.is_valid:
            return AssestUploadResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                        error_message=validation_check.error_message)

        async with async_s3_client.client("s3") as s3:
            await s3.upload_fileobj(file.file, "sleep-dev", file_path)
            return AssestUploadResponse(status_code=status.HTTP_201_CREATED,
                                        document_url=f"https://{S3_BUCKET_URL}/{file_path}"
                                        )


@router.get("/update_status/{table_name}/{id}/")
async def update_status(id: int, table_name: str, is_active: bool):
    """_summary_

    Args:
        id (int): id is to be taken for the row of the table whose status is to be updated
        table_name (str): table name
        is_active (bool): true or false

    Returns:
        _type_: update is_active status of the row of the table 
    """
    res = {
        "country": Country,
        "state": State,
        "city": City,
        "pincode": Pincode,
        "rto_zone": RtoZone,
        "rto": Rto,
        "oem": Oem,
        "model": VehicleModel,
        "variant": Variant,
        "sub_variant": SubVariant,
        "insurer": Insurer,
        "addon": Addon,
        "bundle": Bundle,
        "addon_bundle": AddonBundle,
        "ex_showroom_price": ExShowRoomPrice,
        "bank": Bank,
        "financier": Financier,
        "region": Region,
        "city_cluster": CityCluster,
        "rto_cluster": RtoCluster,
        "insurer_local_office": InsurerLocalOffice,
        "insurer_dealer_mapping": ICDealerMapping
    }
    await res[table_name].update(id, **{"is_active": is_active})
    return {"msg": "Status is updated"}
