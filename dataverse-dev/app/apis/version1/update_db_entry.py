import logging

import http3
from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from app.models.insurer import Insurer, InsurerLocalOffice, ICDealerMapping
from app.schemas.admin_db_details import *
from app.models.location import *
from app.models.vehicle_details import *
from app.models.financier import *
from rb_utils.database import sqldb

from app.settings import USER_DETAILS_UPDATE_URL

logger = logging.getLogger('api')
router = APIRouter()


@router.patch("/update_state/{id}/")
async def update_state(id: int, state_request: UpdateStateRequest):
    logger.info(f"update object request for class: state | object_id: {id} ")
    request = state_request.dict()
    new_dict = {
        "gst_code": request["gst_code"],
        "region": request["region_id"],
        "name": request["state_name"],
        "is_active": request["is_active"]
    }
    try:
        await State.update(id, **new_dict)
        return {"msg": "Data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: state | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_city/{id}/")
async def update_city(id: int, city_request: UpdateCityRequest):
    logger.info(f"update object request for class: city | object_id: {id} ")
    request = city_request.dict()
    new_dict = {
        "name": request["city_name"],
        "state_id": request["state_id"],
        "is_active": request["is_active"]
    }
    try:
        await City.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: city | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_rto_zone/{id}/")
async def update_rto_zone(id: int, rto_zone_request: UpdateRtoZoneRequest):
    logger.info(f"update object request for class: zone | object_id: {id} ")
    request = rto_zone_request.dict()
    new_dict = {
        "zone_name": request["rto_zone_name"],
        "is_active": request["is_active"]
    }
    try:
        await RtoZone.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: zone | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_region/{id}/")
async def update_region(id: int, region_request: UpdateRegionRequest):
    logger.info(f"update object request for class: region | object_id: {id} ")
    request = region_request.dict()
    new_dict = {
        "name": request["region_name"],
        "rto_zone_id": request["rto_zone_id"],
        "is_active": request["is_active"]
    }
    try:
        await Region.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: region | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_rto/{id}/")
async def update_rto(id: int, rto_request: UpdateRtoRequest):
    logger.info(f"update object request for class: rto | object_id: {id} ")
    request = rto_request.dict()
    new_dict = {
        "state_id": request["state_id"],
        "city_id": request["city_id"],
        "name": request["rto_name"],
        "is_active": request["is_active"]
    }
    try:
        await Region.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: rto | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_pincode/{id}/")
async def update_pincode(id: int, pincode_request: UpdatePincodeRequest):
    logger.info(f"update object request for class: pincode | object_id: {id} ")
    request = pincode_request.dict()
    new_dict = {
        "state_id": request["state_id"],
        "city_id": request["city_id"],
        "name": request["pincode"],
        "is_active": request["is_active"]
    }
    try:
        await Pincode.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: pincode | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_rto_cluster/{rto_cluster_id}/")
async def update_rto_cluster(rto_cluster_id: int, rto_cluster_request: UpdateRtoClusterRequest):
    logger.info(f"update object request for class: rto cluster | object_id: {id} ")
    request = rto_cluster_request.dict()
    rto_id_list = request["rto_id"]
    await RtoCluster.update(rto_cluster_id, **{"name": request["name"], "is_active": request["is_active"]})
    try:
        rto_cluster_query = await sqldb.execute(
            select(RtoClusterRtoMapping).where(RtoClusterRtoMapping.rto_cluster_id == rto_cluster_id))
        rto_cluster_data = rto_cluster_query.scalars().all()
        for rto_cluster in rto_cluster_data:
            if rto_cluster.rto_id in rto_id_list:
                await RtoClusterRtoMapping.update(rto_cluster.id, **{"is_active": True})
            else:
                await RtoClusterRtoMapping.update(rto_cluster.id, **{"is_active": False})

        for rto_id in rto_id_list:
            request["rto_id"] = rto_id
            rto_cluster_mapping_query = await sqldb.execute(
                select(RtoClusterRtoMapping).where(RtoClusterRtoMapping.rto_id == rto_id,
                                                   RtoClusterRtoMapping.rto_cluster_id == rto_cluster_id))
            rto_cluster_mapping_data = rto_cluster_mapping_query.scalars().first()
            if not rto_cluster_mapping_data:
                await RtoClusterRtoMapping.create(**{"rto_cluster_id": rto_cluster_id, "rto_id": rto_id,
                                                     'is_active': request["is_active"]})
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: rto cluster | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_city_cluster/{city_cluster_id}/")
async def update_city_cluster(city_cluster_id: int, city_cluster_request: UpdateCityClusterRequest):
    logger.info(f"update object request for class: city cluster | object_id: {id} ")
    request = city_cluster_request.dict()
    city_id_list = request["city_id"]
    await CityCluster.update(city_cluster_id, **{"name": request["name"], "is_active": request["is_active"]})
    try:
        city_cluster_query = await sqldb.execute(
            select(CityClusterCityMapping).where(CityClusterCityMapping.city_cluster_id == city_cluster_id))
        city_cluster_data = city_cluster_query.scalars().all()
        for city_cluster in city_cluster_data:
            if city_cluster.city_id in city_id_list:
                await CityClusterCityMapping.update(city_cluster.id, **{"is_active": True})
            else:
                await CityClusterCityMapping.update(city_cluster.id, **{"is_active": False})

        for city_id in city_id_list:
            request["city_id"] = city_id
            city_cluster_mapping_query = await sqldb.execute(
                select(CityClusterCityMapping).where(CityClusterCityMapping.city_id == city_id,
                                                     CityClusterCityMapping.city_cluster_id == city_cluster_id))
            city_cluster_mapping_data = city_cluster_mapping_query.scalars().first()
            if not city_cluster_mapping_data:
                await CityClusterCityMapping.create(**{"city_cluster_id": city_cluster_id, "city_id": city_id,
                                                       'is_active': request["is_active"]})
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: city cluster | id: {city_cluster_id}, exception "
                         f"encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_bank/{id}/")
