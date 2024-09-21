import logging
from datetime import datetime

import jinja2
import pdfkit
from dateutil.relativedelta import relativedelta
from rb_utils.async_http_client import AsyncHttpClient

from app.models.generate_policy import PolicyPDFStatus, DocumentStatus
from app.repository.services import TemplateService, DocumentStatusServices
from app.settings import DOCUMENT_DNS_CONFIG
from app.settings import SERVICE_CREDENTIALS, S3_ASSET_URL
from app.utils.exceptions import PDFGenerationException
from app.utils.services import save_to_s3_bucket

logger = logging.getLogger("api")

date_format = "%d-%m-%Y"


async def fetch_template(insurer: str) -> str:
    """
    The fetch_template function fetches the template for a given insurer code.

    :param insurer: str: Pass the insurer code to the function
    :return: A string
    """
    logger.info(f"fetching template for insurer code {insurer}")
    template = await TemplateService.get_template(insurer=insurer, doctype_id=1)
    return template.html


async def designated_person_data(designated_person_code: str):
    """
    The designated_person_data function takes a designated_person_code as an argument and returns the dataverse
        response for that code. The function is asynchronous, so it can be used in conjunction with other async functions.

    :param designated_person_code: str: Specify the designated person code
    :return: A json object containing the following fields:
    """
    service_url = SERVICE_CREDENTIALS["dataverse"][
                      "dns"] + f"/api/v1/policy_summary?designated_person_code={designated_person_code}"
    return await AsyncHttpClient.get(url=service_url)


async def get_user_details(user_id: str):
    """
    The get_user_details function takes in a user_id and returns the details of that user.

    :param user_id: str: Specify the user_id of the user whose details are to be fetched
    :return: A json object that contains user details
    """
    service_url = SERVICE_CREDENTIALS["auth"]["dns"] + f"/api/v1/get_user_details/?user_id={user_id}"
    return await AsyncHttpClient.get(url=service_url)


def quotes_context(data: dict) -> dict:
    """
    The quotes_context function takes in a dictionary of data and returns a dictionary of context.
    The quotes_context function is used to create the context for the quotes template.


    :param data: dict: Pass the data from the previous function
    :return: A dictionary with the manufacturing year of the car
    """
    logger.info("creating context for quotes data")
    quotes = data['query_detail']
    if quotes and quotes.get('quote_request'):
        quotes_request = quotes.get('quote_request')
        manufacturing_year = quotes_request.get("manufacturing_year")
        return {
            "manufacturing_year": manufacturing_year,
        }
    return {}


