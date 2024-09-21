import logging
from app.settings import SERVICE_CREDENTIALS
from rb_utils.async_http_client import AsyncHttpClient

from app.utils.exceptions import DealerCodeNotFound

logger = logging.getLogger('utils')


async def get_user_details(user_id: str):
    service_url = SERVICE_CREDENTIALS["auth"][
                      "dns"] + f"/api/v1/get_user_details/?user_id={user_id}"
    user_details = await AsyncHttpClient.get(url=service_url)
    try:
        user_details = user_details["user_details"]
        return user_details
    except Exception as e:
        logger.exception(f"Error occurred while fetching dealer_code")
        raise DealerCodeNotFound(message=f"Dealer code not found for given {user_id}")
