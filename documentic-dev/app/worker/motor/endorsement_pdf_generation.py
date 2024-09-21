import logging

import jinja2
import pdfkit
from rb_utils.async_http_client import AsyncHttpClient

from app.repository.services import TemplateService
from app.settings import SERVICE_CREDENTIALS
from app.utils.exceptions import PDFGenerationException
from app.utils.services import save_to_s3_bucket

logger = logging.getLogger("api")


async def fetch_template(insurer: str) -> str:
    """
    The fetch_template function fetches the HTML template for a given insurer code.

    :param insurer: str: Fetch the template from the database
    :return: A string, so we can use it in the next step
    """
    logger.info(f"fetching template for insurer code {insurer}")
    template = await TemplateService.get_template(insurer=insurer, doctype_id=2)
    return template.html


async def static_data(insurer_code: str, vehicle_cover_id: str, pincode_id: str, city_id: str, state_id: str,
                      salutation_id: str, ncb_carry_forward_id: int):
    """
    The static_data function is used to fetch the static data for a given insurer_code, vehicle_cover_id, pincode_id, city_id and state id.
        The function returns a JSON response containing the static data.

    :param insurer_code: str: Specify the insurer code
    :param vehicle_cover_id: str: Get the vehicle cover id from the user
    :param pincode_id: str: Pass the pincode_id to the service
    :param city_id: str: Get the city id of the user
    :param state_id: str: Pass the state_id of the user
    :param salutation_id: str: Pass the salutation_id to the service
    :param ncb_carry_forward_id :int: Pass the value of ncb carry forward
    :return: A dictionary with the following keys
    """
    service_url = SERVICE_CREDENTIALS["dataverse"][
                      "dns"] + f"/api/v1/policy_summary?insurer_code={insurer_code}&vehicle_cover_id={vehicle_cover_id}&pincode_id={pincode_id}&city_id={city_id}&state_id={state_id}&salutation_id={salutation_id}&ncb_carry_forward_id={ncb_carry_forward_id}"
    return await AsyncHttpClient.get(url=service_url)


def policy_period(new_tp_coverage=None, new_od_coverage=None):
    """
    The policy_period function takes in two arguments, new_tp_coverage and new_od_coverage.
        If both the arguments are not None, then it returns a string containing the dates of coverage for
        Third Party Liability (TPL) and Own Damage (OD). The function also checks if OD tenure is greater than TPL tenure.
        If yes, then it returns only OD coverage dates else it returns only TPL coverage dates.

    :param new_tp_coverage: Get the tenure of the policy
    :param new_od_coverage: Pass the od_coverage dictionary to the function
    :return: The period of coverage for the policy
    """
    if new_od_coverage and new_tp_coverage:
        tp_coverage_dates = f"{new_tp_coverage['tp_start_date']} to {new_tp_coverage['tp_end_date']}(MidNight)"
        od_coverage_dates = f"{new_od_coverage['od_start_date']} to {new_od_coverage['od_end_date']}(MidNight)" if new_od_coverage else None
        if new_od_coverage['od_tenure'] > new_tp_coverage['tp_tenure']:
            return od_coverage_dates
        else:
            return tp_coverage_dates
    else:
        return f"{new_od_coverage['od_start_date']} to {new_od_coverage['od_end_date']}" if new_od_coverage else f"{new_tp_coverage['tp_start_date']} to {new_tp_coverage['tp_end_date']}"


