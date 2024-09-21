import logging
from db.session import async_db_session

from fastapi import status, HTTPException

from sqlalchemy.future import select
from sqlalchemy import update

from schemas.user import MappedOemResponse
from db.models.rbac import User, UserMetaData, DealerDetails
from services.misp_service import get_ams_pos_code


class MispDpOnboarding:

    @classmethod
    async def insert_dp_data(cls, dataframe, session):
        """
        The insert_dp_data function takes a dataframe as input and inserts the records into the dealer table.
            The function returns a message indicating how many records were inserted successfully.

        :param dataframe: DataFrame: Pass the dataframe to the function
        :return: A dictionary with a message key and the number of records inserted as value
        """
        try:
            dealer_dict = dataframe.to_dict(orient='records')
            session.add_all([DealerDetails(**data) for data in dealer_dict])
            await session.commit()
            return {"message": f"{len(dataframe)} records inserted successfully in dealer table"}

        except Exception:
            await session.rollback()
            return {"status_code": status.HTTP_400_BAD_REQUEST}

    @classmethod
    async def mapped_oem_details(cls, mapped_details_request):

        """
        The mapped_oem_details function is used to map the oem with MISP.
            Args:
                mapped_details_request (MappedOemRequest): The request object containing the details of MISP and OEM.

        :param cls: Get the class object of the function
        :param mapped_details_request: Get the request parameters from the user
        :return: The mapped oem details
        """
        logger = logging.getLogger("misp_kyc_details.mapped_oem_details")
        try:
            key = None
            user_id = (await async_db_session.execute(select(User.id).filter(User.email == mapped_details_request.email))).scalars().first()
            if mapped_details_request.user_sub_type_id == 1:
                key = "misp_code"
            elif mapped_details_request.user_sub_type_id == 2:
                key = "designated_person_code"
            pos_code = await get_ams_pos_code(ams_code=(await async_db_session.execute(select(UserMetaData.ams_code).filter(UserMetaData.user_id == user_id))).scalars().first())
            await async_db_session.execute(
                update(UserMetaData).where(UserMetaData.user_id == str(user_id)).values(oem_code=mapped_details_request.oem_code, **{key:pos_code}))
            await async_db_session.commit()
            return MappedOemResponse(misp_email=mapped_details_request.email,
                                     message="Oem is mapped with the specified MISP")

        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching records.")
            await async_db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MAPPED_OEM_INSERTION_ERROR",
            )
