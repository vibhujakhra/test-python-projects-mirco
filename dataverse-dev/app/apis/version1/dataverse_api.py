from typing import Dict, Any, List, Union

from fastapi import APIRouter, Query, Depends, Request
from rb_utils.database import sqldb
from rb_utils.exception.exceptions import FetchDataException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from app.models.addons import Addon, Bundle, IMTMapping
from app.models.admin_details import Oem, Dealer
from app.models.coverage_details import GeoExtension, PaCover, VoluntaryDeductible, ncb, CPAWavierReason, AAIMembership
from app.models.financier import Bank, Financier, AccountType
from app.models.insurer import Insurer, UserRole, InsurerLocalOffice, ICDealerMapping
from app.models.location import City, State, Pincode, Rto, RtoZone, Region
from app.models.personal_details import Relation, Salutation, Designation
from app.models.policy_details import PolicyType, PolicyTypeVehicleCoverMapping, ProposerType, TransactionType, \
    AgreementType, VB64Type, VehicleCover
from app.models.vehicle_details import VehicleType, FuelType, VehicleModel, Variant, ClaimYear, ClaimCount, \
    PreviousPolicyType, NcbType, VehicleClass
from app.schemas.addons_details import BundleResponse, AddonUinResponse
from app.schemas.coverage_details import CPATenureResponse, CPAWavierResponse, GeoExtensionResponse, PaCoverResponse, \
    VoluntaryDeductibleResponse, NoClaimBonusResponse, AAIMembershipResponse, AccountTypeResponse, UserRoleResponse, \
    DesignationResponse
from app.schemas.financier import BankResponse, FinancierResponse
from app.schemas.insurer import DealerListResponse, DealerPersonResponse, InsurerResponse, SalesManagerResponse, \
    ICLocalOfficeResponse, DealerICMappingListResponse, ActiveInsurerResponse
from app.schemas.location import CityResponse, StateResponse, PincodeResponse, RtoResponse, RtoZoneResponse, \
    RegionResponse
from app.schemas.personal_detail import RelationResponse, SalutationResponse
from app.schemas.policy_details import PolicyTypeResponse, ProposerTypeResponse, TransactionTypeResponse, \
    AgreementTypeResponse, VB64TypeResponse, VehicleCoverResponse, VehicleCoverRequest, \
    NewVehicleCoverResponse, NcbTypeResponse, ClaimYearResponse, ClaimCountResponse, PolicySummaryRequest
from app.schemas.vehicle import VehicleModelResponse, VariantResponse, VehicleVariantResponse, VariantByIdResponse, \
    SubVariantResponse, PreviousPolicyTypeResponse, FuelTypeResponse, ExShowRoomPriceResponse, ModelResponse, \
    VehicleTypeResponse, VehicleClassResponse
from app.services.addons_details import AddonDetailRepository
from app.services.admin_details import AdminRepository
from app.services.location import LocationRepository
from app.services.policy_details import PolicyDetailRepository
from app.services.vehicle import VehicleRepository

router = APIRouter()
search_router = APIRouter()


@router.get("/policy_type/", response_model=List[PolicyTypeResponse])
async def get_policy_type():
    policy_type = await PolicyType.fetch_all(is_active=True)
    return [PolicyTypeResponse(id=policy.id, name=policy.name) for policy in policy_type]


@router.get("/proposer_type/", response_model=List[ProposerTypeResponse])
async def get_proposer_type():
    proposer_type = await ProposerType.fetch_all(is_active=True)
    return [ProposerTypeResponse(id=proposer.id, name=proposer.name) for proposer in proposer_type]


@router.get("/vehicle_cover/", response_model=List[VehicleCoverResponse])
async def get_vehicle_cover(vehicle_cover_request: VehicleCoverRequest = Depends()):
    return await PolicyDetailRepository.get_vehicle_cover_details(vehicle_cover_request)


@router.get("/vehicle_type/", response_model=List[VehicleTypeResponse])
async def get_vehicle_type(oem_code: str, vehicle_class_id: int):
    oem_obj = await Oem.fetch_by_code(code=oem_code)
    vehicle_type = await sqldb.execute(select(VehicleType).where(VehicleType.oem_id == oem_obj.id,
                                                                 VehicleType.vehicle_class_id == vehicle_class_id))
    data = vehicle_type.scalars().all()
    return [VehicleTypeResponse(oem_code=oem_code, **item.__dict__) for item in data]


