import logging
from datetime import datetime

import jinja2
import pdfkit
from dateutil.relativedelta import relativedelta
from rb_utils.async_http_client import AsyncHttpClient

from app.repository.services import TemplateService
from app.settings import SERVICE_CREDENTIALS
from app.utils.exceptions import PDFGenerationException
from app.utils.services import save_to_s3_bucket

logger = logging.getLogger("api")

date_format = "%Y-%m-%d"


async def fetch_template(req, insurer: str) -> str:
    """
    The fetch_template function is a coroutine that fetches the template for the insurer code passed in.
        If it's a cancellation letter, we fetch doctype_id 3 (cancellation letter), otherwise we fetch doctype_id 4 (renewal).


    :param req: Get the insurer code from the request
    :param insurer: str: Get the correct template for each insurer
    :return: A string
    """
    logger.info(f"fetching template for insurer code {insurer}")
    if req.is_cancellation_letter:
        template = await TemplateService.get_template(insurer=insurer, doctype_id=3)
    else:
        template = await TemplateService.get_template(insurer=insurer, doctype_id=4)
    return template.html


def restructure_letter_data(context_payload):
    """
    The restructure_letter_data function takes in a context payload and returns a dictionary with the following keys:
        name, policy_number, cover_type, od_period, liability_period, model variant chassis no engine no address mobile number date.


    :param context_payload: Pass the data to the template
    :return: A dictionary with the following keys:
    """
    address = context_payload["proposal_obj"]["customer"]["address"]
    vehicle_cover = context_payload.get("vehicle_cover", {})
    city = context_payload.get("city", {})
    state = context_payload.get("state", {})
    pincode = context_payload.get("pincode", {})
    policy_obj = context_payload["policy_obj"]
    policy_issue_on = policy_obj.get("policy_start_date")
    policy_create_time = policy_obj.get("policy_create_time") if policy_obj.get("policy_create_time") else '00:00'

    own_damage_period_range, liability_period_range = "NA", "NA"
    if vehicle_cover.get("od_tenure"):
        od_period = vehicle_cover.get('od_tenure')
        own_damage_start = (datetime.strptime(policy_issue_on, date_format) + relativedelta(days=-1, years=od_period)).strftime(date_format)
        own_damage_period_range = f"{policy_issue_on}({policy_create_time}) To {own_damage_start}(MidNight)"

    if vehicle_cover.get("tp_tenure"):
        liability_period = vehicle_cover.get('tp_tenure')
        liability_period_start = (datetime.strptime(policy_issue_on, date_format) + relativedelta(days=-1, years=liability_period)).strftime(date_format)
        liability_period_range = f"{policy_issue_on}({policy_create_time}) To {liability_period_start}(MidNight)"

    cancellation_date = (
        datetime.strptime(context_payload["cancellation_obj"]["created_at"], "%Y-%m-%dT%H:%M:%S")).strftime("%d-%m-%Y")

    customer_city = city.get("name")
    customer_state = state.get("name")
    customer_pincode = pincode.get("name")
    customer_address = address.get('address_line_1')
    if address.get('address_line_2'):
        customer_address += f", {address.get('address_line_2')}"
    if address.get('landmark'):
        customer_address += f", {address.get('landmark')}"
    customer_address += (f"; City: {customer_city}; State: {customer_state}; Pincode: {customer_pincode}")
    salutation = context_payload.get("salutation", {}).get("name", "")
    insured_name = context_payload["cancellation_obj"][
            "insured_name"]
    return_dict = {
        "name": f"{salutation} {insured_name}",
        "policy_number": context_payload["policy_obj"]["policy_number"],
        "cover_type": vehicle_cover.get("name"),
        "od_period": own_damage_period_range,
        "liability_period": liability_period_range,
        "model": context_payload["policy_obj"]["model"],
        "variant": context_payload["policy_obj"]["variant"],
        "chassis_no": context_payload["proposal_obj"]["vehicle_details"]["chassis_number"],
        "engine_no": context_payload["proposal_obj"]["vehicle_details"]["engine_number"],
        "address": customer_address,
        "mobile_no": context_payload["proposal_obj"]["customer"]["phone"] or
                     context_payload["proposal_obj"]["customer"]["mobile"],
        "date": cancellation_date,
        "insurer_address": context_payload.get("insurer", {}).get("servicing_office_address"),
        "insurer_name": context_payload.get("insurer", {}).get("name"),
    }
    return return_dict


