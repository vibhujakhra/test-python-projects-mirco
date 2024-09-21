from rb_utils.async_http_client import AsyncHttpClient

from settings import SERVICE_CREDENTIALS, ams_creds, PROXY_URL
from utils.exceptions import *

async def get_ams_pos_code(ams_code: str):

    """
    The get_ams_pos_code function is used to fetch the pos code of a user from AMS service.
        Args:
            user_details (dict): A dictionary containing the details of a particular user.

    :param cls: Define the class that is being used
    :param user_details: dict: Get the user details from the database
    :return: The pos_code for a given user
    """
    ams_service_url = SERVICE_CREDENTIALS["ams_service"]["dns"] + "/api/v1/fetch_profile_by_id/"
    ams_service_data = await AsyncHttpClient.post(
        url=ams_service_url,
        body={
            "user_id": ams_code
        },
        headers=ams_creds,
        proxy=PROXY_URL
    )
    try:
        pos_code = ams_service_data["pos_code"]
        return pos_code
    except Exception as e:
        raise GetAPIException(message=f"Pos Code not found for given {ams_code}",
                                name="app/utils/service.py/get_ams_pos_code/")