def restructure_template_data(context_payload):
    """
    The restructure_template_data function takes in the context_payload dictionary as an argument.
    It then extracts all the required data from it and returns a new dictionary with all the required keys and values.
    The returned dict is used to render the template.

    :param context_payload: Pass the data from the main function to this function
    :return: A dictionary of values
    """
    old_od_coverage = context_payload["previous_proposal_obj"].get("coverage_details", {}).get("od_coverage", {}) or {}
    new_od_coverage = context_payload["new_proposal_obj"].get("coverage_details", {}).get("od_coverage", {}) or {}
    endorsed_od_coverage = context_payload["endorsement_premium_obj"].get("coverage_details", {}).get("od_coverage",
                                                                                                      {}) or {}
    old_tp_coverage = context_payload["previous_proposal_obj"].get("coverage_details", {}).get("tp_coverage", {}) or {}
    new_tp_coverage = context_payload["new_proposal_obj"].get("coverage_details", {}).get("tp_coverage", {}) or {}
    endorsed_tp_coverage = context_payload["endorsement_premium_obj"].get("coverage_details", {}).get("tp_coverage",
                                                                                                      {}) or {}

    address = context_payload["new_proposal_obj"]["customer"]["address"]
    vehicle_cover = context_payload.get("vehicle_cover", {})
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

    if "NCB Carry Forward" in context_payload["changed_endorsement_dict"]:
        ncb_percent = context_payload["changed_endorsement_dict"]["NCB Carry Forward"]["ncb_carry_forward_details"][
                          "NCB Entitled"] or "NA"
    else:
        ncb_percent = context_payload.get("ncb_carry_forward", {}).get("name") or "NA"
    salutation =  context_payload.get("salutation", {}).get("name", "")
    insured_name =context_payload["endorsement_obj"]["insured_name"]
    return_dict = {
        "insurer_logo": context_payload.get("insurer", {}).get("insurer_logo"),
        "insurer_name": context_payload.get("insurer", {}).get("name"),
        "product_name": vehicle_cover.get("full_name"),
        "insurer_service_office_address": context_payload.get("insurer", {}).get("servicing_office_address"),
        "insurer_registered_office_address": context_payload.get("insurer", {}).get("registered_office_address"),
        "insurer_hsn_sac" : context_payload.get("insurer", {}).get('hsn_sac'),
        "insurer_description_of_service" : context_payload.get("insurer", {}).get('description_of_service'),
        "insurer_pan": context_payload.get("insurer", {}).get("pan_number"),
        "insurer_gstin": context_payload.get("insurer", {}).get("gstin_number"),
        "irda_registration_no": context_payload.get("insurer", {}).get("irda_registration_no"),
        "policy_number": context_payload["endorsement_obj"]["policy_number"],
        "insured_name":f"{salutation} {insured_name}", 
        "vehicle_cover": vehicle_cover,
        "insured_address": customer_address,
        "od_coverage_detail": f"{new_od_coverage.get('od_start_date')} to {new_od_coverage.get('od_end_date')}(MidNight)"
        if new_od_coverage else "NA",
        "tp_coverage_detail": f"{new_tp_coverage.get('tp_start_date')} to {new_tp_coverage.get('tp_end_date')}(MidNight)"
        if new_tp_coverage else "NA",
        "customer_gst_number": context_payload["new_proposal_obj"].get("customer", {}).get("gstin") or "NA",
        "cpa_coverage_detail": policy_period(new_tp_coverage=new_tp_coverage, new_od_coverage=new_od_coverage),
        "customer_pan_number": context_payload["new_proposal_obj"].get("customer", {}).get("pan_number") or "NA",
        "endorsement_number": context_payload["endorsement_obj"]["endorsement_number"],
        "endorsement_type": context_payload["endorsement_obj"]["endorsement_name"],
        "is_premium_bearing": context_payload["endorsement_obj"]["is_premium_bearing"],
        "place_of_supply": context_payload.get("insurer", {}).get("place_of_supply"),
        "website_address": context_payload.get("insurer", {}).get("website_address"),
        "endorsement_effective_date": context_payload["endorsement_obj"]["effective_date"],
        "changed_endorsement_dict": context_payload["changed_endorsement_dict"],
        "old_proposer_type": "TO BE DYNAMIC",
        "new_proposer_type": "TO BE DYNAMIC",
        "old_proposer_name": "TO BE DYNAMIC",
        "new_proposer_name": "TO BE DYNAMIC",
        "old_ncb_detail": "TO BE DYNAMIC",
        "new_ncb_detail": "TO BE DYNAMIC",
        "old_basic_od": old_od_coverage.get("basic_od") or 0,
        "new_basic_od": new_od_coverage.get("basic_od") or 0,
        "endorsed_basic_od": endorsed_od_coverage.get("basic_od") or 0,
        "old_basic_tp": old_tp_coverage.get("basic_liability") or 0,
        "new_basic_tp": new_tp_coverage.get("basic_liability") or 0,
        "endorsed_basic_tp": endorsed_tp_coverage.get("basic_liability") or 0,
        "old_electrical_accessories_price": old_od_coverage.get("electrical_accessories_price") or 0,
        "new_electrical_accessories_price": new_od_coverage.get("electrical_accessories_price") or 0,
        "endorsed_electrical_accessories_price": endorsed_od_coverage.get("electrical_accessories_price") or 0,
        "old_tp_bi_fuel_kit_price": old_tp_coverage.get("bi_fuel_kit_price") or 0,
        "new_tp_bi_fuel_kit_price": new_tp_coverage.get("bi_fuel_kit_price") or 0,
        "endorsed_tp_bi_fuel_kit_price": endorsed_tp_coverage.get("bi_fuel_kit_price") or 0,
        "old_non_electrical_accessories_price": old_od_coverage.get("non_electrical_accessories_price") or 0,
        "new_non_electrical_accessories_price": new_od_coverage.get("non_electrical_accessories_price") or 0,
        "endorsed_non_electrical_accessories_price": endorsed_od_coverage.get("non_electrical_accessories_price") or 0,
        "old_tp_geo_ext": old_tp_coverage.get("geo_extension_tp_price") or 0,
        "new_tp_geo_ext": new_tp_coverage.get("geo_extension_tp_price") or 0,
        "endorsed_tp_geo_ext": endorsed_tp_coverage.get("geo_extension_tp_price") or 0,
        "old_od_bi_fuel_kit_price": old_od_coverage.get("bi_fuel_kit_price") or 0,
        "new_od_bi_fuel_kit_price": new_od_coverage.get("bi_fuel_kit_price") or 0,
        "endorsed_od_bi_fuel_kit_price": endorsed_od_coverage.get("bi_fuel_kit_price") or 0,
        "old_net_tp_premium": old_tp_coverage.get("total_tp_liability") or 0,
        "new_net_tp_premium": new_tp_coverage.get("total_tp_liability") or 0,
        "endorsed_net_tp_premium": endorsed_tp_coverage.get("total_tp_liability") or 0,
        "old_sub_total_od_premium": old_od_coverage.get("sub_total_od_premium") or 0,
        "new_sub_total_od_premium": new_od_coverage.get("sub_total_od_premium") or 0,
        "endorsed_sub_total_od_premium": endorsed_od_coverage.get("sub_total_od_premium") or 0,
        "old_net_od_premium": old_od_coverage.get("net_od_premium") or 0,
        "new_net_od_premium": new_od_coverage.get("net_od_premium") or 0,
        "endorsed_net_od_premium": endorsed_od_coverage.get("net_od_premium") or 0,
        "old_pa_cover_pd_si": old_tp_coverage.get("pa_paid_driver_price") or 0,
        "new_pa_cover_pd_si": new_tp_coverage.get("pa_paid_driver_price") or 0,
        "endorsed_pa_cover_pd_si": endorsed_tp_coverage.get("pa_paid_driver_price") or 0,
        "old_geo_ext": old_od_coverage.get("geo_extension_od_price") or 0,
        "new_geo_ext": new_od_coverage.get("geo_extension_od_price") or 0,
        "endorsed_geo_ext": endorsed_od_coverage.get("geo_extension_od_price") or 0,
        "old_pa_cover_unnamed_si": old_tp_coverage.get("pa_unnamed_passenger_price") or 0,
        "new_pa_cover_unnamed_si": new_tp_coverage.get("pa_unnamed_passenger_price") or 0,
        "endorsed_pa_cover_unnamed_si": endorsed_tp_coverage.get("pa_unnamed_passenger_price") or 0,
        "old_imt_32": 0,
        "new_imt_32": 0,
        "endorsed_imt_32": 0,
        "old_pa_cover_driver_si": old_tp_coverage.get("cpa_price") or 0,
        "new_pa_cover_driver_si": new_tp_coverage.get("cpa_price") or 0,
        "endorsed_pa_cover_driver_si": endorsed_tp_coverage.get("cpa_price") or 0,
        "old_deductibles": "",
        "new_deductibles": "",
        "endorsed_deductibles": "",
        "old_net_pa_cover": old_tp_coverage.get("total_pa_cover") or 0,
        "new_net_pa_cover": new_tp_coverage.get("total_pa_cover") or 0,
        "endorsed_net_pa_cover": endorsed_tp_coverage.get("total_pa_cover") or 0,
        "old_voluntary_discount": old_od_coverage.get("voluntary_deductible_price") or 0,
        "new_voluntary_discount": new_od_coverage.get("voluntary_deductible_price") or 0,
        "endorsed_voluntary_discount": endorsed_od_coverage.get("voluntary_deductible_price") or 0,
        "old_ll_cover_driver": old_tp_coverage.get("ll_paid_driver_price") or 0,
        "new_ll_cover_driver": new_tp_coverage.get("ll_paid_driver_price") or 0,
        "endorsed_ll_cover_driver": endorsed_tp_coverage.get("ll_paid_driver_price") or 0,
        "old_anti_theft": old_od_coverage.get("anti_theft_price") or 0,
        "new_anti_theft": new_od_coverage.get("anti_theft_price") or 0,
        "endorsed_anti_theft": endorsed_od_coverage.get("anti_theft_price") or 0,
        "old_ll_employees": old_tp_coverage.get("ll_employees_price") or 0,
        "new_ll_employees": new_tp_coverage.get("ll_employees_price") or 0,
        "endorsed_ll_employees": endorsed_tp_coverage.get("ll_employees_price") or 0,
        "old_aai_member": old_od_coverage.get("aai_membership_price") or 0,
        "new_aai_member": new_od_coverage.get("aai_membership_price") or 0,
        "endorsed_aai_member": endorsed_od_coverage.get("aai_membership_price") or 0,
        "old_ll_sub_total": old_tp_coverage.get("total_ll_cover") or 0,
        "new_ll_sub_total": new_tp_coverage.get("total_ll_cover") or 0,
        "endorsed_ll_sub_total": endorsed_tp_coverage.get("total_ll_cover") or 0,
        "old_ncb_value": old_od_coverage.get("ncb_price") or 0,
        "new_ncb_value": new_od_coverage.get("ncb_price") or 0,
        "endorsed_ncb_value": endorsed_od_coverage.get("ncb_price") or 0,
        "old_liability_total": old_tp_coverage.get("net_tp_premium") or 0,
        "new_liability_total": new_tp_coverage.get("net_tp_premium") or 0,
        "endorsed_liability_total": endorsed_tp_coverage.get("net_tp_premium") or 0,
        "old_handicaped": old_od_coverage.get("handicap_discount") or 0,
        "new_handicaped": new_od_coverage.get("handicap_discount") or 0,
        "endorsed_handicaped": endorsed_od_coverage.get("handicap_discount") or 0,
        "old_total_deduction": old_od_coverage.get("sub_total_deduction_premium") or 0,
        "new_total_deduction": new_od_coverage.get("sub_total_deduction_premium") or 0,
        "endorsed_total_deduction": endorsed_od_coverage.get("sub_total_deduction_premium") or 0,
        "old_net_premium": context_payload["previous_proposal_obj"]["net_premium"] or 0,
        "new_net_premium": context_payload["new_proposal_obj"]["net_premium"] or 0,
        "endorsed_net_premium": context_payload["endorsement_premium_obj"]["net_premium"] or 0,
        "old_addon_premium": context_payload["endorsement_premium_obj"]["addon_details"]["old_addon_bundle_premium"] or 0,
        "new_addon_premium": context_payload["endorsement_premium_obj"]["addon_details"]["new_addon_bundle_premium"] or 0,
        "endorsed_addon_premium": context_payload["endorsement_premium_obj"]["addon_details"]["endorsed_addon_premium"] or 0,
        "old_cgst": context_payload["previous_proposal_obj"]["tax"]["cgst"] or 0,
        "new_cgst": context_payload["new_proposal_obj"]["tax"]["cgst"] or 0,
        "endorsed_cgst": context_payload["endorsement_premium_obj"]["tax"]["cgst"] or 0,
        "old_igst": context_payload["previous_proposal_obj"]["tax"]["igst"] or 0,
        "new_igst": context_payload["new_proposal_obj"]["tax"]["igst"] or 0,
        "endorsed_igst": context_payload["endorsement_premium_obj"]["tax"]["igst"] or 0,
        "old_sgst": context_payload["previous_proposal_obj"]["tax"]["sgst"] or 0,
        "new_sgst": context_payload["new_proposal_obj"]["tax"]["sgst"] or 0,
        "endorsed_sgst": context_payload["endorsement_premium_obj"]["tax"]["sgst"] or 0,
        "old_utgst": context_payload["previous_proposal_obj"]["tax"]["utgst"] or 0,
        "new_utgst": context_payload["new_proposal_obj"]["tax"]["utgst"] or 0,
        "endorsed_utgst": context_payload["endorsement_premium_obj"]["tax"]["utgst"] or 0,
        "old_total_tax": context_payload["previous_proposal_obj"]["tax"]["total_tax"] or 0,
        "new_total_tax": context_payload["new_proposal_obj"]["tax"]["total_tax"] or 0,
        "endorsed_total_tax": context_payload["endorsement_premium_obj"]["tax"]["total_tax"] or 0,
        "payable_endorsed_premium": context_payload["endorsement_premium_obj"]['total_premium'],
        "policy_period": policy_period(new_tp_coverage=new_tp_coverage, new_od_coverage=new_od_coverage),
        "digital_signature": context_payload.get("insurer", {}).get("digital_signature"),
        "is_transfer_of_ownership": context_payload["new_proposal_obj"]['is_ownership_transfer'],
        "transfer_of_ownership": context_payload["new_proposal_obj"]['ownership_transfer_fee'],
        "old_proposal_is_transfer_of_ownership": context_payload["previous_proposal_obj"]['is_ownership_transfer'],
        "old_proposal_transfer_of_ownership": context_payload["previous_proposal_obj"]['ownership_transfer_fee'],
        "ncb_percent": ncb_percent if ncb_percent != "NA" else "0%"
    }
    return return_dict