@router.get("/vehicle_cover_by_id/")
async def get_vehicle_cover(vehicle_cover_id: int, insurer_code: str = None):
    return await PolicyDetailRepository.get_vehicle_cover_by_id(vehicle_cover_id=vehicle_cover_id,
                                                                insurer_code=insurer_code)


@router.get("/cpa_tenure/", response_model=CPATenureResponse)
async def get_cpa_tenure(vehicle_cover_id: int):
    policy_type_vehicle_cover = await PolicyTypeVehicleCoverMapping.fetch(key=vehicle_cover_id)
    response = await VehicleCover.fetch(key=policy_type_vehicle_cover.vehicle_cover_id)
    tenure_list = [max(response.od_tenure, response.tp_tenure)]
    return CPATenureResponse(tenure=tenure_list)


@router.get("/{oem_code}/get_models/", response_model=List[VehicleModelResponse])
async def get_models(oem_code: str, vehicle_type_id: int, vehicle_class_id: int):
    oem_obj = await Oem.fetch_by_code(code=oem_code)
    vehicle_model = await sqldb.execute(select(VehicleModel).where(VehicleModel.oem_id == oem_obj.id,
                                                                   VehicleModel.vehicle_class_id == vehicle_class_id,
                                                                   VehicleModel.vehicle_type_id == vehicle_type_id))
    response = vehicle_model.scalars().all()
    return [VehicleModelResponse(oem_code=oem_code, **item.__dict__) for item in response]


@router.get("/{oem_code}/{model_id}/get_variants/")
async def get_vehicle_variant(model_id: int, oem_code: str = None):
    oem_obj = await Oem.fetch_by_code(code=oem_code)
    model_variants = await VehicleRepository.get_vehicle_variant(oem_id=oem_obj.id, model_id=model_id)
    return [VehicleVariantResponse(**item.__dict__) for item in model_variants]


@router.get("/exshowroom_price/", response_model=List[ExShowRoomPriceResponse])
async def get_exshowroom_price(subvariant_id: int):
    exshowroom_price = await VehicleRepository.get_exshowroom_price(subvariant_id)
    return [ExShowRoomPriceResponse(id=item.id, sub_variant_id=subvariant_id, city=item.city,
                                    exShowRoomPrice=item.exShowRoomPrice) for item in exshowroom_price]


@router.get("/fuel_type/", response_model=List[FuelTypeResponse])
async def get_fuel_type():
    fuel_type = await FuelType.fetch_all(is_active=True)
    return [FuelTypeResponse(id=fuel.id, name=fuel.name) for fuel in fuel_type]


@router.get("/city/", response_model=List[CityResponse])
async def get_cities(state_id: int = None):
    city = select(City).where(City.is_active.is_(True))
    if state_id:
        city = city.where(City.state_id == state_id)
    city_session = await sqldb.execute(city)
    city_list = city_session.scalars().all()
    return [CityResponse(id=city.id, name=city.name) for city in city_list]


@router.get("/states/")
async def get_states(state_id: int = None, state_code: str = None) -> Union[List[StateResponse], Dict]:
    if state_id:
        state_obj = await State.fetch(key=state_id)
        return state_obj.__dict__
    if state_code:
        state_obj = await State.fetch_by_code(code=state_code)
        return state_obj.__dict__
    state_list = await State.fetch_all(is_active=True)
    return [StateResponse(id=state.id, name=state.name) for state in state_list]


@router.get("/region/", response_model=List[RegionResponse])
async def get_region():
    region_list = await Region.fetch_all(is_active=True)
    return [RegionResponse(id=region.id, name=region.name) for region in region_list]


@router.get("/get_models/", response_model=List[ModelResponse])
async def get_models():
    model_list = await VehicleModel.fetch_all(is_active=True)
    return [ModelResponse(id=model.id, name=model.name) for model in model_list]