async def policy_summary_data(insurer_code: str, vehicle_cover_id: str, broker_id: str, pincode_id: str, city_id: str,
                              state_id: str, oem_id: str, user_details: str, salutation_id: str):
    """
    The policy_summary_data function is used to get the policy summary data for a given insurer, vehicle cover, broker, pincode and city.

    :param insurer_code: str: Specify the insurer code
    :param vehicle_cover_id: str: Identify the type of vehicle cover
    :param broker_id: str: Filter the data by broker
    :param pincode_id: str: Get the pincode id
    :param city_id: str: Filter the data based on city_id
    :param state_id: str: Get the state id
    :param oem_id: str: Get the data for a specific oem
    :return: The following data:
    """
    service_url = SERVICE_CREDENTIALS["dataverse"][
                      "dns"] + f"/api/v1/policy_summary?insurer_code={insurer_code}&vehicle_cover_id={vehicle_cover_id}&broker_id={broker_id}&pincode_id={pincode_id}&city_id={city_id}&state_id={state_id}&oem_id={oem_id}&user_details={user_details}&salutation_id={salutation_id}"
    return await AsyncHttpClient.get(url=service_url)


async def get_context(context_payload):
    """
    The get_context function is used to create the context data for the proposal.
        The function takes in a dictionary as an argument and returns a dictionary with additional keys.

        Args:
            context_payload (dict): A dictionary containing all of the information needed to create a proposal.

    :param context_payload: Get the data from the payload
    :return: The context payload which is then passed to the render function
    """
    logger.info(f"Fetching data from policy summary for given data: {context_payload}")
    insurer_code = context_payload['proposal_obj'].get('insurer_code')
    vehicle_cover_id = context_payload['proposal_obj'].get('vehicle_cover_id')
    broker_id = "1"
    oem_id = "1"
    pincode_id = context_payload["proposal_obj"]["customer"]["address"]["pincode_id"]
    city_id = context_payload["proposal_obj"]["customer"]["address"]["city_id"]
    state_id = context_payload["proposal_obj"]["customer"]["address"]["state_id"]
    salutation_id = context_payload["proposal_obj"]["customer"]["salutation"]
    user_id = context_payload["user_id"]
    context_payload.update(await policy_summary_data(insurer_code=insurer_code, vehicle_cover_id=vehicle_cover_id,
                                                     broker_id=broker_id, pincode_id=pincode_id, city_id=city_id,
                                                     state_id=state_id, oem_id=oem_id, user_details=user_id,
                                                     salutation_id=salutation_id))
    logger.info(f"context data created is {context_payload}")
    return context_payload


