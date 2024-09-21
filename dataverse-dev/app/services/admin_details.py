import logging
from typing import List

import http3
from rb_utils.database import sqldb
from sqlalchemy.future import select

from app.models.admin_details import Dealer, DesignatedPerson, SalesManager, Workshop, WorkshopBeneficiaryDetails
from app.models.vehicle_details import BusinessDetail
from app.schemas.admin_db_details import AdminDealerRequest
from app.services.addons_details import AddonDetailRepository
from app.settings import USER_PASSWORD, AUTH_REGISTER_URL
from app.utils.exceptions import DealerCodeAlreadyExistException, DatabaseException, WorkshopCodeAlreadyExistException, \
    UserAlreadyExistException

logger = logging.getLogger("Admin Repository")


class AdminRepository:

    @classmethod
    async def check_dealer_code_exist(cls, dealer_code: str) -> bool:
        query = await sqldb.execute(select(Dealer).filter(Dealer.dealer_code == dealer_code))
        if query.scalars().first():
            raise DealerCodeAlreadyExistException("app.services.admin_details.check_dealer_code",
                                                  f"Dealer code {dealer_code} already exist")
        else:
            return False

    @classmethod
    async def check_workshop_code_exist(cls, workshop_code: list) -> bool:
        query = await sqldb.execute(select(Workshop).filter(Workshop.code.in_(workshop_code)))
        if query.scalars().first():
            raise WorkshopCodeAlreadyExistException("app.services.admin_details.check_workshop_code",
                                                    f"Workshop code already exist")
        else:
            return False

    @classmethod
    async def call_auth_register_api(cls, user_request, dealer_code: str = None, workshop_code: str = None):
        logging.info("app.services.admin_db_details.call_auth_register_api")
        user_info_request = user_request.dict()
        client = http3.AsyncClient()
        user_info_request.update(
            {"password": USER_PASSWORD, "dealer_code": dealer_code, "workshop_code": workshop_code})
        try:
            return await client.post(url=AUTH_REGISTER_URL, json=user_info_request)
        except Exception as e:
            logger.exception(f"Exception encounter {e} while creating dealer record.")
            raise UserAlreadyExistException(logger.name,
                                            f"Exception encounter {e} while creating record in Auth service.")

    @classmethod
    async def get_workshop_beneficiary_details(cls, request_workshop: str, dealer_id: int):
        logging.info("app.services.admin_db_details.get_workshop_beneficiary_details")
        for workshop in request_workshop:
            if workshop.workshop:
                workshop_request = workshop.workshop.dict()
                workshop_request['dealer_id'] = dealer_id
                workshop_obj = await Workshop.create(**workshop_request)
            if workshop.workshop_beneficiary:
                workshop_beneficiary = workshop.workshop_beneficiary.dict()
                await WorkshopBeneficiaryDetails.create(**workshop_beneficiary)
            if workshop.workshop_user_info:
                await cls.call_auth_register_api(workshop.workshop_user_info, workshop_code=workshop_obj.code)
        return {"workshop": workshop_obj.id, "message": "Workshop information is successfully added."}

    @classmethod
    async def add_dealer_details(cls, request: AdminDealerRequest):
        logging.info("app.services.admin_db_details.add_dealer_details")
        try:
            workshop_code_list = [workshop.workshop.code for workshop in request.workshops]
            dealer_code_exist = await cls.check_dealer_code_exist(dealer_code=request.dealer.dealer_code)
            workshop_code_exist = await cls.check_workshop_code_exist(workshop_code=workshop_code_list)
            if not dealer_code_exist:
                dealer = await Dealer.create(**request.dealer.dict())
                if request.dealer_user_info:
                    await cls.call_auth_register_api(request.dealer_user_info, dealer_code=dealer.dealer_code)
            if not workshop_code_exist:
                await cls.get_workshop_beneficiary_details(request_workshop=request.workshops, dealer_id=dealer.id)
            if request.business_detail:
                business_detail_request = request.business_detail.dict()
                business_detail_request['dealer_id'] = dealer.id
                await BusinessDetail.create(**business_detail_request)
            return {"dealer": dealer, "message": "Data is inserted successfully!"}
        except Exception as e:
            logger.exception(f"Exception encounter {e} while creating dealer record.")
            raise DatabaseException(logger.name, f"Exception encounter {e} while creating dealer record.")

    @classmethod
    async def get_designated_person(cls, dealer_code: int) -> List:
        logging.info("app.services.admin_db_details.get_designated_person")
        dealer = await sqldb.execute(select(Dealer.id).where(Dealer.dealer_code == dealer_code))
        dealer_id = dealer.scalars().first()
        designated_person = await sqldb.execute(select(DesignatedPerson).where(DesignatedPerson.dealer_id == dealer_id,
                                                                               DesignatedPerson.is_active.is_(True)))
        return designated_person.scalars().all()

    @classmethod
    async def get_sales_manager(cls, dealer_code: int) -> List:
        logging.info("app.services.admin_db_details.get_sales_manager")
        dealer = await sqldb.execute(select(Dealer.id).where(Dealer.dealer_code == dealer_code))
        dealer_id = dealer.scalars().first()
        sales_manager = await sqldb.execute(
            select(SalesManager).where(SalesManager.dealer_id == dealer_id, SalesManager.is_active.is_(True)))
        return sales_manager.scalars().all()