@router.get("/get_variants/", response_model=List[VariantResponse])
async def get_variants(model_id: int = None):
    variant = select(Variant).where(Variant.is_active.is_(True))
    if model_id:
        variant = variant.where(Variant.model_id == model_id)
    variant_session = await sqldb.execute(variant)
    variant_list = variant_session.scalars().all()
    return [VariantResponse(id=variant.id, name=variant.name) for variant in variant_list]


@router.get("/rto_zone/", response_model=List[RtoZoneResponse])
async def get_rto_zone():
    rto_zone = await RtoZone.fetch_all(is_active=True)
    return [RtoZoneResponse(id=state.id, zone_name=state.zone_name) for state in rto_zone]


@router.get("/rto_location/", response_model=List[RtoResponse])
async def get_rto_location(state_id: int = None):
    rto = select(Rto).where(Rto.is_active.is_(True))
    if state_id:
        rto = select(Rto).where(Rto.state_id == state_id, Rto.is_active.is_(True))
    rto_session = await sqldb.execute(rto)
    rto_list = rto_session.scalars().all()
    return [RtoResponse(id=item.id, name=item.name, city_id=item.city_id, code=item.code, rto_zone_id=item.rto_zone_id)
            for item in rto_list]


@router.get("/pincode/", response_model=List[PincodeResponse])
async def get_pincode(city_id: int = None):
    pincode = select(Pincode).where(Pincode.is_active.is_(True))
    if city_id:
        pincode = pincode.where(Pincode.city_id == city_id)
    pincode_session = await sqldb.execute(pincode)
    pincode_list = pincode_session.scalars().all()
    return [PincodeResponse(id=item.id, name=item.name, city_id=item.city_id, state_id=item.state_id) for
            item in pincode_list]


@search_router.get("/pincode/", response_model=List[PincodeResponse])
async def get_city_and_state(pincode: str = Query(min_length=3, max_length=10)):
    state_and_city = await LocationRepository.get_pincode(pincode)
    return [PincodeResponse(id=item.id, name=item.name, city_id=item.city_id, state_id=item.state_id) for
            item in state_and_city]


@search_router.get("/city/")
async def get_city_data(city_name: str = Query(min_length=3, max_length=10)) -> Union[List[CityResponse], JSONResponse]:
    try:
        query = await sqldb.execute(select(City).filter(func.lower(City.name).like(f"{city_name.lower()}%")))
        city = query.scalars().all()
        if city:
            return [CityResponse(id=item.id, name=item.name) for item in
                    city]
    except Exception as e:
        await sqldb.rollback()
    return JSONResponse(status_code=400, content="No data found related to search keyword.")


@router.get("/geographical_extension/", response_model=List[GeoExtensionResponse])
async def get_geographical_extension():
    geo_extension = await GeoExtension.fetch_all(is_active=True)
    return [GeoExtensionResponse(id=item.id, name=item.name) for item in geo_extension]


@router.get("/voluntary_deductible/", response_model=List[VoluntaryDeductibleResponse])
async def get_voluntary_deductible(id: int = None, vehicle_class_id: int = None, vehicle_type_id: int = None):
    if id:
        voluntary_deductible = await VoluntaryDeductible.fetch(key=id)
        return [VoluntaryDeductibleResponse(id=voluntary_deductible.id, text=voluntary_deductible.text,
                                            value=voluntary_deductible.value,
                                            vehicle_type_id=voluntary_deductible.vehicle_type_id,
                                            vehicle_class_id=voluntary_deductible.vehicle_class_id)]
    voluntary_deductible = await sqldb.execute(select(VoluntaryDeductible).where(
        VoluntaryDeductible.vehicle_class_id == vehicle_class_id,
        VoluntaryDeductible.vehicle_type_id == vehicle_type_id))
    data = voluntary_deductible.scalars().all()
    return [VoluntaryDeductibleResponse(id=item.id, text=item.text, value=item.value,
                                        vehicle_type_id=vehicle_type_id, vehicle_class_id=vehicle_class_id)
            for item in data]


