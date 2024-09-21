import logging
from fastapi import APIRouter, Query
from rb_utils.database import sqldb
from starlette.responses import JSONResponse
from app.models.insurer import *
from app.models.location import *
from app.models.vehicle_details import *
from app.schemas.admin_db_details import *
from app.models.financier import Bank, Financier
from app.services.vehicle import VehicleRepository
from sqlalchemy import select

logger = logging.getLogger('api')
router = APIRouter()


@router.get("/search_zone/", response_model=List[RtoZoneRequest])
async def search_zone(zone_name: str):
    logger.info(f"search on class: zone | arguments: {zone_name}")
    query = await sqldb.execute(select(RtoZone).where(RtoZone.zone_name == zone_name))
    data = query.scalars().all()
    if data:
        return [RtoZoneRequest(zone_name=item.zone_name, is_active=item.is_active) for item in data]
    logger.exception("No data found related to search keyword for class zone")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_region/", response_model=List[SearchRegionResponse])
async def search_region(zone_id: int = None, region_name: str = None):
    logger.info(f"search on class: region | arguments: {zone_id} | {region_name}")
    response = []
    if region_name:
        query = select(Region).where(Region.name == region_name)

    elif zone_id:
        query = select(Region).where(Region.rto_zone_id == zone_id)
    else:
        query = select(Region).where(Region.name == region_name, Region.rto_zone_id == zone_id)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            zone_obj = await RtoZone.fetch(key=item.rto_zone_id)
            response.append(
                SearchRegionResponse(name=item.name, rto_zone_name=zone_obj.zone_name, is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class region")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_state/", response_model=List[SearchStateResponse])
async def search_region(region_id: int = None, state_name: str = None):
    logger.info(f"search on class: state | arguments: {region_id} | {state_name}")
    response = []
    if state_name:
        query = select(State).where(State.name == state_name)
    elif region_id:
        query = select(State).where(State.region == region_id)
    else:
        query = await sqldb.execute(select(State).where(State.region == region_id, State.name == state_name))
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            region_obj = await Region.fetch(key=item.region)
            response.append(SearchStateResponse(name=item.name, region_name=region_obj.name, is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class state")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_city/", response_model=List[SearchCityResponse])
async def search_city(state_id: int = None, city_name: str = None):
    logger.info(f"search on class: city | arguments: {state_id} | {city_name}")
    response = []
    if city_name:
        query = select(City).where(City.name == city_name)
    elif state_id:
        query = select(City).where(City.state_id == state_id)
    else:
        query = select(City).where(City.state_id == state_id, City.name == city_name)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            state_obj = await State.fetch(key=item.state_id)
            response.append(SearchCityResponse(state_name=state_obj.name, name=item.name, is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class city")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_pincode/", response_model=List[SearchPincodeResponse])
async def search_pincode(state_id: int = None, city_id: int = None, pincode: str = None):
    logger.info(f"search on class: pincode | arguments: {state_id} | {city_id} | {pincode}")
    response = []
    if pincode:
        query = select(Pincode).where(Pincode.name == pincode)
    elif state_id:
        query = select(Pincode).where(Pincode.state_id == state_id)
    elif city_id:
        query = select(Pincode).where(Pincode.city_id == city_id)
    else:
        query = select(Pincode).where(Pincode.state_id == state_id, Pincode.city_id == city_id, Pincode.name == pincode)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            state_obj = await State.fetch(key=item.state_id)
            city_obj = await City.fetch(key=item.city_id)
            response.append(SearchPincodeResponse(state_name=state_obj.name, city_name=city_obj.name, name=item.name,
                                                  is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class pincode")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_rto/", response_model=List[SearchRtoResponse])
async def search_rto(state_id: int = None, city_id: int = None, rto: str = None):
    logger.info(f"search on class: rto | arguments: {state_id} | {city_id} | {rto}")
    response = []
    if rto:
        query = select(Rto).where(Rto.name == rto)
    elif state_id:
        query = select(Rto).where(Rto.state_id == state_id)
    elif city_id:
        query = select(Rto).where(Rto.city_id == city_id)
    else:
        query = select(Rto).where(Rto.state_id == state_id, Rto.city_id == city_id, Rto.name == rto)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            state_obj = await State.fetch(key=item.state_id)
            city_obj = await City.fetch(key=item.city_id)
            response.append(SearchRtoResponse(state_name=state_obj.name, city_name=city_obj.name, name=item.name,
                                              code=item.code, is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class city rto")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.patch("/search_city_cluster/")
async def search_city_cluster(city_ids: List[int], cluster_id: int):
    logger.info(f"search on class: city cluster | arguments: {city_ids} | {cluster_id}")
    res = []
    for city_ids in city_ids:
        city_cluster_query = await sqldb.execute(
            select(CityClusterCityMapping).filter(CityClusterCityMapping.city_id == city_ids,
                                                  CityClusterCityMapping.city_cluster_id == cluster_id
                                                  ))
        res.append(city_cluster_query.scalars().first())

    if res:
        city_cluster_segregation = {}
        for city_cluster in res:
            if city_cluster_segregation.get(city_cluster.city_cluster_id) is None:
                city_cluster_segregation[city_cluster.city_cluster_id] = [city_cluster.city_id]
            else:
                city_cluster_segregation[city_cluster.city_cluster_id].append(city_cluster.city_id)

        response = []
        for city_cluster_id, city_ids in city_cluster_segregation.items():
            data = {}
            cluster_obj = await CityCluster.fetch(key=city_cluster_id)
            data['city_cluster_id'] = city_cluster_id
            data['city_cluster_name'] = cluster_obj.name
            data['cluster_cities'] = []
            for city_id in city_ids:
                city_obj = await City.fetch(key=city_id)
                data['cluster_cities'].append({"city_id": city_id, "city_name": city_obj.name})
            response.append(data)
        return response
    logger.exception("No data found related to search keyword for class city cluster")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_rto_cluster/", response_model=List[SearchRtoClusterResponse])
async def search_rto_cluster(state_id: int, city_id: int, rto_id: int, rto_cluster_name: str):
    logger.info(f"search on class: rto cluster | arguments: {state_id} | {city_id} | {rto_cluster_name}")
    query = await sqldb.execute(select(RtoCluster).where(RtoCluster.state_id == state_id,
                                                         RtoCluster.city_id == city_id,
                                                         RtoCluster.rto_id == rto_id,
                                                         RtoCluster.name == rto_cluster_name
                                                         ))
    data = query.scalars().all()
    if data:
        for item in data:
            state_obj = await State.fetch(key=item.state_id)
            city_obj = await City.fetch(key=item.city_id)
            rto_obj = await Rto.fetch(key=item.rto_id)
            return [SearchRtoClusterResponse(state_name=state_obj.name, city_name=city_obj.name, rto_name=rto_obj.name,
                                             name=item.name, is_active=item.is_active)]
    logger.exception("No data found related to search keyword for class rto cluster")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_vehicle_model/", response_model=List[SearchVehicleModelResponse])
async def search_vehicle_model(model_name: str):
    logger.info(f"search on class: model | arguments: {model_name}")
    query = await sqldb.execute(select(VehicleModel).where(VehicleModel.name == model_name))
    data = query.scalars().all()
    if data:
        for item in data:
            oem_obj = await Oem.fetch(key=item.oem_id)
            return [SearchVehicleModelResponse(name=item.name, oem_name=oem_obj.name, is_active=item.is_active)]
    logger.exception("No data found related to search keyword for class model ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_vehicle_variant/", response_model=List[SearchVehicleVariantResponse])
async def search_vehicle_variant(model_id: int = None, variant_name: str = None):
    logger.info(f"search on class: variant | arguments: {model_id} | {variant_name}")
    response = []
    if variant_name:
        query = select(Variant).where(Variant.name == variant_name)
    elif model_id:
        query = select(Variant).where(Variant.model_id == model_id)
    else:
        query = select(Variant).where(Variant.model_id == model_id, Variant.name == variant_name)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            model_obj = await VehicleModel.fetch(key=item.model_id)
            fuel_obj = await FuelType.fetch(key=item.fuel_type_id)
            oem_obj = await Oem.fetch(key=model_obj.oem_id)
            sub_variant_obj = await VehicleRepository.get_color_tone_for_variant_table(item.id)
            for items in sub_variant_obj:
                color = items.color
                tone = items.tone
                response.append(
                    SearchVehicleVariantResponse(oem_name=oem_obj.name, name=item.name, model_name=model_obj.name,
                                                 fuel_type_name=fuel_obj.name,
                                                 color=color, tone=tone,
                                                 cubic_capacity=item.cubic_capacity,
                                                 seating_capacity=item.seating_capacity, is_bifuel=item.is_bifuel,
                                                 is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class variant ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_vehicle_variant_price/", response_model=List[SearchVehicleVariantPriceResponse])
async def search_vehicle_variant_price(variant_id: int = None, state_id: int = None):
    logger.info(f"search on class: exshowroomprice | arguments: {variant_id} | {state_id}")
    response = []
    if variant_id:
        query = select(ExShowRoomPrice).where(ExShowRoomPrice.variant_id == variant_id)
    elif state_id:
        query = select(ExShowRoomPrice).where(ExShowRoomPrice.state_id == state_id)
    else:
        query = select(ExShowRoomPrice).where(ExShowRoomPrice.variant_id == variant_id,
                                              ExShowRoomPrice.state_id == state_id)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            variant_obj = await Variant.fetch(key=item.variant_id)
            state_obj = await State.fetch(key=item.state_id)
            response.append(SearchVehicleVariantPriceResponse(charges_price=item.charges_price,
                                                              exShowRoomPrice=item.exShowRoomPrice,
                                                              variant_name=variant_obj.name, state_name=state_obj.name))
        return response
    logger.exception("No data found related to search keyword for class exshowroomprice ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


# @router.get("/search_dealer_mapping/", response_model=List[SearchICDealerMappingRequest])
# async def search_dealer_mapping(insurer_id: int, dealer_name: str):
#     logger.info(f"search on class: insurer dealer mapping | arguments: {insurer_id} |  {dealer_name}")
#     query = await sqldb.execute(select(ICDealerMapping).where(ICDealerMapping.insurer_id == insurer_id,
#                                                               ICDealerMapping.dealer_name == dealer_name))
#     data = query.scalars().all()
#     if data:
#         for item in data:
#             insurer_obj = await Insurer.fetch(key=item.insurer_id)
#             local_office_obj = await InsurerLocalOffice.fetch(key=item.local_office_code)
#             return [SearchICDealerMappingRequest(
#                 insurer_name=insurer_obj.name,
#                 dealer_name=item.dealer_name,
#                 dealer_code=item.dealer_code,
#                 dealer_state=item.dealer_state,
#                 dealer_city=item.dealer_city,
#                 local_office_state=item.local_office_state,
#                 local_office_code=item.local_office_code,
#                 local_office_code_name=local_office_obj.local_office_code,
#                 payment_mode_code_new=item.payment_mode_code_new,
#                 payment_mode_code_renew=item.payment_mode_code_renew,
#                 is_active=item.is_active
#             )]
#     logger.exception("No data found related to search keyword for class insurer dealer mapping")
#     return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_dealer_mapping/", response_model=List[SearchICDealerMappingRequest])
async def search_dealer_mapping(insurer_id: int = None, dealer_name: str = None):
    logger.info(f"search on class: insurer dealer mapping | arguments: {insurer_id} |  {dealer_name}")
    response = []
    if dealer_name:
        query = select(ICDealerMapping).where(ICDealerMapping.dealer_name == dealer_name)
    elif insurer_id:
        query = select(ICDealerMapping).where(ICDealerMapping.insurer_id == insurer_id)
    else:
        query = select(ICDealerMapping).where(ICDealerMapping.insurer_id == insurer_id,
                                              ICDealerMapping.dealer_name == dealer_name)
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            insurer_obj = await Insurer.fetch(key=item.insurer_id)
            local_office_obj = await InsurerLocalOffice.fetch(key=item.local_office_code)
            response.append(SearchICDealerMappingRequest(
                insurer_name=insurer_obj.name,
                dealer_name=item.dealer_name,
                dealer_code=item.dealer_code,
                dealer_state=item.dealer_state,
                dealer_city=item.dealer_city,
                local_office_state=item.local_office_state,
                local_office_code=item.local_office_code,
                local_office_code_name=local_office_obj.local_office_code,
                payment_mode_code_new=item.payment_mode_code_new,
                payment_mode_code_renew=item.payment_mode_code_renew,
                is_active=item.is_active
            ))
        return response
    logger.exception("No data found related to search keyword for class insurer dealer mapping")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_ic_local_office/", response_model=List[SearchInsurerLocalOfficeResponse])
async def search_ic_local_office(insurer_id: int = None, local_office_code: str = None, state_id: int = None):
    logger.info(f"search on class: insurer local office | arguments: {insurer_id} | {local_office_code} | {state_id}")
    response = []
    if local_office_code:
        query = select(InsurerLocalOffice).where(InsurerLocalOffice.local_office_code == local_office_code)
    elif insurer_id:
        query = select(InsurerLocalOffice).where(InsurerLocalOffice.insurer_id == insurer_id)
    elif state_id:
        query = select(InsurerLocalOffice).where(InsurerLocalOffice.dealer_state_id == state_id)
    else:
        query = select(InsurerLocalOffice).where(InsurerLocalOffice.insurer_id == insurer_id,
                                                 InsurerLocalOffice.local_office_code == local_office_code,
                                                 InsurerLocalOffice.dealer_state_id == state_id,
                                                 )
    query_session = await sqldb.execute(query)
    data = query_session.scalars().all()
    if data:
        for item in data:
            state_obj = await State.fetch(key=item.dealer_state_id)
            city_obj = await City.fetch(key=item.dealer_city_id)
            insurer_obj = await Insurer.fetch(key=item.insurer_id)
            response.append(
                SearchInsurerLocalOfficeResponse(dealer_state_name=state_obj.name, dealer_city_name=city_obj.name,
                                                 insurer_name=insurer_obj.name,
                                                 local_office_code=item.local_office_code,
                                                 address_1=item.address_1, is_active=item.is_active))
        return response
    logger.exception("No data found related to search keyword for class insurer local office ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_bank/", response_model=List[SearchBankResponse])
async def search_bank(bank_name: str = Query(min_length=3, max_length=100)):
    logger.info(f"search on class: bank | arguments: {bank_name}")
    bank = await Bank.smart_search_by_name(name=bank_name.lower())
    if bank:
        return [SearchBankResponse(id=item.id, bank_name=item.name, is_active=item.is_active) for item in bank]
    logger.exception("No data found related to search keyword for class bank ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})


@router.get("/search_financier/", response_model=List[SearchFinancierResponse])
async def search_financier(financier_name: str = Query(min_length=3, max_length=100)):
    logger.info(f"search on class: financier | arguments: {financier_name}")
    financier = await Financier.smart_search_by_name(name=financier_name.lower())
    if financier:
        return [SearchFinancierResponse(id=item.id, financier_name=item.name, is_active=item.is_active) for item in
                financier]
    logger.exception("No data found related to search keyword for class bank ")
    return JSONResponse({"error_msg": "No data found related to search keyword"})
