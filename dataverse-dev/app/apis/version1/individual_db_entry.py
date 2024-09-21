import logging
from typing import Dict

import http3
from fastapi import APIRouter, status, HTTPException
from fastapi_pagination import paginate, Page
from rb_utils.database import sqldb
from sqlalchemy.future import select

from app.models.admin_details import Dealer, Workshop, Oem
from app.models.financier import Bank, Financier
from app.models.insurer import Insurer, InsurerLocalOffice, ICDealerMapping
from app.models.location import City, Pincode, Country, State, Rto, RtoZone, RtoCluster, Region, CityCluster, \
    CityClusterCityMapping, RtoClusterRtoMapping
from app.models.vehicle_details import Variant, FuelType, ExShowRoomPrice, VehicleModel, SubVariant
from app.schemas.admin_db_details import *
from app.services.admin_details import AdminRepository
from app.services.vehicle import VehicleRepository
from app.settings import USER_PASSWORD, AUTH_REGISTER_URL, USER_DETAILS_URL
from app.utils.service import call_auth_api

logger = logging.getLogger('api')
router = APIRouter()


@router.post("/add_city/")
async def add_city(city_request: AddCityRequest) -> AddResponse:
    logger.info(f"create object request for class: City | arguments: {city_request}")
    new_dict = {
        "name": city_request.city_name,
        "state_id": city_request.state_id,
        "is_active": city_request.is_active
    }
    try:
        await City.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: City | arguments: {city_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_state/")
async def add_state(state_request: AddStateRequest) -> AddResponse:
    logger.info(f"create object request for class: State | arguments: {state_request}")
    country_query = select(Country.id).where(Country.name == "India")
    country_session = await sqldb.execute(country_query)
    country_id = country_session.scalars().first()
    new_dict = {
        "name": state_request.state_name,
        "country_id": country_id,
        "region": state_request.region_id,
        "is_active": state_request.is_active,
        "gst_code": state_request.gst_code
    }
    try:
        await State.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: State | arguments: {state_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_pincode/")
async def add_pincode(pincode_request: AddPincodeRequest) -> AddResponse:
    logger.info(f"create object request for class: Pincode | arguments: {pincode_request}")
    new_dict = {
        "name": pincode_request.pincode,
        "state_id": pincode_request.state_id,
        "city_id": pincode_request.city_id,
        "is_active": pincode_request.is_active
    }
    try:
        await Pincode.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Pincode | arguments: {pincode_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_model/")
async def add_model(model_request: AddModelRequest) -> AddResponse:
    logger.info(f"create object request for class: VehicleModel | arguments: {model_request}")
    oem_query = select(Oem.id).where(Oem.code == "RB")
    oem_session = await sqldb.execute(oem_query)
    oem_id = oem_session.scalars().first()
    new_dict = {
        "name": model_request.model_name,
        "oem_id": oem_id,  # TODO: For now oem is hard coded.
        "is_active": model_request.is_active

    }
    try:
        await VehicleModel.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: VehicleModel | arguments: {model_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_variant/")
async def add_variant(variant_request: AddVariantRequest) -> AddResponse:
    logger.info(f"create object request for class: Variant | arguments: {variant_request}")
    request = variant_request.dict()
    variant_dict = {
        "name": request.pop("variant_name"),
        "fuel_type_id": request.pop("fuel_type_id"),
        "model_id": request.pop("model_id"),
        "cubic_capacity": request.pop("cubic_capacity"),
        "seating_capacity": request.pop("seating_capacity"),
        "kilowatt_range": request.pop("kilowatt_range"),
        "is_bifuel": request.pop("is_bifuel"),
        "is_active": request.pop("is_active")
    }
    try:
        variant = await Variant.create(**variant_dict)
    except Exception as e:
        logger.exception(
            f"create object request for class: Variant | arguments: {variant_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")
    try:
        request.update({"variant_id": variant.id})
        await SubVariant.create(**request)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Sub-Variant | arguments: {variant_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_variant_price/")
async def add_variant_price(variant_price_request: ExShowroomPriceRequest) -> AddResponse:
    logger.info(f"create object request for class: ExShowroomPrice | arguments: {variant_price_request}")
    request = variant_price_request
    new_dict = {
        "exShowRoomPrice": request.exShowRoomPrice,
        "state_id": request.state_id,
        "variant_id": request.variant_id,
        "charges_price": request.charges_price,
    }
    try:
        await ExShowRoomPrice.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: ExShowroomPrice | arguments: {variant_price_request} | exception "
            f"encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_rto/")
async def add_rto(rto_request: RtoRequest) -> AddResponse:
    logger.info(f"create object request for class: Rto | arguments: {rto_request}")
    new_dict = {
        "name": rto_request.rto_name,
        "state_id": rto_request.state_id,
        "city_id": rto_request.city_id,
        "is_active": rto_request.is_active,
    }
    try:
        await Rto.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Rto | arguments: {rto_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_rto_zone/")
async def add_rto_zone(rto_request: RtoZoneRequest) -> AddResponse:
    logger.info(f"create object request for class: Zone | arguments: {rto_request}")
    new_dict = {
        "zone_name": rto_request.zone_name,
        "is_active": rto_request.is_active
    }
    try:
        await RtoZone.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: zone | arguments: {rto_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_region/")
async def add_region(region_request: RegionRequest) -> AddResponse:
    logger.info(f"create object request for class: Region | arguments: {region_request}")
    new_dict = {
        "name": region_request.region_name,
        "rto_zone_id": region_request.rto_zone_id,
        "is_active": region_request.is_active
    }
    try:
        await Region.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Region | arguments: {region_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_city_cluster/")
async def add_city_cluster(city_cluster_request: CityClusterRequest) -> AddResponse:
    logger.info(f"create object request for class: City Cluster | arguments: {city_cluster_request}")
    request = city_cluster_request.dict()
    city_cluster_code = city_cluster_request.name.replace(" ", "_").lower()
    city_id_list = request["city_id"]
    filter_city_obj = await sqldb.execute(select(CityCluster).where(CityCluster.code == city_cluster_code))
    filter_city_clusters = filter_city_obj.scalars().first()
    # for filter_city_cluster in filter_city_clusters:
    if filter_city_clusters:
        city_cluster_id = filter_city_clusters.id
    else:
        create_cluster = await CityCluster.create(
            **{"name": request["name"], "code": city_cluster_code, "is_active": request["is_active"]})
        city_cluster_id = create_cluster.id
    try:
        for city_id in city_id_list:
            request["city_id"] = city_id
            await CityClusterCityMapping.create(
                **{"city_cluster_id": city_cluster_id, "city_id": city_id, "is_active": request["is_active"]})
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: City Cluster | arguments: {city_cluster_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_rto_cluster/")
async def add_rto_cluster(rto_cluster_request: RtoClusterRequest) -> AddResponse:
    logger.info(f"create object request for class: Rto Cluster | arguments: {rto_cluster_request}")
    request = rto_cluster_request.dict()
    rto_cluster_code = rto_cluster_request.name.replace(" ", "_").lower()
    rto_id_list = request["rto_id"]
    filter_rto_obj = await sqldb.execute(select(RtoCluster).where(RtoCluster.code == rto_cluster_code))
    filter_rto_clusters = filter_rto_obj.scalars().first()
    if filter_rto_clusters:
        rto_cluster_id = filter_rto_clusters.id
    else:
        create_cluster = await RtoCluster.create(
            **{"name": request["name"], "code": rto_cluster_code, "is_active": request["is_active"]})
        rto_cluster_id = create_cluster.id
    try:
        for rto_id in rto_id_list:
            request["rto_id"] = rto_id
            await RtoClusterRtoMapping.create(
                **{"rto_cluster_id": rto_cluster_id, "rto_id": rto_id, "is_active": request["is_active"]})
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Rto Cluster | arguments: {rto_cluster_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_bank/")
async def add_bank(bank_request: BankRequest) -> AddResponse:
    logger.info(f"create object request for class: Bank | arguments: {bank_request}")
    new_dict = {
        "name": bank_request.name,
        "is_active": bank_request.is_active
    }
    try:
        await Bank.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Bank | arguments: {bank_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_financier/")
async def add_financier(financier_request: FinancierRequest) -> AddResponse:
    logger.info(f"create object request for class: Financier | arguments: {financier_request}")
    new_dict = {
        "name": financier_request.name,
        "is_active": financier_request.is_active
    }
    try:
        await Financier.create(**new_dict)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Financier | arguments: {financier_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_insurer/")
async def add_insurer(ic_request: IcUserInfoRequest) -> Dict[str, str]:
    logger.info(f"create object request for class: Insurer | arguments: {ic_request}")
    insurer_request = ic_request.ic_request.dict()
    user_info_request = ic_request.user_info_request.dict()
    insurer_code = insurer_request['name'].replace(" ", "_")
    registered_address = " | ".join(
        [insurer_request['ic_address_1'], insurer_request['ic_address_2'], insurer_request['ic_address_3']])
    insurer_request['registered_office_address'] = registered_address
    insurer_request['code'] = insurer_code.lower()
    user_info_request['insurer_code'] = insurer_code.lower()

    try:
        # await Insurer.create(**insurer_request)
        client = http3.AsyncClient()
        user_info_request.update({"password": USER_PASSWORD})
        user = await client.post(url=AUTH_REGISTER_URL, json=user_info_request)
        user_id_obj = user.json()
        insurer_request.update({"user_obj_id": user_id_obj['id']})
        await Insurer.create(**insurer_request)
        return {"msg": "Data is inserted"}
    except Exception as e:
        logger.exception(
            f"create object request for class: Insurer | arguments: {ic_request} | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_insurer_local_office/")
async def add_insurer_local_office(ic_local_office_request: InsurerLocalOfficeRequest) -> AddResponse:
    logger.info(f"create object request for class: Insurer Local Office | arguments: {ic_local_office_request}")
    request = ic_local_office_request.dict()
    try:
        await InsurerLocalOffice.create(**request)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: Insurer Local Office | arguments: {ic_local_office_request} | "
            f"exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.post("/add_ic_dealer_mapping/")
async def add_ic_dealer_mapping(ic_dealer_mapping_request: ICDealerMappingRequest) -> AddResponse:
    logger.info(f"create object request for class: insurer dealer mapping | arguments: {ic_dealer_mapping_request}")
    request = ic_dealer_mapping_request.dict()
    insurer_id_list = request["insurer_id"]
    try:
        for insurer_id in insurer_id_list:
            request["insurer_id"] = insurer_id
            await ICDealerMapping.create(**request)
        return AddResponse(msg="Data is inserted successfully")
    except Exception as e:
        logger.exception(
            f"create object request for class: insurer dealer mapping | arguments: {ic_dealer_mapping_request} | "
            f"exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Not able to create records")


@router.get("/ic_dealer_mapping_table/", response_model=Page[ICDealerMappingResponse])
async def ic_dealer_mapping_show_table():
    logger.info(f"get all request for class: InsurerDealerMapping")
    query = await ICDealerMapping.fetch_all()
    response = []
    try:
        for data in query:
            if data.insurer_id:
                insurer_obj = await Insurer.fetch(key=data.insurer_id)
                data.__dict__["insurer_name"] = insurer_obj.name
            if data.local_office_code:
                ic_local_office_obj = await InsurerLocalOffice.fetch(key=data.local_office_code)
                data.__dict__["local_office_code_name"] = ic_local_office_obj.local_office_code
            response.append(ICDealerMappingResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: InsurerDealerMapping | exception encounter {e}.")
        raise HTTPException(status_code=400, detail="Error while fetching all records")


@router.get("/state_table/", response_model=Page[StateTableResponse])
async def state_show_table():
    logger.info(f"get all request for class: state")
    query = await State.fetch_all()
    response = []
    try:
        for data in query:
            if data.region:
                region_obj = await Region.fetch(key=data.region)
                data.__dict__["region_name"] = region_obj.name
            response.append(StateTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: State | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/city_table/", response_model=Page[CityTableResponse])
async def city_show_table():
    logger.info(f"get all request for class: city")
    query = await City.fetch_all()
    response = []
    try:
        for data in query:
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data.__dict__['state_name'] = state_obj.name
            response.append(CityTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: city | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/pincode_table/", response_model=Page[PincodeTableResponse])
async def pincode_show_table():
    logger.info(f"get all request for class: pincode")
    query = await Pincode.fetch_all()
    response = []
    try:
        for data in query:
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data.__dict__['state_name'] = state_obj.name
            if data.city_id:
                city_obj = await City.fetch(key=data.city_id)
                data.__dict__['city_name'] = city_obj.name
            response.append(PincodeTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: pincode | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/rto_table/", response_model=Page[RtoTableResponse])
async def rto_show_table():
    logger.info(f"get all request for class: rto")
    query = await Rto.fetch_all()
    response = []
    try:
        for data in query:
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data.__dict__['state_name'] = state_obj.name
            if data.city_id:
                city_obj = await City.fetch(key=data.city_id)
                data.__dict__['city_name'] = city_obj.name
            response.append(RtoTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: rto | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/Vehicle_model_table/", response_model=Page[VehicleModelTableResponse])
async def vehicle_model_show_table():
    query = await VehicleModel.fetch_all()
    response = []
    try:
        for data in query:
            if data.oem_id:
                oem_obj = await Oem.fetch(key=data.oem_id)
                data.__dict__['oem_name'] = oem_obj.name
            response.append(VehicleModelTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: Model | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/variant_table/", response_model=Page[VehicleVariantTableResponse])
async def variant_show_table():
    logger.info(f"get all request for class: variant")
    query = await Variant.fetch_all()
    response = []
    try:
        for data in query:
            if data.fuel_type_id:
                fuel_obj = await FuelType.fetch(key=data.fuel_type_id)
                data.__dict__['fuel_name'] = fuel_obj.name
            if data.id:
                sub_variant_obj = await VehicleRepository.get_color_tone_for_variant_table(data.id)
                for item in sub_variant_obj:
                    data.__dict__['sub_variant_id'] = item.id
                    data.__dict__['color'] = item.color
                    data.__dict__['tone'] = item.tone
            model = await VehicleModel.fetch(key=data.model_id)
            data.__dict__['model_name'] = model.name
            oem = await Oem.fetch(key=model.oem_id)
            data.__dict__['oem_name'] = oem.name
            response.append(VehicleVariantTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: variant | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/variant_price_table/", response_model=Page[VehicleVariantPriceTableResponse])
async def variant_price_show_table():
    logger.info(f"get all request for class: cls")
    query = await ExShowRoomPrice.fetch_all()
    response = []
    try:
        for data in query:
            if data.variant_id:
                data.__dict__['ex_showroom_price_id'] = data.id
                variant_obj = await Variant.fetch(key=data.variant_id)
                model = await VehicleModel.fetch(key=variant_obj.model_id)
                data.__dict__['model_name'] = model.name
                data.__dict__['variant_name'] = variant_obj.name
                sub_variant_obj = await VehicleRepository.get_color_tone_for_variant_table(data.variant_id)
                for item in sub_variant_obj:
                    data.__dict__['color'] = item.color
                    data.__dict__['tone'] = item.tone
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data.__dict__['state_name'] = state_obj.name
            response.append(VehicleVariantPriceTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: Ex_showroom_price | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/rto_zone_table/", response_model=Page[RtoZoneTableResponse])
async def rto_zone_show_table():
    logger.info(f"get all request for class: zone")
    try:
        rto_zone_obj = await RtoZone.fetch_all()
        return paginate(
            [RtoZoneTableResponse(id=data.id, zone_name=data.zone_name, is_active=data.is_active)
             for data in rto_zone_obj])
    except Exception as e:
        logger.exception(f"Not able to get all records for class: zone | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/region_table/", response_model=Page[RegionTableResponse])
async def region_show_table():
    logger.info(f"get all request for class: region")
    query = await Region.fetch_all()
    response = []
    try:
        for data in query:
            if data.rto_zone_id:
                rto_zone_obj = await RtoZone.fetch(key=data.rto_zone_id)
                data.__dict__['rto_zone_id'] = data.rto_zone_id
                data.__dict__['rto_zone_name'] = rto_zone_obj.zone_name
            response.append(RegionTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: region | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/city_cluster_table/", response_model=Page[CityClusterTableResponse])
async def city_cluster_show_table():
    logger.info(f"get all request for class: city cluster")
    city_cluster_query = await CityClusterCityMapping.fetch_all(is_active=True)
    try:
        city_cluster_segregation = {}
        for city_cluster in city_cluster_query:
            if city_cluster_segregation.get(city_cluster.city_cluster_id) is None:
                city_cluster_segregation[city_cluster.city_cluster_id] = [city_cluster.city_id]
            else:
                city_cluster_segregation[city_cluster.city_cluster_id].append(city_cluster.city_id)

        response = []
        for city_cluster_id, city_ids in city_cluster_segregation.items():
            data = {}
            query = await sqldb.execute(select(CityCluster).where(CityCluster.id == city_cluster_id))
            city_cluster_data = query.scalars().first()
            cluster_obj = await CityCluster.fetch(key=city_cluster_id)
            data['city_cluster_id'] = city_cluster_id
            data['is_active'] = city_cluster_data.is_active
            data['city_cluster_name'] = cluster_obj.name
            data['cluster_cities'] = []
            for city_id in city_ids:
                city_obj = await City.fetch(key=city_id)
                data['cluster_cities'].append({"city_id": city_id, "city_name": city_obj.name,
                                               "city_status": city_obj.is_active})

            response.append(CityClusterTableResponse(**data))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: city cluster | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/rto_cluster_table/", response_model=Page[RtoClusterTableResponse])
async def rto_cluster_show_table():
    logger.info(f"get all request for class: cls")
    rto_cluster_query = await RtoClusterRtoMapping.fetch_all(is_active=True)
    try:
        rto_cluster_segregation = {}
        for rto_cluster in rto_cluster_query:
            if rto_cluster_segregation.get(rto_cluster.rto_cluster_id) is None:
                rto_cluster_segregation[rto_cluster.rto_cluster_id] = [rto_cluster.rto_id]
            else:
                rto_cluster_segregation[rto_cluster.rto_cluster_id].append(rto_cluster.rto_id)

        response = []
        for rto_cluster_id, rto_ids in rto_cluster_segregation.items():
            data = {}
            query = await sqldb.execute(select(RtoCluster).where(RtoCluster.id == rto_cluster_id))
            rto_cluster_data = query.scalars().first()
            cluster_obj = await RtoCluster.fetch(key=rto_cluster_id)
            data['rto_cluster_id'] = rto_cluster_id
            data['is_active'] = rto_cluster_data.is_active
            data['rto_cluster_name'] = cluster_obj.name
            data['cluster_rto'] = []
            for rto_id in rto_ids:
                rto_obj = await Rto.fetch(key=rto_id)
                data['cluster_rto'].append({"rto_id": rto_id, "rto_code": rto_obj.code,
                                            "rto_status": rto_obj.is_active})

            response.append(RtoClusterTableResponse(**data))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: rto cluster | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/insurer_table/", response_model=Page[InsurerTableResponse])
async def insurer_show_table():
    logger.info(f"get all request for class: insurer")
    query = await Insurer.fetch_all()
    response = []
    try:
        for data in query:
            if data.user_obj_id:
                user_details_url = f'{USER_DETAILS_URL}?user_id={data.user_obj_id}'
                user_details = await call_auth_api(user_details_url)
                user_data = user_details['user_details']
                data.__dict__['salutation'] = user_data["salutation"]
                data.__dict__['first_name'] = user_data["first_name"]
                data.__dict__['middle_name'] = user_data["middle_name"]
                data.__dict__['last_name'] = user_data["last_name"]
                data.__dict__['user_role_id'] = user_data["role_id"]
                data.__dict__['designation'] = user_data["designation"]
                data.__dict__['user_landline_no'] = user_data["landline_no"]
                data.__dict__['user_mobile_no'] = user_data["mobile_no"]
                data.__dict__['user_email'] = user_data["email"]
                data.__dict__['user_status'] = user_data["is_active"]
            response.append(InsurerTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: insurer | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/insurer_local_office_table/", response_model=Page[InsurerLocalOfficeTableResponse])
async def insurer_local_office_show_table():
    logger.info(f"get all request for class: insurer local office")
    query = await InsurerLocalOffice.fetch_all()
    response = []
    try:
        for data in query:
            if data.insurer_id:
                insurer_obj = await Insurer.fetch(key=data.insurer_id)
                data.__dict__["insurer_name"] = insurer_obj.name
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data.__dict__['dealer_state_name'] = state_obj.name
            if data.city_id:
                city_obj = await City.fetch(key=data.city_id)
                data.__dict__['dealer_city_name'] = city_obj.name
            response.append(InsurerLocalOfficeTableResponse(**data.__dict__))
        return paginate(response)
    except Exception as e:
        logger.exception(f"Not able to get all records for class: insurer local office | exception encounter {e}.")
        raise HTTPException(status_code=400, detail=f"Error while fetching all records")


@router.get("/financier_table/", response_model=Page[FinancierResponse])
async def financier_show_table():
    logger.info(f"get all request for class: financier")
    financier_obj = await Financier.fetch_all()
    return paginate(
        [FinancierResponse(id=financier.id, financier_name=financier.name, code=financier.code,
                           is_active=financier.is_active) for
         financier in financier_obj])


@router.get("/bank_table/", response_model=Page[BankResponse])
async def bank_show_table():
    logger.info(f"get all request for class: bank")
    bank_obj = await Bank.fetch_all()
    return paginate(
        [BankResponse(id=bank.id, bank_name=bank.name, code=bank.code, is_active=bank.is_active) for bank in bank_obj])


# for variant dropdown in variant price add new entry
@router.get("/get_variants_and_sub_variants/", response_model=List[SubVariantAndVariantResponse])
async def get_variants_and_sub_variant(model_id: int):
    variant_list = await VehicleRepository.get_variants_and_sub_variant(model_id)
    response = []
    for variant in variant_list:
        for sub_variant in variant:
            variant_obj = await Variant.fetch(key=sub_variant.variant_id)
            sub_variant.__dict__['variant_id'] = sub_variant.variant_id
            sub_variant.__dict__['variant_name'] = variant_obj.name
            response.append(SubVariantAndVariantResponse(**sub_variant.__dict__))
    return response


# TODO: Add dealer and get dealer API needs to be update for now these apis are not in use.
@router.post("/add_dealer/")
async def add_dealer(admin_dealer_request: AdminDealerRequest):
    dealer = await AdminRepository.add_dealer_details(admin_dealer_request)
    if not dealer:
        return "Error occur while inserting data."
    return DealerResponse(dealer_code=dealer['dealer'].dealer_code, message=dealer['message'])


@router.get("/get_dealer/", response_model=Page[DealerTableResponse])
async def get_dealer():
    logger.info(f"app.apis.version1.individual_db_entry.get_dealer")
    dealer = await Dealer.fetch_all()
    response = []
    try:
        for data in dealer:
            data_dict = data.__dict__
            workshop = await sqldb.execute(select(Workshop.code).filter(Workshop.dealer_id == data_dict['id']))
            workshop_code = workshop.scalars().all()
            data_dict['workshop_code'] = workshop_code if workshop_code else "N/A"
            if data.state_id:
                state_obj = await State.fetch(key=data.state_id)
                data_dict["state_name"] = state_obj.name
            if data.city_id:
                city_obj = await City.fetch(key=data.city_id)
                data_dict['city_name'] = city_obj.name
            response.append(DealerTableResponse(**data_dict))
        return paginate(response)
    except Exception as e:
        logger.exception(
            f"Not able to get all records for class: app.apis.version1.individual_db_entry.get_dealer | exception "
            f"encounter {e}.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while fetching all records")