@router.get("/sub_variant/", response_model=List[SubVariantResponse])
async def get_color_tone(variant_id: int):
    color_and_tone = await VehicleRepository.get_color_tone(variant_id)
    return [SubVariantResponse(id=item.id, tone=item.tone, color=item.color, variant_id=variant_id) for item in
            color_and_tone]


@router.get("/no_claim_bonus/", response_model=List[NoClaimBonusResponse])
async def get_ncb_carry_forward(id: int = None, policy_type_id: int = None, ncb_type_id: int = None):
    """
    The get_ncb_carry_forward function is used to get the NCB carry forward details.
        Args:
            id (int): The ID of the ncb_carry_forward object.
            policy_type_id (int): The ID of the policy type object.

    :param id: int: Fetch the details of a particular ncb
    :param policy_type_id: int: Get the ncb_list for a particular policy type
    :param ncb_type_id: int: Determine the type of ncb to be fetched
    :return: A list of noclaimbonusresponse objects
    """
    query = select(ncb).order_by("value")
    if id:
        query = query.where(ncb.id == id)
    if policy_type_id:
        query = query.where(ncb.policy_type_id == policy_type_id)
    if ncb_type_id:
        query = query.where(ncb.allowed_previous_policy.is_(True)) if ncb_type_id == 1 else query.where(
            ncb.allowed_reserving_letter.is_(True))
    ncb_list = await sqldb.execute(query)
    ncb_list = ncb_list.scalars().all()

    return [NoClaimBonusResponse(**item.__dict__) for item in ncb_list]


@router.get("/pa_cover/", response_model=List[PaCoverResponse])
async def get_pa_cover(id: int = None, vehicle_type_id: int = None, vehicle_class_id: int = None):
    if id:
        pa_cover = await PaCover.fetch(key=id)
        return [PaCoverResponse(id=pa_cover.id, text=pa_cover.text, value=pa_cover.value,
                                vehicle_type_id=pa_cover.vehicle_type, vehicle_class_id=pa_cover.vehicle_class_id)]
    pa_cover = await AddonDetailRepository.get_pa_cover(vehicle_type_id, vehicle_class_id)
    return [PaCoverResponse(id=item.id, text=item.text, value=item.value,
                            vehicle_type_id=item.vehicle_type, vehicle_class_id=item.vehicle_class_id)
            for item in pa_cover]


@router.get("/financier/", response_model=List[FinancierResponse])
async def get_financier():
    financier = await Financier.fetch_all(is_active=True)
    return [FinancierResponse(id=item.id, name=item.name) for item in financier]


@router.get("/bank/", response_model=List[BankResponse])
async def get_bank():
    bank = await Bank.fetch_all(is_active=True)
    return [BankResponse(id=item.id, name=item.name) for item in bank]


@router.get("/addons/")
async def get_addons() -> Dict[Any, Any]:
    addons = await Addon.fetch_all(is_active=True)
    return {item.id: item.name for item in addons}


@router.get("/insurer_list/", response_model=List[InsurerResponse])
async def get_insurer():
    insurer = await Insurer.fetch_all(is_active=True)
    return [InsurerResponse(id=item.id, name=item.name, code=item.code, insurer_logo=item.insurer_logo,
                            servicing_office_address=item.servicing_office_address,
                            is_renewal_integrated=item.is_renewal_integrated,
                            is_active=item.is_active) for item in insurer]


@router.get("/all_insurer_list/", response_model=List[InsurerResponse])
async def get_insurer():
    insurer = await Insurer.fetch_all()
    return [InsurerResponse(id=item.id, name=item.name, code=item.code, insurer_logo=item.insurer_logo,
                            is_renewal_integrated=item.is_renewal_integrated,
                            servicing_office_address=item.servicing_office_address,
                            is_active=item.is_active) for item in insurer]


@router.get("/insurer_bundle/", response_model=BundleResponse)
async def get_insurer_bundles(insurer_id: int):
    insurer_bundle = await AddonDetailRepository.get_insurer_bundles(insurer_id)
    addons_list = list({item.id for item in insurer_bundle})
    return BundleResponse(insurer_id=insurer_id, bundle_list=addons_list)


@router.get("/salutation_list/", response_model=List[SalutationResponse])
async def get_salutation():
    salutation = await Salutation.fetch_all(is_active=True)
    return [SalutationResponse(id=item.id, name=item.name, salutation_type=item.salutation_type) for item in
            salutation]


