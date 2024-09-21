import logging
from typing import List, Dict, Any

from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.addons import Addon, Bundle, AddonBundle
from app.models.admin_details import Broker, DesignatedPerson, SalesManager
from app.models.coverage_details import GeoExtension, PaCover, VoluntaryDeductible, ncb, CPAWavierReason
from app.models.financier import Bank, Financier
from app.models.insurer import Insurer, ICDealerMapping, InsurerLocalOffice
from app.models.location import City, State, Pincode, Rto, RtoZone
from app.models.personal_details import Relation, Salutation
from app.models.policy_details import PolicyType, ProposerType, VehicleCover, AgreementType
from app.models.vehicle_details import VehicleClass, VehicleType, FuelType, VehicleModel, Variant, Oem, Dealer, \
    SubVariant
from app.schemas.coverage_details import VoluntaryDeductibleResponse, LastYearNCBResponse, NoClaimBonusResponse
from app.schemas.financier import BankResponse
from app.schemas.insurer import BrokerResponse, InsurerResponse, DesignatedPersonResponse, SalesManagerResponse
from app.schemas.location import RtoResponse, RtoZoneSummaryResponse, StateResponse
from app.schemas.policy_details import PolicyTypeResponse, VehicleCoverByIdResponse, VehicleCoverResponse, \
    PaCoverResponse, DealerResponse
from app.schemas.vehicle import PolicySummaryResponse, VariantSummaryResponse, ModelSummaryResponse, SubVariantResponse, \
    OemResponse, VehicleClassSchema
from app.services.policy_details import PolicyDetailRepository
from app.settings import USER_DETAILS_URL
from app.utils.exceptions import *
from app.utils.service import call_auth_api