def pricing_content(data: dict) -> dict:
    """
    The pricing_content function takes in a dictionary of data and returns a dictionary with the following keys:
        basic_od, electrical_accessories_od, non_electrical_accessories_od, bi-fuel-kit-od, sub-total od
        od geographical area extension (geo ext), imt 23 premium (imt23), voluntary discount (voluntary)
        anti theft discount(anti theft), aai membership(aai membership), ncb(ncb) handicapped discount(handicap)

    :param data: dict: Pass the data from the previous function
    :return: A dictionary of the following form:
    """
    logger.info("creating context for pricing data")
    quotes = data['query_detail']['quote_response']
    tp_premium = quotes.get('tp_premium') or {}
    od_premium = quotes.get('od_premium') or {}

    basic_od = od_premium.get('discounted_od') or 0
    electrical_accessories_od = od_premium.get(
        'electrical_accessories_price') or 0
    non_electrical_accessories_od = od_premium.get(
        'non_electrical_accessories_price') or 0
    bi_fuel_kit_od = od_premium.get("bi_fuel_kit_od_price") or 0
    geo_extension_od = od_premium.get("geo_extension_od_price") or 0
    imt_23_premium = od_premium.get("imt_23_premium") or 0
    voluntary_discount = od_premium.get('voluntary_deductible_price') or 0
    anti_theft_discount = od_premium.get("anti_theft_price") or 0
    aai_membership = od_premium.get("aai_membership_price") or 0
    ncb = od_premium.get("ncb_price") or 0
    handicap_discount = od_premium.get('handicap_discount') or 0
    sub_total_od = od_premium.get('sub_total_od_premium') or 0
    sub_total_deductions = od_premium.get(
        'sub_total_deduction_premium') or 0

    basic_tp = tp_premium.get('basic_liability') or 0
    bi_fuel_kit_tp = tp_premium.get('bi_fuel_kit_tp_price') or 0
    geo_extension_tp = tp_premium.get('geo_extension_tp_price') or 0
    net_tp_premium = tp_premium.get('net_tp_premium') or 0
    pa_cover_paid_driver = tp_premium.get('pa_paid_driver_price') or 0
    pa_cover_unnamed_passenger = tp_premium.get(
        'pa_unnamed_passenger_price') or 0
    compulsory_pa_cover_owner_driver = tp_premium.get('cpa_price') or 0
    ll_paid_driver = tp_premium.get('ll_paid_driver_price') or 0
    ll_employee = tp_premium.get('ll_employees_price') or 0

    sub_total_liability = tp_premium.get('total_tp_liability') or 0
    sub_total_legal_liability = tp_premium.get('total_ll_cover') or 0
    sub_total_pa_cover = tp_premium.get('total_pa_cover') or 0

    return {
        "basic_od": basic_od,
        "electrical_accessories_od": electrical_accessories_od,
        "non_electrical_accessories_od": non_electrical_accessories_od,
        "bi_fuel_od": bi_fuel_kit_od,
        "sub_total_od": sub_total_od,
        "od_geographical_area_ext": geo_extension_od,
        "imt_23_premium": imt_23_premium,
        "voluntary_discount": voluntary_discount,
        "anti_theft_discount": anti_theft_discount,
        "aai_membership": aai_membership,
        "ncb": ncb,
        "handicapped_discount": handicap_discount,
        "basic_tp_premium": basic_tp,
        "bi_fuel_tp": bi_fuel_kit_tp,
        "tp_geographical_area_ext": geo_extension_tp,
        "sub_total_liability": sub_total_liability,
        "pa_cover_paid_driver": pa_cover_paid_driver,
        "pa_cover_unnamed_passenger": pa_cover_unnamed_passenger,
        "compulsory_pa_cover_owner_driver": compulsory_pa_cover_owner_driver,
        "sub_total_pa_cover": sub_total_pa_cover,
        "ll_paid_driver": ll_paid_driver,
        "ll_employees": ll_employee,
        "sub_total_legal_liability": sub_total_legal_liability,
        "net_liability_premium": net_tp_premium,
        "sub_total_deduction": sub_total_deductions,
    }


def customer_context(data: dict) -> dict:
    """
    The customer_context function creates a context for customer data.

    :param data: dict: Pass the data that is being processed by the function
    :return: A dictionary with the key-value pairs &quot;customer_pan&quot; and &quot;customer_gstin&quot;
    """
    logger.info("creating context for customer data")
    proposal = data.get('proposal_detail')
    policy_summary = data.get("policy_summary")

    if proposal and proposal.get('customer') and policy_summary:
        customer = proposal.get('customer')
        customer_pan = customer.get('pan_number') or "NA"
        customer_gstin = customer.get("gstin") or "NA"

        return {
            "customer_pan": customer_pan.upper(),
            "customer_gstin": customer_gstin
        }

    return {}


async def get_ncb_deduction(ncb_carry_forward_id, last_year_ncb_id, left_days, is_claim_case):
    """
    The get_ncb_deduction function is used to get the NCB deduction value for a policy.
        It takes in three parameters:
            1) ncb_carry_forward_id - The id of the NCB carry forward object, if any.
            2) last_year_ncb - The id of the last year's NCB object, if any.
            3) left days - Number of days left from expiry date till today's date (can be negative).

    :param ncb_carry_forward_id: Get the ncb value from the dataverse service
    :param last_year_ncb_id: Get the ncb value from dataverse
    :param left_days: Determine the number of days left for the policy to expire
    :param is_claim_case: Check if the policy is a claim case or not
    :return: The ncb deduction in percentage
    """
    ncb_value = 0
    if is_claim_case or left_days < -90:
        ncb_value = 0
    if last_year_ncb_id:
        service_url = SERVICE_CREDENTIALS["dataverse"][
                          "dns"] + f"/api/v1/policy_summary/?last_year_ncb_id={last_year_ncb_id}"
        ncb_details = await AsyncHttpClient.get(url=service_url)
        ncb_value = ncb_details["last_year_ncb"]["new_slab_value"]
    if ncb_carry_forward_id:
        service_url = SERVICE_CREDENTIALS["dataverse"][
                          "dns"] + f"/api/v1/policy_summary/?ncb_carry_forward_id={ncb_carry_forward_id}"
        ncb_details = await AsyncHttpClient.get(url=service_url)
        ncb_value = ncb_details["ncb_carry_forward"]["value"]
    return f"{ncb_value}%"