@router.get("/cpa_wavier_reason/", response_model=List[CPAWavierResponse])
async def get_cpa_wavier_reason():
    cpa_wavier_reason = await CPAWavierReason.fetch_all(is_active=True)
    return [CPAWavierResponse(id=item.id, text=item.name) for item in cpa_wavier_reason]


@router.get("/imt_numbers/")
async def get_imt_numbers() -> Dict[Any, Any]:
    imt_number = await IMTMapping.fetch_all(is_active=True)
    response = {}
    for item in imt_number:
        response[item.key_name] = item.imt_code
    return response


@router.get("/aai_membership/", response_model=List[AAIMembershipResponse])
async def get_aai_membership():
    aai_membership = await AAIMembership.fetch_all(is_active=True)
    return [AAIMembershipResponse(id=value.id, name=value.name) for value in aai_membership]


@router.get("/account_type/", response_model=List[AccountTypeResponse])
async def get_account_type():
    account_type = await AccountType.fetch_all(is_active=True)
    return [AccountTypeResponse(id=value.id, name=value.name) for value in account_type]


@router.get("/user_role/", response_model=List[UserRoleResponse])
async def get_user_role():
    user_role = await UserRole.fetch_all(is_active=True)
    return [UserRoleResponse(id=value.id, name=value.name) for value in user_role]


@router.get("/designation/", response_model=List[DesignationResponse])
async def get_designation():
    designation = await Designation.fetch_all(is_active=True)
    return [DesignationResponse(id=value.id, name=value.name) for value in designation]


@router.get("/get_variant_by_id/{variant_id}", response_model=VariantByIdResponse)
async def get_variant_by_id(variant_id: int):
    variant_details = await Variant.fetch(key=variant_id)
    fuel_type_code = await FuelType.fetch(key=variant_details.fuel_type_id)
    model_data = await VehicleModel.fetch(key=variant_details.model_id)
    response_dict = variant_details.__dict__
    response_dict["fuel_type_code"] = fuel_type_code.code
    response_dict["vehicle_class_id"] = model_data.vehicle_class_id
    response_dict["vehicle_type_id"] = model_data.vehicle_type_id
    return VariantByIdResponse(**response_dict)


@router.get("/dealer_person/", response_model=List[DealerPersonResponse])
async def get_designated_person(request: Request):
    user_details = await AddonDetailRepository.get_user_details(user_id=request.headers.get('x-user-id'))
    dealer = await sqldb.execute(
        select(Dealer.dealer_code).where(Dealer.dealer_code == user_details["user_details"]["dealer_code"]))
    dealer_code = dealer.scalars().first()
    designated_person_list = await AdminRepository.get_designated_person(dealer_code=dealer_code)
    return [DealerPersonResponse(id=designated_person.id, dealer_person_name=designated_person.designated_person_name,
                                 is_active=designated_person.is_active, code=designated_person.code)
            for
            designated_person in designated_person_list]


@router.get("/sales_manager/", response_model=List[SalesManagerResponse])
async def get_sales_manager(request: Request):
    user_details = await AddonDetailRepository.get_user_details(user_id=request.headers.get('x-user-id'))
    dealer = await sqldb.execute(
        select(Dealer.dealer_code).where(Dealer.dealer_code == user_details["user_details"]["dealer_code"]))
    dealer_code = dealer.scalars().first()
    sales_manager_list = await AdminRepository.get_sales_manager(dealer_code=dealer_code)
    return [
        SalesManagerResponse(id=sales_manager.id, sales_manager_name=sales_manager.sales_manager_name,
                             is_active=sales_manager.is_active, code=sales_manager.code)
        for
        sales_manager in sales_manager_list]


@router.get("/local_office_code/", response_model=List[ICLocalOfficeResponse])
async def local_office_code():
    ic_local_offices = await InsurerLocalOffice.fetch_all(is_active=True)
    return [ICLocalOfficeResponse(**ic_local_office.__dict__)
            for ic_local_office in ic_local_offices]