async def update_bank(id: int, bank_request: UpdateBankRequest):
    logger.info(f"update object request for class: bank | object_id: {id} ")
    request = bank_request.dict()
    new_dict = {
        "name": request["bank_name"],
        "is_active": request["is_active"]
    }
    try:
        await Bank.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: bank | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_financier/{id}/")
async def update_financier(id: int, financier_request: UpdateFinancierRequest):
    logger.info(f"update object request for class: financier | object_id: {id} ")
    request = financier_request.dict()
    new_dict = {
        "name": request["financier_name"],
        "is_active": request["is_active"]
    }
    try:
        await Financier.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: financier | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_insurer/{id}/")
async def update_insurer(id: int, ic_request: UpdateIcUserInfo):
    logger.info(f"update object request for class: insurer | object_id: {id} ")
    insurer_query = await sqldb.execute(select(Insurer).where(Insurer.id == id))
    insurer_obj = insurer_query.scalars().first()
    insurer_request = ic_request.ic_request.dict()
    user_info_request = ic_request.user_info_request.dict()
    registered_address = " | ".join([insurer_request['ic_address_1'], insurer_request['ic_address_2'], insurer_request['ic_address_3']])
    insurer_request['registered_office_address'] = registered_address
    try:
        await Insurer.update(id, **insurer_request)
        client = http3.AsyncClient()
        user_details_url = f'{USER_DETAILS_UPDATE_URL}?user_id={insurer_obj.user_obj_id}'
        await client.patch(url=user_details_url, json=user_info_request)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: insurer | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_insurer_local_office/{id}/")
async def update_insurer_local_office(id: int, ic_local_office_request: UpdateInsurerLocalOffice):
    logger.info(f"update object request for class: insurer local office | object_id: {id} ")
    request = ic_local_office_request.dict()
    try:
        await InsurerLocalOffice.update(id, **request)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(
            f"Not able to update records for class: insurer local office | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_insurer_dealer_mapping/{id}/")
async def update_insurer_dealer_mapping(id: int, ic_dealer_mapping_request: UpdateInsurerDealerMapping):
    logger.info(f"update object request for class: insurer dealer mapping | object_id: {id} ")
    request = ic_dealer_mapping_request.dict()
    try:
        insurer_id_list = request["insurer_id"]
        for insurer_id in insurer_id_list:
            request["insurer_id"] = insurer_id
            await ICDealerMapping.update(id, **request)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(
            f"Not able to update records for class: insurer dealer mapping | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_vehicle_model/{id}/")
async def update_vehicle_model(id: int, model_request: UpdateModelRequest):
    logger.info(f"update object request for class: vehicle model | object_id: {id} ")
    request = model_request.dict()
    new_dict = {
        "name": request["model_name"],
        "is_active": request["is_active"]
    }
    try:
        await VehicleModel.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: vehicle model | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_vehicle_variant/{id}/")
async def update_vehicle_variant(id: int, subvariant_id: int, variant_request: UpdateVehicleVariantRequest):
    logger.info(f"update object request for class: vehicle variant | object_id: {id} ")
    request = variant_request.dict()
    new_dict = {
        "name": request["name"],
        "model_id": request["model_id"],
        "fuel_type_id": request["fuel_type_id"],
        "cubic_capacity": request["cubic_capacity"],
        "kilowatt_range": request["kilowatt_range"],
        "seating_capacity": request["seating_capacity"],
        "is_bifuel": request["is_bifuel"],
        "is_active": request["is_active"]
    }
    try:
        await Variant.update(id, **new_dict)
    except Exception as e:
        logger.exception(f"Not able to update records for class: vehicle variant | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")

    sub_variant_dict = {
        "color": request["color"],
        "tone": request["tone"],
        "variant_id": id
    }
    try:
        await SubVariant.update(subvariant_id, **sub_variant_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(f"Not able to update records for class: vehicle variant | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")


@router.patch("/update_vehicle_variant_price/{id}/")
async def update_vehicle_variant_price(id: int, variant_price_request: UpdateVehicleVariantPriceRequest):
    logger.info(f"update object request for class: region | object_id: {id} ")
    request = variant_price_request.dict()
    new_dict = {
        "charges_price": request["charges_price"],
        "exShowRoomPrice": request["exShowRoomPrice"],
        "variant_id": request["variant_id"],
        "state_id": request["state_id"],
    }
    try:
        await ExShowRoomPrice.update(id, **new_dict)
        return {"msg": "data is updated"}
    except Exception as e:
        logger.exception(
            f"Not able to update records for class: vehicle variant | id: {id}, exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to update the records")