async def get_context(context_payload):
    """
    The get_context function is used to create the context for the proposal.
        It takes in a payload and returns a context_payload with all static data required for creating the proposal.

        Args:
            context_payload (dict): The payload containing new_proposal, previous_proposal and customer details.

    :param context_payload: Pass the context data to the get_context function
    :return: The context payload with the static data added to it
    """
    insurer_code = context_payload['new_proposal_obj'].get('insurer_code')
    vehicle_cover_id = context_payload['new_proposal_obj'].get('vehicle_cover_id')
    pincode_id = context_payload["new_proposal_obj"]["customer"]["address"]["pincode_id"]
    city_id = context_payload["new_proposal_obj"]["customer"]["address"]["city_id"]
    state_id = context_payload["new_proposal_obj"]["customer"]["address"]["state_id"]
    salutation_id = context_payload["new_proposal_obj"]["customer"]["salutation"]
    ncb_carry_forward_id = context_payload["previous_proposal_obj"]["ncb_carry_forward_id"] if \
        context_payload["previous_proposal_obj"]["ncb_carry_forward_id"] else 0
    context_payload.update(
        await static_data(insurer_code=insurer_code, vehicle_cover_id=vehicle_cover_id, pincode_id=pincode_id,
                          city_id=city_id, state_id=state_id, salutation_id=salutation_id,
                          ncb_carry_forward_id=ncb_carry_forward_id))
    logger.info(f"context data created is {context_payload}")
    return context_payload