@router.get("/relation/", response_model=List[RelationResponse])
async def get_relation():
    relation = await Relation.fetch_all(is_active=True)
    return [RelationResponse(id=item.id, name=item.name) for item in relation]


@router.get("/bundle_addons/")
async def get_bundles_addons(addon_bundle_id: int = None):
    bundle_and_addons_dict = {}
    bundles_list = []

    bundle_addon_response = select(Bundle).where(Bundle.is_active.is_(True))
    if addon_bundle_id:
        bundle_addon_response = bundle_addon_response.where(Bundle.id == addon_bundle_id)

    bundle_addon_response = await sqldb.execute(bundle_addon_response)
    bundle_addon_response = bundle_addon_response.scalars().all()

    for items in bundle_addon_response:
        ic_obj = await Insurer.fetch(key=items.insurer_id)
        bundles_response = {"id": items.id, "name": items.name, "insurer_code": ic_obj.code}
        addons_list = await AddonDetailRepository.get_addons_list(bundles_response.get("id"))
        bundles_response["addons_list"] = addons_list
        bundles_list.append(bundles_response)

    bundle_and_addons_dict["bundle_list"] = bundles_list
    return bundle_and_addons_dict


@router.get("/previous_policy_type/", response_model=List[PreviousPolicyTypeResponse])
async def get_prev_policy_type():
    prev_policy_type = await PreviousPolicyType.fetch_all(is_active=True)
    return [PreviousPolicyTypeResponse(id=prev_policy.id, name=prev_policy.name) for prev_policy in prev_policy_type]


@router.get("/ncb_type/", response_model=List[NcbTypeResponse])
async def ncb_type():
    ncb_type_list = await NcbType.fetch_all(is_active=True)
    return [NcbTypeResponse(id=ncb_type_obj.id, name=ncb_type_obj.name) for ncb_type_obj in ncb_type_list]


@router.get("/claim_year/", response_model=List[ClaimYearResponse])
async def claim_year(vehicle_cover_id: int):
    policy_type_vehicle_cover = await PolicyTypeVehicleCoverMapping.fetch(key=vehicle_cover_id)
    vehicle_cover_list = await VehicleCover.fetch(key=policy_type_vehicle_cover.vehicle_cover_id)
    max_value = max(vehicle_cover_list.od_tenure, vehicle_cover_list.tp_tenure)
    claim_year_list = [year for year in range(0, max_value + 1)]

    claim_year_query = select(ClaimYear).where(ClaimYear.id.in_(claim_year_list))
    claim_year_session = await sqldb.execute(claim_year_query)
    claim_year_session_list = claim_year_session.scalars().all()

    return [ClaimYearResponse(id=claim_year_session.id, name=claim_year_session.name) for claim_year_session in
            claim_year_session_list]


@router.get("/claim_count/", response_model=List[ClaimCountResponse])
async def claim_count():
    claim_count_objs = await ClaimCount.fetch_all(is_active=True)
    return [ClaimCountResponse(id=claim.id, count=claim.count) for claim in claim_count_objs]


@router.get("/renewal_vehicle_cover/")
async def vehicle_cover(previous_vehicle_cover: int, od_expiry_date: str = None, tp_expiry_date: str = None) -> \
        List[NewVehicleCoverResponse]:
    vehicle_cover_obj = await PolicyDetailRepository.get_new_vehicle_cover(previous_vehicle_cover, od_expiry_date,
                                                                           tp_expiry_date)

    vehicle = [NewVehicleCoverResponse(id=item.get("id"), name=item.get("name")) for item in vehicle_cover_obj]
    return vehicle


@router.get("/transaction_type/", response_model=List[TransactionTypeResponse])
async def get_transaction_type():
    transaction_type = await TransactionType.fetch_all(is_active=True)
    return [TransactionTypeResponse(
        id=transaction.id, name=transaction.name, code=transaction.code) for transaction in transaction_type]


@router.get("/agreement_type/", response_model=List[AgreementTypeResponse])
async def get_agreement_type():
    agreement_type = await AgreementType.fetch_all(is_active=True)
    return [AgreementTypeResponse(id=agreement.id, name=agreement.name) for agreement in agreement_type]