def restructure_certificate_data(context_payload):
    """
    The restructure_certificate_data function takes in a context payload and returns a dictionary with the following keys:
        policy_number, policy_period, od_period, liability_period, cpa_cover_period, insured name (insured name),
        insured address (insured address), gstin no. (gstin number), pan no. (pan number), cancellation no.,
        cancellation effective date(effective date of cancellation) ,cancellation reason(reason for cancelling the policy) ,refund in favour of(name to whom refund is made) ,manufacturer(manufacturer's name ),model(model

    :param context_payload: Pass the data to the function
    :return: A dictionary
    """
    vehicle_cover = context_payload.get("vehicle_cover", {})
    insurer = context_payload.get("insurer", {})
    broker = context_payload.get("broker", {})
    oem = context_payload.get("oem", {})
    proposal_obj = context_payload["proposal_obj"]
    cancellation_obj = context_payload["cancellation_obj"]
    policy_obj = context_payload["policy_obj"]
    policy_issue_on = policy_obj.get("policy_start_date")
    policy_create_time = policy_obj.get("policy_create_time") if policy_obj.get("policy_create_time") else '00:00'
    net_refund_premium = 0
    if cancellation_obj["od_premium"] and cancellation_obj["tp_premium"]:
        net_refund_premium = round(cancellation_obj["od_premium"] + cancellation_obj["tp_premium"], 2)
    igst = round(net_refund_premium * 0.18, 2)
    own_damage_period_range, liability_period_range, cpa_period_range = "NA", "NA", "NA"
    if vehicle_cover.get("od_tenure"):
        od_period = vehicle_cover.get('od_tenure')
        own_damage_start = (datetime.strptime(policy_issue_on, date_format) + relativedelta(days=-1, years=od_period)).strftime(date_format)
        own_damage_period_range = f"{policy_issue_on}({policy_create_time}) To {own_damage_start}(MidNight)"

    if vehicle_cover.get("tp_tenure"):
        liability_period = vehicle_cover.get('tp_tenure')
        liability_period_start = (datetime.strptime(policy_issue_on, date_format) + relativedelta(days=-1, years=liability_period)).strftime(date_format)
        liability_period_range = f"{policy_issue_on}({policy_create_time}) To {liability_period_start}(MidNight)"

    if proposal_obj.get("is_cpa", {}):
        cpa_period = proposal_obj.get('cpa_tenure_id')
        cpa_period_start = (datetime.strptime(policy_issue_on, date_format) + relativedelta(days=-1, years=cpa_period)).strftime(date_format)
        cpa_period_range = f"{policy_issue_on}({policy_create_time}) To {cpa_period_start}(MidNight)"

    broker_validity = datetime.strptime(broker.get("validity"), date_format)
    broker_validity = datetime.strftime(broker_validity, "%d-%m-%Y")

    address = context_payload["proposal_obj"]["customer"]["address"]
    city = context_payload.get("city", {})
    state = context_payload.get("state", {})
    pincode = context_payload.get("pincode", {})

    customer_city = city.get("name")
    customer_state = state.get("name")
    customer_pincode = pincode.get("name")
    customer_address = address.get('address_line_1')
    if address.get('address_line_2'):
        customer_address += f", {address.get('address_line_2')}"
    if address.get('landmark'):
        customer_address += f", {address.get('landmark')}"
    customer_address += (f"; City: {customer_city}; State: {customer_state}; Pincode: {customer_pincode}")

    response_dict = {
        "policy_number": cancellation_obj["policy_number"],
        "policy_period": policy_obj.get("policy_start_date", {}) + "To" + policy_obj.get("policy_end_date", {}),
        "od_period": own_damage_period_range,
        "liability_period": liability_period_range,
        "cpa_cover_period": cpa_period_range,
        "insured_name": context_payload.get("salutation", {}).get("name") + " " + cancellation_obj["insured_name"],
        "insured_address": customer_address,
        "gstin_no": proposal_obj["customer"]["gstin"] if proposal_obj["customer"].get("gstin",
                                                                                      {}) else 'NA',
        "pan_no": proposal_obj["customer"]["pan_number"],
        "cancellation_no": cancellation_obj["cancellation_number"],
        "cancellation_effective_date": cancellation_obj["effective_date"] or "NA",
        "cancellation_reason": cancellation_obj["cancellation_reason"] or "NA",
        "refund_in_favour_of": cancellation_obj["refund_in_favour_of_name"],
        "manufacturer": oem.get("name"),
        "model": cancellation_obj["model"],
        "chassis_no": cancellation_obj["chassis_number"],
        "engine_no": cancellation_obj["engine_number"],
        "registration_no": cancellation_obj["registration_number"],
        "net_refund_premium": net_refund_premium,
        "igst": igst,
        "total_refund_premium": cancellation_obj["total_refundable_premium"],
        "refund_mode": cancellation_obj["refund_method"],
        "pending_refund_message": cancellation_obj["pending_refund_message"],
        "cheque_no": cancellation_obj["cheque_number"],
        "refund_date": cancellation_obj["refund_date"],
        "insurer_registered_address": insurer.get("registered_office_address"),
        "irda_registration_no": insurer.get("irda_registration_no"),
        "insurer_gstin_no": insurer.get("gstin_number"),
        "insurer_cin_no": insurer.get("cin"),
        "insurer_pan_no": insurer.get("pan_number"),
        "broker_irda_license_no": broker.get("irda_license_no"),
        "broker_cin_no": broker.get("cin"),
        "broker_category": broker.get("category"),
        "broker_validity": broker_validity,
        "insurer_logo": insurer.get("insurer_logo"),
        "insurer_name": insurer.get("name"),
        "vehicle_cover_product": vehicle_cover.get("full_name"),
        "insurer_hsn_sac": insurer.get('hsn_sac'),
        "insurer_description_of_service": insurer.get('description_of_service'),
        "insurer_grievance_clause": insurer.get('grievance_clause'),
        "digital_signature": insurer.get('digital_signature'),
    }
    return response_dict