def policy_summary_context(data: dict) -> dict:
    """
    The policy_summary_context function creates a context for policy_summary data.
        Args:
            data (dict): The dictionary containing the policy_summary and query detail information.

    :param data: dict: Pass the data to be used in the template
    :return: A dictionary with the following keys:
    """
    logger.info("creating context for policy_summary data")
    policy_summary = data.get('policy_summary')
    quotes = data['query_detail']
    quotes_request = None
    sub_str = " "
    if quotes and quotes.get('quote_request') and quotes.get('quote_response'):
        quotes_request = quotes.get('quote_request')

    if policy_summary and quotes_request:
        insurer_name = policy_summary['insurer'].get('name')
        insurer_first_name = insurer_name[:insurer_name.index(sub_str) + len(sub_str)]
        insurer = policy_summary['insurer']
        broker = policy_summary['broker']
        dealer = policy_summary['dealer_details']

        insurer_cin = insurer.get('cin')
        insurer_uin = insurer.get('uin')
        insurer_service_office_address = insurer.get(
            'servicing_office_address')
        insurer_registered_office_address = insurer.get(
            'registered_office_address')
        insurer_hsn_sac = insurer.get('hsn_sac')
        insurer_place_of_supply = insurer.get('place_of_supply')
        insurer_invoice_number = insurer.get('invoice_number')
        insurer_description_of_service = insurer.get('description_of_service')
        insurer_logo = insurer.get('insurer_logo')
        insurer_pan = insurer.get('pan_number')
        insurer_gstin = insurer.get('gstin_number')
        website_address = insurer.get('website_address')
        irda_reg_no = insurer.get('irda_registration_no')
        insurer_limitations_as_to_us = insurer.get('limitations_as_to_us')
        insurer_drivers_clause = insurer.get('drivers_clause')
        insurer_grievance_clause = insurer.get('grievance_clause')
        insurer_disclaimer = insurer.get('disclaimer')
        insurer_important_notice = insurer.get('important_notice')
        insurer_puc_clause = insurer.get('puc_clause')
        insurer_note = insurer.get('note')
        insurer_fastag_clause = insurer.get('fastag_clause')
        insurer_limits_of_liability_clause = insurer.get(
            'limits_of_liability_clause')
        insurer_cpa_sum_insured = insurer.get(
            "cpa_sum_insured_for_liability_clause")
        seating_capacity = policy_summary.get('seating_capacity')

        make = policy_summary.get('make')
        vehicle_cover_product = policy_summary.get('vehicle_cover_product')
        vehicle_detail = policy_summary.get('vehicle_detail')
        rto = policy_summary.get('rto')
        rto_code = policy_summary.get('rto_code')
        vehicle_class = policy_summary.get('vehicle_class')
        cpa_waiver_reason = policy_summary.get('cpa_waiver_reason') or "NA"
        geo_extension_countries = policy_summary.get(
            "geo_extension_data") or "NA"
        nominee_relation = policy_summary.get('nominee_relation') or "NA"
        appointee_relation = policy_summary.get("appointee_relation") or "NA"
        broker_category = broker.get('category')
        irda_license_no = broker.get('irda_license_no')
        validity = broker.get('validity')
        broker_cin = broker.get('cin')
        name_and_address = broker.get('name') + ", " + broker.get('address')
        contact_no = broker.get('mobile')
        support_mail_id = broker.get('email')
        own_damage_period_range = policy_summary.get('own_damage_period_range')
        liability_period_range = policy_summary.get('liability_period_range')
        cpa_period_range = policy_summary.get('cpa_period_range')
        liability_period = policy_summary.get('liability_period')
        insured_name = policy_summary.get('customer_name')
        policy_type_code = policy_summary.get('policy_type_code')
        prev_od_insurer = policy_summary.get('prev_od_insurer') or "NA"
        prev_tp_insurer = policy_summary.get('prev_od_insurer') or "NA"
        prev_od_star_date = policy_summary.get('prev_od_start_date') or "NA"
        insured_address = policy_summary.get('insured_address')
        customer_city = policy_summary.get('customer_city') or "NA"
        prev_tp_tenure = policy_summary.get('prev_tp_tenure')
        prev_od_tenure = policy_summary.get('prev_od_tenure')
        imt_codes = policy_summary.get('imt_codes')
        digital_signature = insurer.get('digital_signature')
        policy_type_uin = policy_summary.get('policy_type_uin') or "NA"
        opted_addons_name = policy_summary.get('addon_bundle') or "NA"
        pa_paid_driver_value = policy_summary.get('pa_paid_driver_value') or 0
        misp_code = dealer.get('misp_code')
        pa_unnamed_passenger_value = policy_summary.get(
            'pa_unnamed_passenger_value') or 0
        voluntary_deductible_value = policy_summary.get(
            'voluntary_deductible_value') or 0

        return {
            "rto": f"{rto} ({rto_code})",
            "make": make,
            "imt_codes": imt_codes,
            "insurer_name": insurer_name,
            "insurer_first_name": insurer_first_name,
            "insurer_uin": insurer_uin,
            "pa_paid_driver_value": pa_paid_driver_value,
            "pa_unnamed_passenger_value": pa_unnamed_passenger_value,
            "voluntary_deductible_value": voluntary_deductible_value,
            "insurer_cin": insurer_cin,
            "insurer_logo": insurer_logo,
            "insurer_pan": insurer_pan,
            "insurer_gstin": insurer_gstin,
            "insurer_hsn_sac": insurer_hsn_sac,
            "insurer_note": insurer_note,
            "vehicle_class": vehicle_class,
            "insurer_service_office_address": insurer_service_office_address,
            "insurer_registered_office_address": insurer_registered_office_address,
            "insurer_place_of_supply": insurer_place_of_supply,
            "insurer_invoice_number": insurer_invoice_number,
            "insurer_description_of_service": insurer_description_of_service,
            "insurer_limitations_as_to_us": insurer_limitations_as_to_us,
            "insurer_drivers_clause": insurer_drivers_clause,
            "insurer_grievance_clause": insurer_grievance_clause,
            "insurer_disclaimer": insurer_disclaimer,
            "insurer_important_notice": insurer_important_notice,
            "insurer_puc_clause": insurer_puc_clause,
            "insurer_fastag_clause": insurer_fastag_clause,
            "insurer_compulsory_deductible": 100,
            "insurer_limits_of_liability_clause": insurer_limits_of_liability_clause,
            "insurer_cpa_sum_insured": insurer_cpa_sum_insured,
            "website_address": website_address,
            "irda_registration_no": irda_reg_no,
            "vehicle_cover_product": vehicle_cover_product,
            "vehicle_detail": vehicle_detail,
            "seating_capacity": seating_capacity,
            "own_damage_period_range": own_damage_period_range,
            "liability_period_range": liability_period_range,
            "liability_period": liability_period,
            "geo_extension_countries": geo_extension_countries,
            "cpa_waiver_reason": cpa_waiver_reason,
            "relationship_with_insured": nominee_relation,
            "relationship_with_nominee": appointee_relation,
            "broker_category": broker_category,
            "irda_license_no": irda_license_no,
            "validity": validity,
            "broker_cin": broker_cin,
            "contact_no": contact_no,
            "name_and_address": name_and_address,
            "support_mail_id": support_mail_id,
            "insured_name": insured_name,
            "cpa_period_range": cpa_period_range,
            "policy_type_code": policy_type_code,
            "prev_od_insurer": prev_od_insurer,
            "prev_tp_insurer": prev_tp_insurer,
            "prev_od_star_date": prev_od_star_date,
            "insured_address": insured_address,
            "customer_city": customer_city,
            "prev_tp_tenure": prev_tp_tenure,
            "prev_od_tenure": prev_od_tenure,
            "digital_signature": digital_signature,
            "opted_addons_name": opted_addons_name,
            "policy_type_uin": policy_type_uin,
            "misp_code": misp_code or "NA"
        }

    return {}