@router.get("/vb64_type/", response_model=List[VB64TypeResponse])
async def get_vb64_type():
    vb64_types = await VB64Type.fetch_all(is_active=True)
    return [VB64TypeResponse(id=vb64_type.id, name=vb64_type.name) for vb64_type in vb64_types]


@router.get("/policy_summary/")
async def get_policy_summary_detail(policy_summary_request: PolicySummaryRequest = Depends()):
    policy_summary_request = policy_summary_request.dict()
    user_details = policy_summary_request.pop("user_details", None)
    summary_dict = await AddonDetailRepository.policy_summary(policy_summary_request)
    service_address = {}
    policy_summary_response = {}
    if policy_summary_request.get("insurer_code") and user_details:
        user_details = await AddonDetailRepository.get_user_details(user_id=user_details)
        dealer_query = select(Dealer).where(Dealer.dealer_code == user_details["user_details"]["dealer_code"])
        dealer_query = await sqldb.execute(dealer_query)
        dealer_query = dealer_query.scalars().first()
        dealer_state = await State.fetch(key=dealer_query.state_id)
        dealer_city = await City.fetch(key=dealer_query.city_id)
        dealer_query = dealer_query.__dict__
        dealer_query["dealer_state"] = dealer_state.name
        dealer_query["dealer_city"] = dealer_city.name

        service_address = await AddonDetailRepository.get_service_address(
            user_details=user_details,
            insurer_code=policy_summary_request["insurer_code"]
        )
        policy_summary_response.update({"dealer_details": dealer_query, "ic_location_detail": service_address})

    policy_summary_detail = await AddonDetailRepository.get_policy_details(summary_dict, service_address.get(
        "servicing_office_address"), service_address.get("gstin_number"))
    policy_summary_response.update(policy_summary_detail)
    return policy_summary_response


@router.get("/get_vehicle_class/", response_model=List[VehicleClassResponse])
async def get_vehicle_class(oem_code: str, vehicle_class_id: int = None):
    oem_obj = await Oem.fetch_by_code(code=oem_code)
    vehicle_class_obj = select(VehicleClass).where(VehicleClass.oem_id == oem_obj.id,
                                                   VehicleClass.is_active.is_(True))
    if vehicle_class_id:
        vehicle_class_obj = vehicle_class_obj.where(VehicleClass.id == vehicle_class_id)

    vehicle_class = await sqldb.execute(vehicle_class_obj)
    data = vehicle_class.scalars().all()
    return [VehicleClassResponse(oem_code=oem_code, **vehicle_class.__dict__) for vehicle_class in data]


@router.get("/get_addons_uin/", response_model=List[AddonUinResponse])
async def get_addons_uin(insurer_code: str = None):
    addon_obj = select(Addon).where(Addon.is_active.is_(True))
    if insurer_code:
        addon_obj = select(Addon).where(Addon.insurer_code == insurer_code,
                                        Addon.is_active.is_(True))
    addon_response = await sqldb.execute(addon_obj)
    addons = addon_response.scalars().all()
    return [AddonUinResponse(**addon.__dict__) for addon in addons]


@router.get("/get_dealer_list/", response_model=List[DealerListResponse])
async def get_dealer_list(dealer_code: str = None):
    """
    The get_dealer_list function returns a list of dealers.

    :param dealer_code: str: Filter the response by a specific dealer code
    :return: A list of dealerlistresponse objects
    """
    dealers_obj = select(Dealer).where(Dealer.is_active.is_(True))
    if dealer_code:
        dealers_obj = dealers_obj.where(Dealer.dealer_code == dealer_code)
    dealers_response = await sqldb.execute(dealers_obj)
    data = dealers_response.scalars().all()
    return [DealerListResponse(**dealer.__dict__) for dealer in
            data]


@router.get("/get_rto_ids/")
async def get_rto_ids(rto_zone_id: int):
    rto_ids = (await sqldb.execute(select(Rto.id).where(Rto.rto_zone_id == rto_zone_id))).scalars().all()
    return {"rto_ids": rto_ids}


@router.get("/get_city_ids/")
async def get_city_ids(state_id: int):
    city_ids = (await sqldb.execute(select(City.id).where(City.state_id == state_id))).scalars().all()
    return {"city_ids": city_ids}


