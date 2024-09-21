import logging
import os

import emails
import jinja2
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from sqlalchemy import select
from emails.store import LazyHTTPFile
from app.models.communication import Templates, CommunicationRequest, ChannelType, StatusType
from app.schemas.communication import BaseCommunicationRequest
from app.settings import KALEYRA_URL, KALEYRA_SENDER_ID, KALEYRA_API_KEY, EMAIL_CONFIGURATION, PROXY_URL

current_directory = os.getcwd()
logger = logging.getLogger('consumer')


class Communicator:

    @classmethod
    async def send_email(cls, communication_data: BaseCommunicationRequest):
        try:
            template_query = select(Templates).where(Templates.template_slug == communication_data.template_slug)
            template_obj = await sqldb.execute(template_query)
            (template_obj,) = template_obj.one()
            html_str = template_obj.email_template
            environment = jinja2.Environment()
            template = environment.from_string(html_str)
            message_data = template.render(**communication_data.template_format_kwargs)
            attachment_url = communication_data.attachment
            email_kwargs = {
                "subject": communication_data.subject,
                "mail_from": EMAIL_CONFIGURATION['from'],
                "html": message_data
            }
            # Prepare the email
            if attachment_url:
                attachment_file = LazyHTTPFile(uri=attachment_url)
                email_kwargs["attachments"] = [attachment_file]

            message = emails.html(**email_kwargs)
            # Send the email
            response = message.send(
                to=communication_data.email,
                smtp={
                    "host": EMAIL_CONFIGURATION['server'],
                    "port": EMAIL_CONFIGURATION['port'],
                    "timeout": 5,
                    "user": EMAIL_CONFIGURATION['username'],
                    "password": EMAIL_CONFIGURATION['password'],
                    "tls": True
                },
            )
            await CommunicationRequest.create(**{
                "templates_id": template_obj.id,
                "raw_request": message_data,
                "raw_response": str(response.status_text),
                "channel": ChannelType.email,
                "status": StatusType.sent,
                "worker_id": "Worker_1"
            })
            return
        except Exception as e:
            logger.exception(f"Exception encounter {e} while sending email.")

    @classmethod
    async def send_sms(cls, communication_data: BaseCommunicationRequest):
        template_query = select(Templates).where(Templates.template_slug == communication_data.template_slug)
        template_obj = await sqldb.execute(template_query)
        (template_obj,) = template_obj.one()
        message = template_obj.sms_template.format(**communication_data.template_format_kwargs)

        formatted_url = KALEYRA_URL.format(KALEYRA_API_KEY=KALEYRA_API_KEY,
                                           message=message,
                                           mobile_no=communication_data.mobile,
                                           KALEYRA_SENDER_ID=KALEYRA_SENDER_ID,
                                           dlt_template_id=template_obj.dlt_template_id)

        response = await AsyncHttpClient.post(url=formatted_url, proxy=PROXY_URL)
        await CommunicationRequest.create(**{
            "templates_id": template_obj.id,
            "raw_request": str(formatted_url),
            "raw_response": str(response),
            "channel": ChannelType.sms,
            "worker_id": "Worker_1",
            "status": StatusType.sent
        })

        return

    @classmethod
    async def send_whatsapp(cls, communication_data: BaseCommunicationRequest):
        return