def policy_context(data: dict) -> dict:
    """
    The policy_context function is used to create a context for policy data.
        Args:
            data (dict): The dictionary containing the policy and query details.

    :param data: dict: Pass the policy_detail and query_detail data to the function
    :return: A dictionary with the following keys:
    """
    logger.info("creating context for policy data")
    policy = data['policy_detail']
    quotes = data['query_detail']
    quotes_request = None
    if quotes and quotes.get('quote_request'):
        quotes_request = quotes.get('quote_request')

    if policy and quotes_request:
        policy_no = policy.get('policy_number')
        created_at = datetime.strptime(policy.get('created_at'), '%Y-%m-%dT%H:%M:%S')
        policy_issue_on = datetime.strftime(created_at, date_format)
        policy_generation_datetime = datetime.strftime(created_at, '%d-%m-%Y (%H:%M)')
        transaction_id = policy.get('transaction_id')
        policy_no_url = policy_no.replace('/', '-')
        qr_code_policy_pdf_url = f"{DOCUMENT_DNS_CONFIG}/get_document/documents/motor/{transaction_id}/{policy_no_url}.pdf"

        return {
            "policy_no": policy_no,
            "policy_issue_on": policy_issue_on,
            "policy_generation_datetime": policy_generation_datetime,
            "policy_pdf_url": qr_code_policy_pdf_url
        }

    return {}


