import logging
import pandas as pd

from enum import Enum
from fastapi import APIRouter, Request, Depends
from typing import List, Union
from app.models.payment import VB64Status

from app.services.reports_analytics import ReportsAnalytics
from app.schemas.reports_analytics import *
from app.utils.exceptions import *

logger = logging.getLogger(__name__)

router = APIRouter()

class TransactionTypes(Enum):
    policy =  1
    endorsement =  2


@router.get("/64_VB_reports/")
async def get_vb64_reports(request: Request, filter_params: VB64ReportRequest = Depends()) -> Union[
    List[VB64Reports], NotDataFoundResponse]:
    logger.info("Getting vb64 reports")
    result = await ReportsAnalytics.vb_64_query(request=request, filter_params=filter_params)
    if type(result)==dict:
        return result
    df = pd.DataFrame([r.dict() for r in result])
    df.rename(columns={"vb_64_status":"64_vb_status"}, inplace=True)
    if filter_params.transaction_type_id ==TransactionTypes.policy.value:
        df.drop(columns=["approval_status"], inplace=True)
    df.columns = [(" ".join(i.split("_")).upper()) for i in df.columns]
    csv_string = df.to_csv(index=False)

    return {"data": result, "csv_data": csv_string}

# @router.get("/64_VB_policy_reports/")
# async def get_64_VB_policy_reports(request: Request, start_date: str, end_date: str) -> Union[
#     List[VB64Reports], NotDataFoundResponse]:
#     response = await ReportsAnalytics.vb_64_query(request=request, start_date=start_date, end_date=end_date,
#                                                   transaction_type_id=1)
#     return response

@router.get("/vb64_status/")
async def get_vb64_status() -> VB64StatusResponse:
    logger.info( "Fetching vb64 status")
    vb64_status = await VB64Status.fetch_all()
    return [VB64StatusResponse(id=item.id, name=item.name, code=item.code) for item in vb64_status]