async def get_template(data: dict):
    """
    The get_template function is responsible for fetching the template from the database,
    filling it with data and returning a filled template.


    :param data: dict: Pass in the data from the request
    :return: A string of html
    """
    insurer_code = data['new_proposal_obj'].get('insurer_code')
    logger.info(f"fetching filled template for nsurer code {insurer_code}")
    html_string = await fetch_template(insurer=insurer_code)

    environment = jinja2.Environment(autoescape=False)
    template = environment.from_string(html_string)
    context_payload = await get_context(context_payload=data)
    context_payload = restructure_template_data(context_payload)
    filled_template = template.render(**context_payload)
    return filled_template


async def generate_pdf(html_str: str, endorsement_number: str, transaction_id: str) -> None:
    """
    The generate_pdf function takes in a html string, endorsement number and transaction id as arguments.
    It then creates a pdf file with the name of the endorsement number and saves it to an s3 bucket.
    The function returns the url of this saved pdf file.

    :param html_str: str: Pass the html string to be converted into pdf
    :param endorsement_number: str: Name the pdf file
    :param transaction_id: str: Uniquely identify the transaction
    :return: The endorsement_pdf_url
    """
    endorsement_pdf_name = f"{endorsement_number}.pdf"
    logger.info(f"creating policy pdf with name {endorsement_pdf_name}")

    try:
        endorsement_pdf = pdfkit.from_string(html_str, False)
        endorsement_pdf_url = await save_to_s3_bucket(raw_pdf_content=endorsement_pdf, product_slug='motor',
                                                      transaction_id=transaction_id, file_name=endorsement_pdf_name)

        logger.info(f"policy pdf is successfully created for transaction_id {transaction_id}")
    except Exception:
        logger.exception(f"Error encountered while creating policy pdf for transaction_id: {transaction_id},\
                           and policy_number {endorsement_number}")
        raise PDFGenerationException(name="worker.motor.policy_pdf_generation.generate_pdf",
                                     message=f"Error encountered while generating pdf for transaction \
                                               id: {transaction_id}, please try after some time")

    return endorsement_pdf_url


async def create_pdf(request: dict) -> str:
    """
    The create_pdf function takes in a request dictionary and returns the path to the generated PDF.
    The request dictionary contains all of the data needed to fill out an endorsement template, including:
        - The endorsement object itself (containing information about who is being endorsed)
        - The endorser's name and title (for use in filling out the template)
        - A list of endorsements that have already been made for this transaction ID, if any exist.  This is used to determine whether or not we should include a &quot;previous endorsements&quot; section on this particular PDF.

    :param request: dict: Pass in the data that will be used to fill out the template
    :return: The path of the generated pdf file
    """
    filled_template = await get_template(data=request)
    endorsement_number = request["endorsement_obj"]["endorsement_number"]
    transaction_id = request["endorsement_obj"]['transaction_id']
    logger.info(f"Creating endorsement pdf for endorsement no {endorsement_number}")
    return await generate_pdf(html_str=filled_template,
                              endorsement_number=endorsement_number,
                              transaction_id=transaction_id)
