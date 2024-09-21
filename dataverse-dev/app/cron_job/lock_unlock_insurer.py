import asyncio

import logging
from fastapi import APIRouter
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from rb_utils.database import initiate_database
from sqlalchemy import select

from app.models.admin_details import Dealer
from app.models.insurer import ICDealerMapping, Insurer
from app.settings import SERVICE_CREDENTIALS
from app.settings import CONNECTION_CONFIG


logger = logging.getLogger('api')
router = APIRouter()
initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)
async def lock_unlock_insurer():
    insurer_codes = (await sqldb.execute(select(Insurer.code).where(Insurer.is_active == True))).scalars().all()
    logger.info("lock_and_unlock insurer as per dealer")
    try:
        for insurer_code in insurer_codes:
            service_url = SERVICE_CREDENTIALS["muneem"]['dns'] + f"/api/v1/get_delayed_payment_list/?insurer_code={insurer_code}"
            payment_detail = await AsyncHttpClient.get(url=service_url)
            insurer_id = (
                await sqldb.execute(select(Insurer.id).where(Insurer.code == insurer_code))).first().id
            for payment in payment_detail:
                dealer_id = (
                    await sqldb.execute(select(Dealer.id).where(Dealer.dealer_code == payment.get("dealer_code")))).first().id
                ic_dealer_id = (await sqldb.execute(select(ICDealerMapping.id).filter(ICDealerMapping.dealer_id == dealer_id,
                                                                                      ICDealerMapping.insurer_id == insurer_id))).first().id
                if (payment.get('transaction_count') >= 1 and payment.get('is_vb64_verified') == False):
                    update_value = {"is_12_days_delayed": True}
                    await ICDealerMapping.update(key=ic_dealer_id, **update_value)
                else:
                    update_value = {"is_12_days_delayed": False}
                    await ICDealerMapping.update(key=ic_dealer_id, **update_value)
    except Exception as e:
        logger.exception(f"Error occured in lock_unlock_insurer method | due to exception {e}")


if __name__ == '__main__':
	asyncio.run(lock_unlock_insurer())