def calculate_od_start_date(od_policy_end_date: str):
    """
    The calculate_od_start_date function takes in a string representing the end date of an OD policy and returns
    the start date of that same policy. The function assumes that the input is a string formatted as dd-mm-yyyy,
    and it will return &quot;NA&quot; if no input is provided.

    :param od_policy_end_date: str: Pass the od_policy_end_date value to the function
    :return: The start date of the od policy
    """
    if not od_policy_end_date:
        return "NA"
    od_start_date = datetime.strptime(od_policy_end_date, date_format).date() - relativedelta(years=1, days=-1)
    return od_start_date.strftime(date_format)


def proposal_context(data: dict) -> dict:
    """
    The proposal_context function creates a context for proposal data.
        Args:
            data (dict): The dictionary containing the proposal_detail and policy_summary keys.

    :param data: dict: Pass the data from the previous function to this one
    :return: A dictionary which is used to render the proposal
    """
    logger.info("creating context for proposal data")
    proposal = data.get('proposal_detail')
    policy_summary = data.get('policy_summary')

    ll_for_employee_count = 0
    cpa_opted, result = False, {}
    net_od_premium = 0

    tax = proposal.get('tax')
    cgst = tax.get('cgst')
    sgst = tax.get('sgst')
    igst = tax.get('igst')
    utgst = tax.get('utgst')
    total_tax = tax.get('total_tax')

    if proposal:
        proposal_number = proposal.get('proposal_number') or "NA"
        proposal_date = proposal.get('proposal_generation_date') or "NA"

        # idv details
        electrical_accessories_idv = proposal.get("electrical_accessories_idv")
        non_electrical_accessories_idv = proposal.get(
            "non_electrical_accessories_idv")
        bifuel_kit_idv = proposal.get('bi_fuel_kit_idv')
        total_idv = proposal.get("total_idv")
        total_premium_payable = proposal.get("total_premium")
        net_premium = round(proposal.get("net_premium"), 2)
        cpa_opted = proposal.get("is_cpa")

        coverage_details = proposal['coverage_details']
        if coverage_details:
            tp_coverage = coverage_details.get('tp_coverage')
            if tp_coverage:
                ll_for_employee_count = tp_coverage.get('ll_employee_id')

        if coverage_details:
            od_coverage = coverage_details.get('od_coverage')
            if od_coverage:
                net_od_premium = od_coverage.get('net_od_premium')

        nominee = proposal.get('nominee')
        if nominee:
            nominee_name = nominee.get("name")
            nominee_age = nominee.get("age")
            appointee_name = nominee.get("appointee_name") or "NA"
            result.update({
                "nominee_name": nominee_name,
                "nominee_age": nominee_age,
                "appointee_name": appointee_name,
            })

        vehicle_details = proposal.get('vehicle_details')
        if vehicle_details:
            invoice_date = vehicle_details.get('invoice_date')
            registration_date = vehicle_details.get('registration_date')
            registration_number = vehicle_details.get(
                'registration_number') or "NEW"
            chassis_number = vehicle_details.get('chassis_number')
            engine_number = vehicle_details.get('engine_number')
            vehicle_idv = vehicle_details.get('idv')
            result.update({
                "invoice_date": invoice_date,
                "registration_date": registration_date,
                "registration_no": registration_number,
                "chassis_number": chassis_number,
                "engine_number": engine_number,
                "vehicle_idv": vehicle_idv
            })
        prev_od_policy_number = prev_od_end_date = prev_od_start_date = prev_od_insurer = "NA"
        prev_policy_details = proposal['prev_policy_details']
        if prev_policy_details:
            prev_od_policy_number = prev_policy_details.get('policy_number')
            prev_od_end_date = prev_policy_details.get('od_policy_end_date', "NA")
            prev_od_start_date = calculate_od_start_date(prev_policy_details.get('od_policy_end_date'))
            prev_od_insurer = policy_summary.get('prev_od_insurer')

        other_tp_policy_details = proposal['other_tp_policy_details']
        if other_tp_policy_details:
            result.update({
                "prev_tp_policy_number": other_tp_policy_details.get('policy_number') or "NA",
                "prev_tp_start_date": other_tp_policy_details.get('tp_policy_start_date') or "NA",
                "prev_tp_end_date": other_tp_policy_details.get('tp_policy_end_date') or "NA",
                "prev_tp_insurer": policy_summary.get('prev_tp_insurer') or 'NA',
            })

        hypothecation = proposal['hypothecation'] or {}
        if hypothecation:
            result.update({
                "hypothecation_agreement": policy_summary.get("agreement_type"),
                "hypothecation_financier": policy_summary.get("financier"),
                "hypothecation_loan_acc_no": hypothecation.get("loan_account_number"),
                "hypothecation_branch": hypothecation.get("branch"),
                "hypothecation_city": policy_summary.get("hypothecation_city")
            })

        selected_addon_bundles = proposal.get('selected_addon_bundles')
        addon_bundle_premium, opted_bundle_name = 0, None
        if selected_addon_bundles:
            for bundle in selected_addon_bundles:
                opted_bundle_name = bundle['bundle_name']
                addon_bundle_premium += bundle['premium']

        result.update({
            "net_premium": net_premium,
            "net_od_premium": net_od_premium,
            "total_premium_payable": total_premium_payable,
            "cgst": cgst,
            "sgst": sgst,
            "utgst": utgst,
            "igst": igst,
            "total_tax": total_tax,
            "electrical_accessories_idv": electrical_accessories_idv,
            "non_electrical_accessories_idv": non_electrical_accessories_idv,
            "cng_lpg_kit": bifuel_kit_idv,
            "total_idv": total_idv,
            "prev_od_policy_number": prev_od_policy_number,
            "prev_od_end_date": prev_od_end_date,
            "prev_od_start_date": prev_od_start_date,
            "prev_od_insurer": prev_od_insurer,
            "proposal_no_and_date": f"{proposal_number}, {proposal_date}",
            "ll_for_employee_count": ll_for_employee_count,
            "addon_bundle_premium": addon_bundle_premium,
            "opted_bundle_name": opted_bundle_name,
            "cpa_opted": cpa_opted
        })
        return result