class AddonDetailRepository:
    model_dict = {
        "oem_id": Oem,
        "oem_code": Oem,
        "appointee_relation_id": Relation,
        "nominee_relation_id": Relation,
        "salutation_id": Salutation,
        "variant_id": Variant,
        "vehicle_model_id": VehicleModel,
        "proposer_type_id": ProposerType,
        "city_id": City,
        "fuel_type_id": FuelType,
        "ncb_carry_forward_id": ncb,
        "last_year_ncb_id": ncb,
        "pincode_id": Pincode,
        "vehicle_cover_id": VehicleCover,
        "state_id": State,
        "bank_id": Bank,
        "broker_id": Broker,
        "insurer_code": Insurer,
        "policy_type_id": PolicyType,
        "vehicle_type_id": VehicleType,
        "rto_location_id": Rto,
        "voluntary_deductible_id": VoluntaryDeductible,
        "prev_od_insurer_code": Insurer,
        "prev_tp_insurer_code": Insurer,
        "cpa_waiver_reason_id": CPAWavierReason,
        "geo_extension_id": GeoExtension,
        "prev_vehicle_cover_id": VehicleCover,
        "rto_zone_id": RtoZone,
        "sub_variant_id": SubVariant,
        "vehicle_class_id": VehicleClass,
        "pa_paid_driver_id": PaCover,
        "pa_unnamed_passenger_id": PaCover,
        "financier_id": Financier,
        "agreement_type_id": AgreementType,
        "hypothecation_city_id": City,
        "dealer_code": Dealer,
        "designated_person_code": DesignatedPerson,
        "sales_manager_code": SalesManager,
    }

    schema_dict = {
        "variant": VariantSummaryResponse,
        "sub_variant": SubVariantResponse,
        "broker": BrokerResponse,
        "insurer": InsurerResponse,
        "vehicle_cover": VehicleCoverByIdResponse,
        "prev_vehicle_cover": VehicleCoverResponse,
        "voluntary_deductible": VoluntaryDeductibleResponse,
        "rto_location": RtoResponse,
        "policy_type": PolicyTypeResponse,
        "prev_od_insurer": InsurerResponse,
        "prev_tp_insurer": InsurerResponse,
        "rto_zone": RtoZoneSummaryResponse,
        "vehicle_model": ModelSummaryResponse,
        "pa_paid_driver": PaCoverResponse,
        "pa_unnamed_passenger": PaCoverResponse,
        "state": StateResponse,
        "oem": OemResponse,
        "dealer": DealerResponse,
        "designated_person": DesignatedPersonResponse,
        "sales_manager": SalesManagerResponse,
        "bank": BankResponse,
        "last_year_ncb": LastYearNCBResponse,
        "ncb_carry_forward": NoClaimBonusResponse,
        "vehicle_class": VehicleClassSchema
    }

    @classmethod
    async def get_insurer_bundles(cls, insurer_id: int) -> List[Bundle]:
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(Bundle).where(Bundle.insurer_id == int(insurer_id)).order_by("name")
            insurer_bundles = await sqldb.execute(query)
            return insurer_bundles.scalars().all()

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_addons_list(cls, bundle_id: int) -> List[Dict[str, Any]]:
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            response_list = []

            bundle_addons = select(AddonBundle.addon_id).where(AddonBundle.bundle_id == int(bundle_id))
            bundle_addons_session = await sqldb.execute(bundle_addons)
            bundle_addons_list = bundle_addons_session.scalars().all()

            addon = select(Addon).where(Addon.id.in_(bundle_addons_list)).order_by("name")
            addon_session = await sqldb.execute(addon)
            addons_list = addon_session.scalars().all()
            return [item.__dict__ for item in addons_list]

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_service_address(cls, user_details: dict, insurer_code: str):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            user_data = user_details['user_details']
            dealer_code = user_data['dealer_code']
            if not (dealer_code or user_details):
                servicing_office_address = ""
                return servicing_office_address
            else:
                dealer_obj = await sqldb.execute(select(Dealer).where(Dealer.dealer_code == dealer_code))
                dealer_data = dealer_obj.scalars().first()
                insurer_data = await Insurer.fetch_by_code(code=insurer_code)
                ic_dealer_mapping_obj = await sqldb.execute(
                    select(ICDealerMapping).where(ICDealerMapping.dealer_id == dealer_data.id,
                                                  ICDealerMapping.insurer_id == insurer_data.id))
                ic_dealer_mapping_data = ic_dealer_mapping_obj.scalars().first()
                local_office_data = await InsurerLocalOffice.fetch(key=ic_dealer_mapping_data.local_office_id)
                city_data = await City.fetch(key=local_office_data.city_id)
                state_data = await State.fetch(key=local_office_data.state_id)
                pincode_data = await Pincode.fetch(key=local_office_data.pincode_id)
                servicing_office_address = "  ".join([local_office_data.address_1,
                                                      local_office_data.address_2 or "",
                                                      local_office_data.address_3 or "",
                                                      city_data.name,
                                                      state_data.name, pincode_data.name])
                response_dict = {
                    "ic_gst_state_code": state_data.gst_code,
                    "ic_branch_name": " ".join(local_office_data.local_office_code.split(
                        "_")).capitalize() if local_office_data.local_office_code else "",
                    "ic_branch_code": local_office_data.local_office_code or "",
                    "ic_branch_address": servicing_office_address,
                    "gstin_number": local_office_data.gst_in,
                    "servicing_office_address": servicing_office_address,

                }
                return response_dict
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_pa_cover(cls, vehicle_type_id: int, vehicle_class_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(PaCover).where(PaCover.vehicle_type == vehicle_type_id,
                                          PaCover.vehicle_class_id == vehicle_class_id).order_by("id")
            vehicle_cover_session = await sqldb.execute(query)
            vehicle_cover = vehicle_cover_session.scalars().all()
            if not len(vehicle_cover):
                raise Exception

            return vehicle_cover

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")


    @classmethod
    async def policy_summary(cls, policy_summary_request):
        logger = logging.getLogger("db.services.addon_details.policy_summary")
        policy_dict = {}
        response_dict = {key: value for key, value in policy_summary_request.items() if value}
        for key, value in response_dict.items():
            if key == "geo_extension_ids":
                cities_name_list = await cls.get_geo_cities_list(value)
                policy_dict["geo_extension"] = cities_name_list
                continue
            if key == "vehicle_cover_id":
                policy_dict["vehicle_cover"] = await PolicyDetailRepository.get_vehicle_cover_by_id(
                    value, policy_summary_request.get('insurer_code'))
                continue
            if key == "prev_vehicle_cover_id":
                policy_dict["prev_vehicle_cover"] = await PolicyDetailRepository.get_vehicle_cover_by_id(
                    value)
                continue
            if key == "vehicle_model_id":
                policy_dict["oem_name"] = await PolicyDetailRepository.get_oem_name(
                    value)

            if isinstance(value, int):
                query = select(cls.model_dict.get(key)).where(cls.model_dict.get(key).id == value)
            else:
                if key == 'dealer_code':
                    query = select(cls.model_dict.get(key)).where(cls.model_dict.get(key).dealer_code == value)
                else:
                    query = select(cls.model_dict.get(key)).where(cls.model_dict.get(key).code == value)
            try:
                policy_summary_session = await sqldb.execute(query)
                model_detail = policy_summary_session.scalars().first()
            except Exception as e:
                logger.exception(f"Exception encounter {e} while fetching records.")
                raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching records.")

            policy_dict[key.replace("_id", "").replace("_code", "")] = model_detail
        return policy_dict

    @classmethod
    async def get_policy_details(cls, details, service_address=None, gstin_number=None):
        summary_details = {}
        response_dict = {key: value for key, value in details.items() if value}
        for key, value in response_dict.items():
            if key == "geo_extension" or key == "oem_name":
                summary_details.update({key: value})
                continue
            if key in cls.schema_dict:
                schema_class = cls.schema_dict.get(key)
                if key == 'insurer':
                    value.servicing_office_address = service_address
                    value.gstin_number = gstin_number
                validated_data = schema_class(**value.__dict__)
                summary_details.update({
                    key: validated_data
                })
            else:
                summary_details.update({key: PolicySummaryResponse(id=value.id, name=value.name)})

        return summary_details

    @classmethod
    async def get_geo_cities_list(cls, geo_extension_ids):
        temp_list = []
        for city_id in geo_extension_ids.split(","):
            extn_city_obj = await GeoExtension.fetch(key=city_id)
            temp_list.append(extn_city_obj.name)
        return ", ".join(temp_list)

    @classmethod
    async def get_user_details(cls, user_id: str):
        user_details_url = f'{USER_DETAILS_URL}?user_id={user_id}'
        user_details = await call_auth_api(user_details_url)
        return user_details
