import logging

from rb_utils.database import sqldb
from sqlalchemy import select

from app.models.generate_policy import DocumentStatus, PolicyPDFStatus, Templates
from app.utils.exceptions import DatabaseConnectionException

logger = logging.getLogger("api")


class DocumentStatusServices:

    @classmethod
    async def create_document(cls, data: dict) -> DocumentStatus:

        """
        The create_document function creates a new document in the database.

        :param cls: Specify the class of the object to be created
        :param data: dict: Pass the data to be stored in the database
        :return: A documentstatus object
        """
        logger.info("Creating document in database")
        current_status = PolicyPDFStatus.REQUEST_RECEIVED.name
        data.update({"current_state": current_status})
        document = await DocumentStatus.create(**data)
        return document

    @classmethod
    async def update_document(cls, data: dict, obj: DocumentStatus) -> None:

        """
        The update_document function updates the document status of a given document.

        :param cls: Pass the class of the object being updated
        :param data: dict: Pass the data to be updated
        :param obj: DocumentStatus: Pass the object to be updated
        :return: None
        """
        await DocumentStatus.update(key=obj.id, **data)

    @classmethod
    async def get_document(cls, policy_uuid: str) -> DocumentStatus:

        """
        The get_document function is used to fetch a single document status record from the database.
            Args:
                policy_uuid (str): The unique identifier of the policy for which we want to retrieve the document status.

        :param cls: Refer to the class itself
        :param policy_uuid: str: Get the document status of a policy with that particular uuid
        :return: A documentstatus object
        """
        logger.info(f"fetching document for given policy uuid: {policy_uuid}")
        try:
            query = select(DocumentStatus).where(DocumentStatus.policy_uuid == policy_uuid)
            results = await sqldb.execute(query)
            (result,) = results.one()
            return result
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching all records.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} while fetching all records.")

    @classmethod
    def check_validations(cls, data: dict, transaction_id: str) -> dict:

        """
        The check_validations function is used to check if the data passed in has all the required keys.
            If any of the keys are missing, it will return a False status and an error message with which key was missing.

        :param cls: Pass the class object to the function
        :param data: dict: Pass the data to be validated
        :param transaction_id: str: Log the transaction_id in case of any error
        :return: A dict containing the status of validation and a list of messages
        """
        logger.info(f"Checking validations if data passed in has all the required keys for given transaction_id: {transaction_id}")
        keys = ['query_detail', 'proposal_detail', 'payment_detail', 'policy_detail']
        result_data = {
            "status": True,
            "message": []
        }

        for key in keys:
            if not data.get(key):
                logger.info(f"{key} data not found for transaction_id: {transaction_id}")
                result_data['message'].append(f"{key} data not found for transaction_id: {transaction_id}")
                result_data['status'] = False

        return result_data


class TemplateService:

    @classmethod
    async def get_template(cls, insurer: str, doctype_id: int) -> str:

        """
        The get_template function is used to fetch the template for a given insurer and doctype_id.
            Args:
                cls (str): The class name of the function.
                insurer (str): The code of the insurer whose template needs to be fetched.
                doctype_id (int): The id of the document type whose template needs to be fetched.

        :param cls: Make the function a class method
        :param insurer: str: Specify the insurer code
        :param doctype_id: int: Get the template for a particular document type
        :return: A template object
        """
        logger.info(f"Fetching template for insurer {insurer} and doctype {doctype_id}")
        try:
            query = select(Templates).where(Templates.insurer_code == insurer, Templates.doctype_id == doctype_id)
            results = await sqldb.execute(query)
            (result,) = results.one()
            return result
        except Exception as e:
            logger.exception(f"Exception encounter {e} while fetching the template.")
            raise DatabaseConnectionException(logger.name, f"Exception encounter {e} fetching the template.")