async def payment_context(request, data: dict) -> dict:
    """
    The payment_context function is used to create the context for proposal data.
        Args:
            request (dict): The request object.
            data (dict): The payment_detail dict from the incoming payload.

    :param request: Get the request object
    :param data: dict: Get the data from the request body
    :return: A dictionary with the following keys:
    """
    logger.info("creating context for proposal data")
    payment = data.get('payment_detail')
    result = {}
    user_details = await get_user_details(user_id=request.headers.get('x-user-id'))
    dealer_person = payment.get('dealer_person')
    dealer = await designated_person_data(designated_person_code=dealer_person)
    result["dp_name"] = dealer['designated_person']['designated_person_name']
    result["dp_code"] = dealer_person
    misp_name = "NA"
    if user_details.get('user_details', {}).get('misp_details'):
        misp_details = user_details['user_details']['misp_details']
        misp_name = misp_details['first_name']
        if misp_details['middle_name']:
            misp_name = f"{misp_name} {misp_details['middle_name']}"
        if misp_details['last_name']:
            misp_name = f"{misp_name} {misp_details['last_name']}"
    result.update({
        "misp_name": misp_name
    })
    return result


async def get_context(request, data):
    """
    The get_context function is used to create the context payload for the quote response.
        The function takes in a request object and data as input parameters.
        It returns a dictionary containing all the required information for creating context payload.

    :param request: Get the session data
    :param data: Pass the data from the previous function
    :return: A dictionary with the following keys:
    """
    context_payload = {}
    quotes_request = data['query_detail']['quote_request']
    quotes_response = data['query_detail']['quote_response']
    is_claim_case = quotes_request.get('renewal_details').get('is_claim_case') if quotes_request.get(
        'renewal_details') else False
    ncb_percent = await get_ncb_deduction(ncb_carry_forward_id=quotes_request.get('ncb_carry_forward_id', 0),
                                          last_year_ncb_id=quotes_request.get('last_year_ncb_id', 0),
                                          left_days=quotes_response.get('left_days', 0),
                                          is_claim_case=is_claim_case)
    context_payload.update(quotes_context(data=data))
    context_payload.update(pricing_content(data=data))
    context_payload.update(customer_context(data=data))
    context_payload.update(policy_summary_context(data=data))
    context_payload.update(policy_context(data=data))
    context_payload.update(proposal_context(data=data))
    context_payload.update(await payment_context(request=request, data=data))
    context_payload.update({"ncb_percentage": ncb_percent})
    context_payload["s3_asset_url"] = S3_ASSET_URL
    logger.info(f"context data created is {context_payload}")
    return context_payload


