from fastapi import APIRouter

from app.schemas.policy_details import *
from app.schemas.vehicle import *
from app.services.policy_details import PolicyDetailRepository
from app.services.vehicle import VehicleRepository

router = APIRouter()


@router.get("/oem_code/", response_model=OemResponse)
async def get_oem(oem_id: int):
    response = {}
    oem = await VehicleRepository.get_oem(oem_id)
    response = OemResponse(id=oem.id, name=oem.name, code=oem.code)
    return response


@router.get("/policy_type_service/")
async def get_policy_type_by_id(policy_type_id: int):
    policy_type = await PolicyDetailRepository.get_policy_type_by_id(policy_type_id=policy_type_id)
    response = {}
    for key, value in policy_type.items():
        response.update({key: PolicyTypeResponse(id=value.id, name=value.name)})
    return response


@router.get("/model_detail/", response_model=ModelDetailResponse)
async def get_details(variant_code: str):
    detail = await VehicleRepository.get_details(variant_code)
    validated_data = ModelDetailResponse(id=detail.id, model_id=detail.model_id,
                                         fuel_type_id=detail.fuel_type_id).dict()

    response = {
        "id": validated_data.get("id"),
        "model_id": validated_data.get("model_id"),
        "fuel_type_id": validated_data.get("fuel_type_id")
    }
    return response