@router.get("/get_reports_data/")
async def get_rtozone_by_rto_id(rto_id: int):
    rto = (await sqldb.execute(select(Rto).where(Rto.id == rto_id).options(
        selectinload(Rto.rto_zone),
        selectinload(Rto.city),
        selectinload(Rto.state)))).scalars().first()
    return {
        "rto_zone": rto.rto_zone.zone_name,
        "city": rto.city.name,
        "state": rto.state.name,
    }


@router.post("/get_zone_list/")
async def get_rto_ids_list(rto_ids: list):
    rtos = (await sqldb.execute(select(Rto).where(Rto.id.in_(rto_ids)).options(
        selectinload(Rto.rto_zone),
        selectinload(Rto.city),
        selectinload(Rto.state)))).scalars().all()
    return [{rto.id: {"zone_name": rto.rto_zone.zone_name,
                      "city": rto.city.name,
                      "state": rto.state.name, } for rto in rtos}]


@router.get("/get_dealer_insurer_mapping_list/", response_model=DealerICMappingListResponse)
async def get_dealer_insurer_mapping_list(dealer_code: str):
    """
    The get_dealer_list function returns a list of all dealers and their associated insurer codes.
        If the dealer_code parameter is provided, only that dealer's information will be returned.

    :param dealer_code: str: Filter the response based on the dealer_code
    :return: A list of DealerICMappingListResponse objects
    """

    dealers_id = (await sqldb.execute(select(Dealer.id).where(Dealer.dealer_code == dealer_code))).first().id

    allowed_ic_dealer_list = (await sqldb.execute(
        select(
            ICDealerMapping.insurer_id,
        ).where(
            ICDealerMapping.is_active.is_(True),
            ICDealerMapping.is_12_days_delayed.is_not(True),
            ICDealerMapping.dealer_id == dealers_id
        )
    )).scalars().all()

    allowed_insurer_codes = (await sqldb.execute(
        select(
            Insurer.code,
            Insurer.insurer_logo,
            Insurer.is_renewal_integrated,
        ).where(
            Insurer.is_active.is_(True),
            Insurer.id.in_(allowed_ic_dealer_list)
        )
    )).all()

    return DealerICMappingListResponse(
        dealer_code=dealer_code,
        allowed_insurer_list=[ActiveInsurerResponse(
            code=insurer.code, insurer_logo=insurer.insurer_logo,
            is_renewal_integrated=insurer.is_renewal_integrated
        ) for insurer in allowed_insurer_codes]
    )


@router.get("/get_feed_file_insurers/")
async def get_feed_file_insurers() -> List[str]:
    """
    The get_feed_file_insurers function returns a list of insurer codes for insurers that have requested feed files.

    :return: A list of insurer codes that have requested a feed file
    :doc-author: Trelent
    """

    try:
        feed_file_insurer_codes = (await sqldb.execute(
            select(
                Insurer.code,
            ).where(
                Insurer.is_feedfile_requested.is_(True),
            )
        )).all()
        feed_file_insurer_codes = [insurer_code for (insurer_code,) in feed_file_insurer_codes]
        return feed_file_insurer_codes
    except Exception as e:
        await sqldb.rollback()
        raise FetchDataException(message=f"Error occurred while fetching record, exception encounter {e}.")


@router.get("/get_insurer_local_office/")
async def get_insurer_local_office(dealer_id: int, insurer_id: int):
    ic_dealer_mapping_id = (await sqldb.execute(
        select(ICDealerMapping.id).where(ICDealerMapping.insurer_id == insurer_id,
                                         ICDealerMapping.dealer_id == dealer_id))).scalars().first()
    local_office = (await sqldb.execute(
        select(InsurerLocalOffice).where(InsurerLocalOffice.id == ic_dealer_mapping_id).options(
            selectinload(InsurerLocalOffice.state), selectinload(InsurerLocalOffice.city),
            selectinload(InsurerLocalOffice.pincode)))).scalars().first()
    return f"{local_office.city.name}, {local_office.state.name} {local_office.pincode.name}"