async def get_template(request, data: dict):
    """
    The get_template function is responsible for fetching the template from the database,
        filling it with data and returning a filled template.

    :param request: Get the request object
    :param data: dict: Pass the data from the request to this function
    :return: A filled template
    """
    insurer_code = data['policy_detail'].get('insurer_code')
    logger.info(f"Fetching filled template for insurer code: {insurer_code}")
    html_string = await fetch_template(insurer=insurer_code)

    environment = jinja2.Environment(autoescape=False)
    template = environment.from_string(html_string)
    context_payload = await get_context(request=request, data=data)
    filled_template = template.render(**context_payload)

    return filled_template


async def generate_pdf(html_str: str, policy_number: str, document_id: int, transaction_id: str) -> None:
    """
    The generate_pdf function is responsible for generating a PDF from the HTML string passed to it.
        It uses the pdfkit library to generate a PDF from an HTML string, and then saves that file in S3.
        The function returns the URL of this saved file.

    :param html_str: str: Pass the html string to be converted into pdf
    :param policy_number: str: Create the pdf file name
    :param document_id: int: Fetch the document status object from the database
    :param transaction_id: str: Identify the transaction uniquely
    :return: A string, but the return type is none
    """
    document = await DocumentStatus.fetch(key=document_id)

    policy_pdf_name = policy_number.replace("/", "-")
    logger.info(f"creating policy pdf with name {policy_pdf_name}")

    data = {
        "current_state": PolicyPDFStatus.FAILED.name
    }

    try:
        policy_pdf = pdfkit.from_string(html_str, False)
        policy_pdf_url = await save_to_s3_bucket(raw_pdf_content=policy_pdf, product_slug='motor',
                                                 transaction_id=transaction_id, file_name=f"{policy_pdf_name}.pdf")

        data.update(current_state=PolicyPDFStatus.COMPLETED.name,
                    url=policy_pdf_url)
        logger.info(
            f"policy pdf is successfully created for transaction_id {transaction_id}")
    except Exception:
        logger.exception(f"Error encountered while creating policy pdf for transaction_id: {transaction_id},\
                       and policy_number {policy_number}")
        await DocumentStatusServices.update_document(data=data, obj=document)
        raise PDFGenerationException(name="worker.motor.policy_pdf_generation.generate_pdf",
                                     message=f"Error encountered while generating pdf for transaction \
                                           id: {transaction_id}, please try after some time")

    await DocumentStatusServices.update_document(data=data, obj=document)
    return policy_pdf_url


