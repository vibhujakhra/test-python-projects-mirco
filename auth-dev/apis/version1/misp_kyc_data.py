import logging

import pandas as pd
from fastapi import UploadFile, APIRouter
from fastapi.responses import JSONResponse
from db.session import async_db_session

from schemas.user import MispOemRequest
from utils.misp_kyc_details import MispDpOnboarding

logger = logging.getLogger('api')
router = APIRouter()


@router.post("/upload_dp/")
async def upload_dp(document_file: UploadFile, misp_code: str):
    """
    The upload_dp function is used to upload a csv file containing the designated person data.
    The function takes in an UploadFile object and returns a JSONResponse object.

    :param document_file: UploadFile: Upload the file from the user
    :return: A json response object with the status and url of the file
    """
    logger.info("Upload designated person csv.")
    dp_data = pd.read_csv(document_file.file)
    data = {"error": "Uploaded file is empty."}
    converted_dataframe = dp_data.applymap(lambda x: str(x) if x else None)
    converted_dataframe["misp_code"] = misp_code
    if not converted_dataframe.empty:
        data = await MispDpOnboarding.insert_dp_data(dataframe=converted_dataframe, session=async_db_session)
        if data.get('status_code') == 400:
            async_db_session.rollback()
            return JSONResponse({"status": "Records are incorrect. Kindly check and re-upload"})
        async_db_session.commit()
    return JSONResponse(data)


@router.post("/oem_and_misp_details/")
async def oem_and_misp(details_request: MispOemRequest):
    """
    The oem_and_misp function takes a MispOemRequest object and returns the OEM details for that email address.
    The function first checks if the email is in MISP. If it is true,
    then we return a dictionary with all of the information from source.

    :param details_request: MispOemRequest: Pass the data from the misp event to this function
    :return: The details of the oems that are mapped to misp
    """
    mapped_oem_detail = await MispDpOnboarding.mapped_oem_details(mapped_details_request=details_request)
    return mapped_oem_detail
