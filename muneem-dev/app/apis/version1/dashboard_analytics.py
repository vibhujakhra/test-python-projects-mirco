import logging

from fastapi import APIRouter, Request
from sqlalchemy import select
from sqlalchemy.sql import func

from app.models.payment import Payment
from app.schemas.dashboard_analytics import *
from app.services.dashboard_analytics import PaymentServiceTrend

router = APIRouter()
logger = logging.getLogger("api")

@router.get("/insurer_wise_premium/", response_model=MultipleInsurerWisePremiumResponse)
async def insurer_wise_premium(start_date: str, end_date: str, request: Request):
    logger.info(f"Getting insurer wise premium from {start_date} to {end_date}")
    query = select(Payment.insurer_code, func.sum(Payment.payment_amount)).group_by(Payment.insurer_code).where(Payment.policy_type_id!=None)
    query_payments = await PaymentServiceTrend.get_payment_query(start_date=start_date, end_date=end_date,
                                                                 request=request, query=query)
    total_premium = sum([premium for _, premium in query_payments])
    result_data = [{"insurer_code": insurer, "premium": premium} for insurer, premium in query_payments]
    logger.info("Successfully returned result data")
    return {"data": result_data, "total_premium": total_premium}


@router.get("/get_daily_policy_trend/")
async def daily_policy_trend(start_date: str, end_date: str, trend_pattern: str, request: Request):
    logger.info(f"Get daily policy trend from {start_date} to {end_date}")
    if trend_pattern not in ["year", "month", "day", "hour"]:
        return {
            "error": "Requested trend pattern is not valid."
        }
    query = select(func.DATE_TRUNC(trend_pattern, Payment.created_at), Payment.policy_type_id)
    query_payments = await PaymentServiceTrend.get_payment_query(start_date=start_date, end_date=end_date,
                                                                 request=request, query=query)
    temp_response = {}
    for time_stamp, policy_type in query_payments:
        if not (time_stamp or policy_type):
            continue
        policy_type_dict = temp_response.get(policy_type, {})
        policy_type_dict_timestamp = policy_type_dict.get(time_stamp.strftime("%d-%m-%Y %H:%M"), 0)
        policy_type_dict[time_stamp.strftime("%d-%m-%Y %H:%M")] = policy_type_dict_timestamp + 1
        temp_response[policy_type] = policy_type_dict
    result_data = []
    for policy_type, time_stamp_count in temp_response.items():
        result_data = result_data + [{"policy_type": policy_type, "time_stamp": time_stamp, "count": count} for
                                     time_stamp, count in
                                     time_stamp_count.items()]
    logger.info("Successfully returned result data")
    return {"data": result_data}


@router.get("/get_plan_wise_policy_count/", response_model=MultiplePlanWisePolicyCountResponse)
async def plan_wise_policy_count(start_date: str, end_date: str, request: Request):
    logger.info( f"Get plan_wise_policy_count from {start_date} to {end_date}")
    query = select(Payment.vehicle_cover_id, func.count(Payment.vehicle_cover_id)).group_by(
        Payment.vehicle_cover_id)
    query_payments = await PaymentServiceTrend.get_payment_query(start_date=start_date, end_date=end_date,
                                                                 request=request, query=query)
    total_policy = sum([policy_count for _, policy_count in query_payments if _])
    result_data = [
        {"vehicle_cover_type": cover_type, "policy_count": count, "policy_percentage": (count / total_policy * 100)} for
        cover_type, count in query_payments if cover_type]
    logger.info("Successfully get the result data")
    return {"data": result_data, "total_policy": total_policy}


@router.get("/get_plan_wise_premium/", response_model=MultiplePlanWisePremiumResponse)
async def plan_wise_premium(start_date: str, end_date: str, request: Request):
    logger.info( f"Get plan_wise_premium from {start_date} to {end_date}")
    query = select(Payment.vehicle_cover_id, func.sum(Payment.payment_amount)).group_by(Payment.vehicle_cover_id)
    query_payments = await PaymentServiceTrend.get_payment_query(start_date=start_date, end_date=end_date,
                                                                 request=request, query=query)
    total_premium = sum([premium for _, premium in query_payments])
    result_data = [
        {"vehicle_cover_type": cover_type, "premium": premium, "premium_percentage": (premium / total_premium * 100)}
        for cover_type, premium in query_payments if cover_type]
    logger.info("Successfully get the result data")
    return {"data": result_data, "total_premium": total_premium}