async def create_pdf(req, request: dict):
    """
    The create_pdf function is responsible for creating a PDF document from the
        HTML template and data provided.

    :param req: Pass the request object to the function
    :param request: dict: Pass the request data from the client to this function
    :return: A dict that contains the url to the pdf document
    """
    filled_template = await get_template(request=req, data=request)
    policy_number = request['policy_detail'].get('policy_number')
    document_id = request.get('document_id')
    transaction_id = request['transaction_id']
    logger.info(f"Creating policy pdf for policy no {policy_number}")
    return await generate_pdf(html_str=filled_template,
                              policy_number=policy_number,
                              document_id=document_id,
                              transaction_id=transaction_id)


async def fetch_premium_breakup_template(insurer: str) -> str:
    logger.info(f"fetching template for insurer code {insurer}")
    template = await TemplateService.get_template(insurer=insurer, doctype_id=5)
    return template.html


async def get_premium_breakup_template(data: dict):
    """
    The get_premium_breakup_template function takes in a dictionary of data and returns the premium breakup template
    filled with the data. The function first fetches the premium breakup template from S3, then uses Jinja2 to fill it
    with the provided data.

    :param data: dict: Pass the data to be used in the template
    :return: The premium breakup template
    """
    insurer_code = data["insurer_code"]
    logger.info(f"Fetching filled template for insurer code: {insurer_code}")
    html_string = await fetch_premium_breakup_template(insurer=insurer_code)

    environment = jinja2.Environment(autoescape=False)
    template = environment.from_string(html_string)
    filled_template = template.render(**data)

    return filled_template


async def generate_premium_breakup_pdf(html_str: str, quote_id: str, transaction_id: str) -> None:
    """
    The generate_premium_breakup_pdf function takes in a html string and returns the url of the pdf generated.
        The function uses pdfkit to generate a premium breakup pdf from the html string passed as an argument.
        It then saves this file to s3 bucket and returns its url.

    :param html_str: str: Pass the html string that is to be converted into pdf
    :param quote_id: str: Create the pdf file name
    :param transaction_id: str: Identify the transaction for which the pdf is being generated
    :return: The url of the pdf
    """
    premium_breakup_pdf_name = f"{quote_id}_premium_breakup.pdf"
    logger.info(f"creating premium breakup pdf with name {premium_breakup_pdf_name}")

    try:
        premium_breakup_pdf = pdfkit.from_string(html_str, False)
        cancellation_pdf_url = await save_to_s3_bucket(raw_pdf_content=premium_breakup_pdf, product_slug='motor',
                                                       transaction_id=transaction_id,
                                                       file_name=premium_breakup_pdf_name)

        logger.info(f"premium breakup pdf is successfully created for transaction_id {transaction_id}")
    except Exception:
        logger.exception(f"Error encountered while creating premium breakup pdf for transaction_id: {transaction_id},\
                           and policy_number {quote_id}")
        raise PDFGenerationException(name="worker.motor.policy_pdf_generation.generate_pdf",
                                     message=f"Error encountered while generating pdf for transaction \
                                               id: {transaction_id}, please try after some time")

    return cancellation_pdf_url


async def create_premium_breakup_pdf(request: dict):
    """
    The create_premium_breakup_pdf function is used to create a pdf for the premium breakup.
        It takes in request data and returns the path of the generated pdf.

    :param request: dict: Get the data required to fill the template
    :return: A tuple of the form (pdf_bytes, pdf_name)
    """
    try:
        logger.info(f"Request data received for premium breakup is {request}")
        filled_template = await get_premium_breakup_template(data=request)
        quote_id = request["quote_id"]
        transaction_id = request["transaction_id"]
        return await generate_premium_breakup_pdf(html_str=filled_template,
                                                  quote_id=quote_id,
                                                  transaction_id=transaction_id)
    except Exception as e:
        logger.exception(f"Error encountered {e} while creating pdf for premium breakup")
