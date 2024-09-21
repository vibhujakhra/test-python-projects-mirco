import datetime
import logging
from typing import Dict, Any, List, Union

from rb_utils.database import sqldb
from sqlalchemy import select
from sqlalchemy.future import select

from app.models.policy_details import ODTPConditions, CurrentDateConditions, NewVehicleCoverMapping, \
    PolicyTypeVehicleCoverMapping, InsurerVehicleCoverMapping
from app.models.policy_details import PolicyType, VehicleCover
from app.models.vehicle_details import VehicleModel, Oem
from app.schemas.policy_details import VehicleCoverByIdResponse, VehicleCoverResponse
from app.utils.exceptions import *
from app.utils.helper import str_to_datetime


class PolicyDetailRepository:

    @classmethod
    async def get_vehicle_cover(cls, vehicle_cover_request):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(PolicyTypeVehicleCoverMapping).filter(PolicyTypeVehicleCoverMapping.is_active.is_(True))
            if vehicle_cover_request.previous_policy_type_id == 3:
                query = query.filter(
                    PolicyTypeVehicleCoverMapping.prev_policy_type_id == vehicle_cover_request.previous_policy_type_id)
            if vehicle_cover_request.policy_type_id:
                query = query.filter(
                    PolicyTypeVehicleCoverMapping.policy_type_id == vehicle_cover_request.policy_type_id)
            if vehicle_cover_request.vehicle_class_id:
                query = query.filter(
                    PolicyTypeVehicleCoverMapping.vehicle_class_id == vehicle_cover_request.vehicle_class_id)
            if vehicle_cover_request.vehicle_type_id:
                query = query.filter(
                    PolicyTypeVehicleCoverMapping.vehicle_type_id == vehicle_cover_request.vehicle_type_id)

            vehicle_cover_session = await sqldb.execute(query)
            vehicle_cover = vehicle_cover_session.scalars().all()
            if not vehicle_cover:
                raise Exception
            return vehicle_cover
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_vehicle_cover_details(cls, vehicle_cover_request):
        response_list = []
        response = await PolicyDetailRepository.get_vehicle_cover(vehicle_cover_request)
        for item in response:
            vehicle_cover = await VehicleCover.fetch(key=item.vehicle_cover_id)
            response_list.append(VehicleCoverResponse(id=item.id, name=vehicle_cover.name,
                                                      policy_type_id=item.policy_type_id,
                                                      vehicle_class_id=item.vehicle_class_id,
                                                      vehicle_type_id=item.vehicle_type_id,
                                                      od_tenure=vehicle_cover.od_tenure,
                                                      tp_tenure=vehicle_cover.tp_tenure))
        return response_list

    @classmethod
    async def get_vehicle_cover_by_id(cls, vehicle_cover_id: int, insurer_code: str = None) -> VehicleCoverByIdResponse:
        policy_type_vehicle_cover_by_id = await PolicyTypeVehicleCoverMapping.fetch(key=vehicle_cover_id)
        vehicle_cover_data = await VehicleCover.fetch(key=policy_type_vehicle_cover_by_id.vehicle_cover_id)
        vehicle_cover_response = {
            "id": vehicle_cover_data.id,
            "name": vehicle_cover_data.name,
            "policy_type_id": policy_type_vehicle_cover_by_id.policy_type_id,
            "vehicle_class_id": policy_type_vehicle_cover_by_id.vehicle_class_id,
            "vehicle_type_id": policy_type_vehicle_cover_by_id.vehicle_type_id,
            "od_tenure": vehicle_cover_data.od_tenure,
            "tp_tenure": vehicle_cover_data.tp_tenure
        }
        if insurer_code:
            insurer_vehicle_cover = select(InsurerVehicleCoverMapping).filter(
                InsurerVehicleCoverMapping.is_active.is_(True),
                InsurerVehicleCoverMapping.policy_type_vehicle_cover_id == vehicle_cover_id,
                InsurerVehicleCoverMapping.insurer_code == insurer_code)
            insurer_vehicle_cover_session = await sqldb.execute(insurer_vehicle_cover)
            insurer_vehicle_cover_obj = insurer_vehicle_cover_session.scalars().first()
            vehicle_cover_response.update({"full_name": insurer_vehicle_cover_obj.full_name,
                                           "insurer_code": insurer_vehicle_cover_obj.insurer_code,
                                           "uin": insurer_vehicle_cover_obj.uin})
        return VehicleCoverByIdResponse(**vehicle_cover_response)

    @classmethod
    async def get_policy_type_by_id(cls, policy_type_id: int):
        logger = logging.getLogger("db.models.base.get_by_id")
        try:
            query = select(PolicyType).where(PolicyType.id == policy_type_id).order_by("name")
            policy_type_id = await sqldb.execute(query)
            policy = policy_type_id.scalars().first()
            policy_dict = {
                "policy": policy
            }

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

        return policy_dict

    @classmethod
    async def get_new_vehicle_cover(cls, previous_vehicle_cover_id: int, od_expiry_date: str = None,
                                    tp_expiry_date: str = None):
        logger = logging.getLogger("services.policy_details.vehicle_cover")
        try:
            vehicle_cover_list: List[Dict[str, Any]] = []
            vehicle_cover_query = select(NewVehicleCoverMapping.policy_type_vehicle_cover_mapping_id).filter(
                NewVehicleCoverMapping.is_active.is_(True))
            policy_type_vehicle_cover = await PolicyTypeVehicleCoverMapping.fetch(key=previous_vehicle_cover_id)
            if od_expiry_date and tp_expiry_date:
                own_damage_expiry_date = str_to_datetime(od_expiry_date)
                third_party_expiry_date = str_to_datetime(tp_expiry_date)
                current_date = datetime.datetime.now().date()
                if NewVehicleCoverMapping.is_od_expired and NewVehicleCoverMapping.is_tp_expired:
                    vehicle_cover = await VehicleCover.fetch(key=policy_type_vehicle_cover.vehicle_cover_id)
                    if vehicle_cover.od_tenure:
                        own_damage_start_date = str_to_datetime(od_expiry_date) - datetime.timedelta(days=364)
                        for year in range(own_damage_expiry_date.year, (third_party_expiry_date.year) + 1):
                            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                                own_damage_start_date = own_damage_start_date + datetime.timedelta(days=1)

                    if vehicle_cover.od_tenure == 1 and vehicle_cover.tp_tenure == 0:
                        if (own_damage_expiry_date - third_party_expiry_date).days > 1 and current_date < own_damage_expiry_date:
                            vehicle_cover_query = vehicle_cover_query. \
                                where(
                                NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_GT_ONE.name,
                                NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                NewVehicleCoverMapping.current_date_conditions == CurrentDateConditions.CURRENT_DATE_LT_OD_EXPIRY)
                        elif (current_date > own_damage_expiry_date) and (own_damage_expiry_date - third_party_expiry_date).days > 1:
                            vehicle_cover_query = vehicle_cover_query. \
                                    where(
                                    NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_GT_ONE.name,
                                    NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                    NewVehicleCoverMapping.current_date_conditions == CurrentDateConditions.CURRENT_DATE_GT_OD_EXPIRY)
                        elif (own_damage_expiry_date - third_party_expiry_date).days == 0:
                            vehicle_cover_query = vehicle_cover_query. \
                                where(
                                NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_ZERO.name,
                                NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)
                        elif (own_damage_expiry_date - third_party_expiry_date).days == 1:
                            vehicle_cover_query = vehicle_cover_query. \
                                where(
                                NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_ONE.name,
                                NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)

                        elif (own_damage_expiry_date - third_party_expiry_date).days < 0:
                            if (own_damage_expiry_date - third_party_expiry_date).days == -1 or (
                                    own_damage_expiry_date and third_party_expiry_date) < current_date or (
                                    own_damage_expiry_date < current_date and third_party_expiry_date == current_date):
                                vehicle_cover_query = vehicle_cover_query. \
                                    where(
                                    NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_LT_ZERO.name,
                                    NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                    NewVehicleCoverMapping.current_date_conditions == None)
                            elif current_date < max(own_damage_expiry_date, third_party_expiry_date):
                                if ((own_damage_expiry_date - third_party_expiry_date).days == -1):
                                    vehicle_cover_query = vehicle_cover_query. \
                                        where(
                                        NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_MINUS_ONE.name,
                                        NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                        NewVehicleCoverMapping.current_date_conditions == CurrentDateConditions.CURRENT_DATE_LT_OD_EXPIRY_AND_TP_EXPIRY)
                                elif ((own_damage_expiry_date - third_party_expiry_date).days < -1) and (
                                        (own_damage_expiry_date - third_party_expiry_date).days > -1830):
                                    vehicle_cover_query = vehicle_cover_query. \
                                        where(
                                        NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_LT_MINUS_ONE.name,
                                        NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                        NewVehicleCoverMapping.current_date_conditions == CurrentDateConditions.CURRENT_DATE_LT_OD_EXPIRY_AND_TP_EXPIRY)
                                else:
                                    raise Exception
                            elif (current_date > own_damage_expiry_date) and (current_date < third_party_expiry_date):
                                vehicle_cover_query = vehicle_cover_query. \
                                    where(
                                    NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_MINUS_ONE.name,
                                    NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id,
                                    NewVehicleCoverMapping.current_date_conditions == CurrentDateConditions.CURRENT_DATE_LT_TP_EXPIRY_AND_GT_OD_EXPIRY)
                            else:
                                raise Exception
                        else:
                            raise Exception

                    elif (732 >= abs((own_damage_expiry_date - third_party_expiry_date).days)) and (
                            abs((own_damage_expiry_date - third_party_expiry_date).days) >= 730):
                        vehicle_cover_query = vehicle_cover_query. \
                            where(
                            NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_THREE.
                            name,
                            NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)

                    elif (1462 >= abs((own_damage_expiry_date - third_party_expiry_date).days)) and (
                            abs((own_damage_expiry_date - third_party_expiry_date).days) >= 1460):
                        vehicle_cover_query = vehicle_cover_query. \
                            where(
                            NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_DIFF_TP_EXPIRY_EQ_FIVE.
                            name,
                            NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)

                    elif (own_damage_expiry_date == third_party_expiry_date):
                        vehicle_cover_query = vehicle_cover_query. \
                            where(
                            NewVehicleCoverMapping.od_tp_condition == ODTPConditions.OD_EXPIRY_EQ_TP_EXPIRY.
                            name,
                            NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)


                    else:
                        raise Exception
                else:
                    raise Exception

            elif od_expiry_date:
                vehicle_cover_query = vehicle_cover_query. \
                    where(NewVehicleCoverMapping.od_tp_condition == ODTPConditions.STANDALONE_OD.name,
                          NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)

            else:
                vehicle_cover_query = vehicle_cover_query. \
                    where(NewVehicleCoverMapping.od_tp_condition == ODTPConditions.STANDALONE_TP.name,
                          NewVehicleCoverMapping.old_vehicle_cover_id == policy_type_vehicle_cover.id)

            new_vehicle_cover_session = await sqldb.execute(vehicle_cover_query)
            new_vehicle_cover = new_vehicle_cover_session.scalars().all()
            for item in new_vehicle_cover:
                policy_type_vehicle_cover = await PolicyTypeVehicleCoverMapping.fetch(key=item)
                # it will give vehicle cover name mapped to the specific vehicle cover id
                vehicle_cover_name = select(VehicleCover.name).where(
                    VehicleCover.id == policy_type_vehicle_cover.vehicle_cover_id)
                vehicle_cover_session = await sqldb.execute(vehicle_cover_name)
                vehicle_cover = vehicle_cover_session.scalars().first()
                vehicle_cover_dict = {"id": item, "name": vehicle_cover}
                vehicle_cover_list.append(vehicle_cover_dict)

            if len(new_vehicle_cover) == 0:
                raise Exception
            return vehicle_cover_list

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise RecordNotFoundException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    async def get_oem_name(cls,vehicle_model_id: int):
        oem_id = (await sqldb.execute(select(VehicleModel.oem_id).where(VehicleModel.id==vehicle_model_id))).scalars().first()
        oem_name =  (await sqldb.execute(select(Oem.name).where(Oem.id==oem_id))).scalars().first()
        return oem_name