async def get_template(req, data: dict):
    """
    The get_template function is responsible for fetching the template from the database,
        rendering it with Jinja2 and returning a filled template.

    :param req: Determine if the request is a cancellation letter or not
    :param data: dict: Pass the data to be used in the template
    :return: A dictionary with the following keys:
    """
    try:
        insurer_code = data['proposal_obj'].get('insurer_code')  # new_proposal_obj -> proposal_obj
        logger.info(f"Fetching filled template for insurer code: {insurer_code}")
        html_string = await fetch_template(req, insurer=insurer_code)

        environment = jinja2.Environment(autoescape=False)
        template = environment.from_string(html_string)
        context_payload = await get_context(context_payload=data)
        if req.is_cancellation_letter:
            context_payload = restructure_letter_data(context_payload=context_payload)
        else:
            context_payload = restructure_certificate_data(context_payload=context_payload)
        filled_template = template.render(**context_payload)
        return filled_template
    except Exception as e:
        logger.exception(f"Error encountered {e} while fetching template")


async def generate_pdf(req, html_str: str, cancellation_number: str, transaction_id: str) -> None:
    """
    The generate_pdf function takes in a html_str, cancellation_number and transaction_id as arguments.
    It then creates a pdf file with the name of the cancellation number and saves it to an s3 bucket.
    The function returns None if there is no error encountered while creating the pdf file.

    :param html_str: str: Pass the html string to the pdfkit
    :param cancellation_number: str: Name the pdf file
    :param transaction_id: str: Save the pdf to s3 bucket
    :return: A url, but the return type is none
    """
    if req.is_cancellation_letter:
        cancellation_pdf_name = f"{cancellation_number}_letter.pdf"
        logger.info(f"creating policy pdf with name {cancellation_pdf_name}")
    else:
        cancellation_pdf_name = f"{cancellation_number}_certificate.pdf"
        logger.info(f"creating policy pdf with name {cancellation_pdf_name}")

    try:
        cancellation_pdf = pdfkit.from_string(html_str, False)
        cancellation_pdf_url = await save_to_s3_bucket(raw_pdf_content=cancellation_pdf, product_slug='motor',
                                                       transaction_id=transaction_id, file_name=cancellation_pdf_name)

        logger.info(f"policy pdf is successfully created for transaction_id {transaction_id}")
    except Exception:
        logger.exception(f"Error encountered while creating policy pdf for transaction_id: {transaction_id},\
                           and policy_number {cancellation_number}")
        raise PDFGenerationException(name="worker.motor.policy_pdf_generation.generate_pdf",
                                     message=f"Error encountered while generating pdf for transaction \
                                               id: {transaction_id}, please try after some time")

    return cancellation_pdf_url


async def create_pdf(req, request: dict) -> str:
    """
    The create_pdf function is responsible for creating a PDF file from the HTML template.
        It takes in the request object and a dictionary containing all of the data needed to fill out
        the cancellation form. The function then calls get_template, which returns an HTML string with
        all of its placeholders filled out with data from our database. This string is passed into generate_pdf,
        which creates a PDF file using pdfkit and saves it to S3.

    :param req: Pass the request object to the function
    :param request: dict: Pass the data to be used in the template
    :return: The path of the pdf file
    """
    try:
        filled_template = await get_template(req=req, data=request)
        cancellation_number = request["cancellation_obj"]["cancellation_number"]
        transaction_id = request["cancellation_obj"]['transaction_id']
        logger.info(f"Creating cancellation pdf for cancellation no {cancellation_number}")
        return await generate_pdf(req=req,
                                  html_str=filled_template,
                                  cancellation_number=cancellation_number,
                                  transaction_id=transaction_id)
    except Exception as e:
        logger.exception(f"Error encountered {e} while creating pdf for cancellation")
