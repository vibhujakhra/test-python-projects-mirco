import logging

import numpy as np
import pandas as pd
from pandas import DataFrame

from app.data_insertion.base import BaseInsert
from app.models.addons import Addon, Bundle, AddonBundle
from app.models.financier import Bank, AccountType
from app.models.insurer import Insurer, UserRole, InsurerLocalOffice, ICDealerMapping
from app.models.personal_details import Salutation, Designation
from app.utils.service import validate_id

logger = logging.getLogger('api')


class InsurerInsert(BaseInsert):
    SQLALCHEMY_MODEL = Insurer

    @classmethod
    async def get_bank_ids_map(cls):
        bank_names = await Bank.fetch_all()
        return {bank.name.lower(): bank.id for bank in bank_names}

    @classmethod
    async def get_account_type_ids_map(cls):
        account_type_list = await AccountType.fetch_all()
        return {account_type.name.lower(): account_type.id for account_type in account_type_list}

    @classmethod
    async def get_salutation_ids_map(cls):
        salutation_list = await Salutation.fetch_all()
        return {salutation.name.lower(): salutation.id for salutation in salutation_list}

    @classmethod
    async def get_user_role_ids_map(cls):
        user_role_list = await UserRole.fetch_all()
        return {user_role.name.lower(): user_role.id for user_role in user_role_list}

    @classmethod
    async def get_designation_ids_map(cls):
        designation_list = await Designation.fetch_all()
        return {designation.name.lower(): designation.id for designation in designation_list}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        state_dict = await cls.get_state_ids_map()
        city_dict = await cls.get_city_ids_map()
        pincode_dict = await cls.get_pincode_ids_map()
        bank_dict = await cls.get_bank_ids_map()
        account_type_dict = await cls.get_account_type_ids_map()
        salutation_dict = await cls.get_salutation_ids_map()
        user_role_dict = await cls.get_user_role_ids_map()
        designation_dict = await cls.get_designation_ids_map()

        dataframe.rename(columns={
            'Insurance Company Name': 'name',
            'Code': 'code',
            'UIN': 'uin',
            'CIN': 'cin',
            'Irda Registration No': 'irda_registration_no',
            'State Name': 'state_id',
            'City Name': 'city_id',
            'Pincode': 'pincode_id',
            'Account Type': 'account_type_id',
            'Salutation': 'salutation_id',
            'User Role': 'user_role_id',
            'Designation': 'designation_id',
            'Cms Bank Name': 'cms_bank_name_id',
            'Servicing Office Address': 'servicing_office_address',
            # 'Registered Office Address': 'registered_office_address',
            # 'Hsn Sac': 'hsn_sac',
            'Insurer Logo': 'insurer_logo',
            'Pan Number': 'pan_number',
            # 'Gstin Number': 'gstin_number',
            # 'Description Of Service': 'description_of_service',
            # 'Place Of Supply': 'place_of_supply',
            # 'Invoice Number': 'invoice_number',
            'Digital Signature': 'digital_signature',
            # 'Limitations As To Us': 'limitations_as_to_us',
            # 'Drivers Clause': 'drivers_clause',
            'Grievance Clause': 'grievance_clause',
            # 'Disclaimer': 'disclaimer',
            # 'Important Notice': 'important_notice',
            # 'Note': 'note',
            # 'Fastag Clause': 'fastag_clause',
            # 'Puc Clause': 'puc_clause',
            # 'Limits Of Liability Clause': 'limits_of_liability_clause',
            # 'Compulsory Deductible': 'compulsory_deductible',
            # 'Cpa Sum Insured For Liability Clause': 'cpa_sum_insured_for_liability_clause',
            'Status': 'is_active',
            'Ic Address 1': 'ic_address_1',
            'Ic Address 2': 'ic_address_2',
            'Ic Address 3': 'ic_address_3',
            'Landline No': 'landline_no',
            'Helpdesk No': 'helpdesk_no',
            'Ic Email': 'ic_email',
            'Website Address': 'website_address',
            'Service Tax Code No': 'service_tax_code_no',
            'Service Tax Registration No': 'service_tax_registration_no',
            'Authorized Signatory Name': 'authorized_signatory_name',
            'Authorized Signatory Designation': 'authorized_signatory_designation',
            'Agency Name': 'agency_name',
            'Agency Code': 'agency_code',
            'Deposit Bank Name': 'deposit_bank_id',
            'Deposit Account No': 'deposit_account_no',
            'Payment Collection Address': 'payment_collection_address',
            'Payment Collection Landline No': 'payment_collection_landline_no',
            'Payment Collection Mobile No': 'payment_collection_mobile_no',
            'Transfer Fee': 'transfer_fee',
            'Endorsment Charge': 'endorsment_charge',
            'Endorsment Status': 'endorsment_status',
            'Cancellation Email': 'cancellation_email',
            'Claim Email': 'claim_email',
            'Endorsment Email': 'endorsment_email',
            'Ncb Carry Forward Email': 'ncb_carry_forward_email',
            'Break In Case Email': 'break_in_case_email',
            'Master Email': 'master_email',
            'First Name': 'first_name',
            'Middle Name': 'middle_name',
            'Last Name': 'last_name',
            'User Landline No': 'user_landline_no',
            'User Mobile No': 'user_mobile_no',
            'User Email': 'user_email',
            'User Status': 'user_status',
            'Cms Client Code': 'cms_client_code',

        }, inplace=True)
        # try:
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe = dataframe.astype({'irda_registration_no': 'string', 'landline_no': 'string',
                                      'helpdesk_no': 'string', 'service_tax_code_no': 'string',
                                      'service_tax_registration_no': 'string', 'agency_code': 'string',
                                      'deposit_account_no': 'string', 'payment_collection_landline_no': 'string',
                                      'user_landline_no': 'string', 'user_mobile_no': 'string',
                                      'cms_client_code': 'string', 'pincode_id': 'string',
                                      'payment_collection_mobile_no': 'string'
                                      })
        dataframe['servicing_office_address'] = dataframe['servicing_office_address'].replace(to_replace=np.nan,
                                                                                              value='')
        # dataframe['registered_office_address'] = dataframe['registered_office_address'].replace(to_replace=np.nan,
        #                                                                                         value='')
        # dataframe['hsn_sac'] = dataframe['hsn_sac'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['description_of_service'] = dataframe['description_of_service'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['place_of_supply'] = dataframe['place_of_supply'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['invoice_number'] = dataframe['invoice_number'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['limitations_as_to_us'] = dataframe['limitations_as_to_us'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['drivers_clause'] = dataframe['drivers_clause'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['disclaimer'] = dataframe['disclaimer'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['important_notice'] = dataframe['important_notice'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['note'] = dataframe['note'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['fastag_clause'] = dataframe['fastag_clause'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['puc_clause'] = dataframe['puc_clause'].replace(
        #     to_replace=np.nan, value='')
        # dataframe['limits_of_liability_clause'] = dataframe['limits_of_liability_clause'].replace(to_replace=np.nan,
        #                                                                                           value='')
        # dataframe['compulsory_deductible'] = dataframe['compulsory_deductible'].replace(
        #     to_replace=np.nan, value=0)
        # dataframe['cpa_sum_insured_for_liability_clause'] = dataframe['cpa_sum_insured_for_liability_clause'].replace(
        #     to_replace=np.nan, value=0)

        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")
        # new fields
        dataframe['ic_address_2'] = dataframe['ic_address_2'].replace(
            to_replace=np.nan, value='')
        dataframe['ic_address_3'] = dataframe['ic_address_3'].replace(
            to_replace=np.nan, value='')
        dataframe["state_id"] = dataframe["state_id"].apply(
            lambda x: validate_id(state_dict, x))
        dataframe["city_id"] = dataframe["city_id"].apply(
            lambda x: validate_id(city_dict, x))
        dataframe["pincode_id"] = dataframe["pincode_id"].apply(
            lambda x: validate_id(pincode_dict, x))
        dataframe['authorized_signatory_designation'] = dataframe['authorized_signatory_designation'].replace(
            to_replace=np.nan,
            value='')
        dataframe['deposit_bank_id'] = dataframe['deposit_bank_id'].apply(
            lambda x: validate_id(bank_dict, x))
        dataframe["account_type_id"] = dataframe["account_type_id"].apply(
            lambda x: validate_id(account_type_dict, x))
        dataframe['payment_collection_landline_no'] = dataframe['payment_collection_landline_no'].replace(
            to_replace=np.nan, value='')
        dataframe['payment_collection_mobile_no'] = dataframe['payment_collection_mobile_no'].replace(to_replace=np.nan,
                                                                                                      value='')
        dataframe['ncb_carry_forward_email'] = dataframe['ncb_carry_forward_email'].replace(
            to_replace=np.nan, value='')
        dataframe['break_in_case_email'] = dataframe['break_in_case_email'].replace(
            to_replace=np.nan, value='')
        dataframe["salutation_id"] = dataframe["salutation_id"].apply(
            lambda x: validate_id(salutation_dict, x))
        dataframe['middle_name'] = dataframe['middle_name'].replace(
            to_replace=np.nan, value='')
        dataframe["user_role_id"] = dataframe["user_role_id"].apply(
            lambda x: validate_id(user_role_dict, x))
        dataframe["designation_id"] = dataframe["designation_id"].apply(
            lambda x: validate_id(designation_dict, x))
        dataframe['user_mobile_no'] = dataframe['claim_email'].replace(
            to_replace=np.nan, value='')
        dataframe['user_status'] = dataframe["user_status"].apply(
            lambda x: x == "yes")
        dataframe['endorsment_status'] = dataframe["endorsment_status"].apply(lambda x: x == "yes")
        dataframe["cms_bank_name_id"] = dataframe["cms_bank_name_id"].apply(
            lambda x: validate_id(bank_dict, x))
        dataframe['cms_client_code'] = dataframe['cms_client_code'].replace(
            to_replace=np.nan, value='')
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['code'].isna()) | (data['uin'].isna()) | (
            data['irda_registration_no'].isna()) | (data['insurer_logo'].isna()) | (data['pan_number'].isna())
                          | (data['digital_signature'].isna()) | (data['grievance_clause'].isna()) | (
                              data['ic_address_1'].isna())
                          | (data['landline_no'].isna()) | (data['helpdesk_no'].isna()) | (data['ic_email'].isna())
                          | (data['website_address'].isna()) | (data['service_tax_code_no'].isna())
                          | (data['service_tax_registration_no'].isna())
                          | (data['authorized_signatory_name'].isna())
                          | (data['agency_name'].isna()) | (data['agency_code'].isna())
                          | (data['deposit_account_no'].isna()) | (data['payment_collection_address'].isna())
                          | (data['transfer_fee'].isna())
                          | (data['endorsment_charge'].isna()) | (data['cancellation_email'].isna())
                          | (data['master_email'].isna())
                          | (data['claim_email'].isna())
                          | (data['endorsment_email'].isna()) | (data['first_name'].isna())
                          | (data['last_name'].isna()) | (data['user_landline_no'].isna()) | (
                              data['user_email'].isna()) | (data['is_active'].isna())]
        data['registered_office_address'] = data.apply(
            lambda x: " | ".join([x['ic_address_1'], x['ic_address_2'], x['ic_address_3']]), axis=1)
        if nan_values.values.size:
            return nan_values

        return dataframe


class InsurerLocalOfficeInsert(BaseInsert):
    SQLALCHEMY_MODEL = InsurerLocalOffice

    @classmethod
    async def get_insurer_ids_map(cls):
        insurer_list = await Insurer.fetch_all()
        return {insurer.name.lower(): insurer.id for insurer in insurer_list}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        state_dict = await cls.get_state_ids_map()
        city_dict = await cls.get_city_ids_map()
        pincode_dict = await cls.get_pincode_ids_map()
        insurer_dict = await cls.get_insurer_ids_map()
        dataframe.rename(columns={
            'Insurance Company': 'insurer_id',
            'Local Office Code': 'local_office_code',
            'Gst In': 'gst_in',
            'Address 1': 'address_1',
            'Address 2': 'address_2',
            'Address 3': 'address_3',
            'Dealer State': 'dealer_state_id',
            'Dealer City': 'dealer_city_id',
            'Pincode': 'pincode_id',
            'Email': 'email',
            'Landline No': 'landline_no',
            'Mobile No': 'mobile_no',
            'Helpdesk No': 'helpdesk_no',
            'Status': 'is_active'

        }, inplace=True)
        dataframe = dataframe.astype({
            "pincode_id": "string", "local_office_code": "string", "landline_no": "string",
            "mobile_no": "string", "helpdesk_no": "string",
        })
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["insurer_id"] = dataframe["insurer_id"].apply(
            lambda x: validate_id(insurer_dict, x))
        dataframe["address_2"] = dataframe["address_2"].replace(
            to_replace=np.nan, value='')
        dataframe["address_3"] = dataframe["address_3"].replace(
            to_replace=np.nan, value='')
        dataframe["dealer_state_id"] = dataframe["dealer_state_id"].apply(
            lambda x: validate_id(state_dict, x))
        dataframe["dealer_city_id"] = dataframe["dealer_city_id"].apply(
            lambda x: validate_id(city_dict, x))
        dataframe["pincode_id"] = dataframe["pincode_id"].apply(
            lambda x: validate_id(pincode_dict, x))
        dataframe["landline_no"] = dataframe["landline_no"].replace(
            to_replace=np.nan, value='')
        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['insurer_id'].isna()) | (data['local_office_code'].isna())
                          | (data['gst_in'].isna()) | (data['address_1'].isna())
                          | (data['dealer_state_id'].isna()) | (data['dealer_city_id'].isna())
                          | (data['pincode_id'].isna()) | (data['email'].isna()) | (data['mobile_no'].isna())
                          | (data['helpdesk_no'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


class InsurerDealerMappingInsert(BaseInsert):
    SQLALCHEMY_MODEL = ICDealerMapping

    @classmethod
    async def get_insurer_ids_map(cls):
        insurer_list = await Insurer.fetch_all()
        return {insurer.name.lower(): insurer.id for insurer in insurer_list}

    @classmethod
    async def get_ic_local_office_ids_map(cls):
        ic_local_office_list = await InsurerLocalOffice.fetch_all()
        return {ic_local_office.local_office_code.lower(): ic_local_office.id
                for ic_local_office in ic_local_office_list}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        state_dict = await cls.get_state_ids_map()
        city_dict = await cls.get_city_ids_map()
        insurer_dict = await cls.get_insurer_ids_map()
        ic_local_office_dict = await cls.get_ic_local_office_ids_map()
        payment_mode_dict = await cls.get_payment_mode_ids_map()
        dataframe.rename(columns={
            'Insurance Company': 'insurer_id',
            'Dealer Name': 'dealer_name',
            'Dealer Code': 'dealer_code',
            'Dealer State': 'dealer_state',
            'Dealer City': 'dealer_city',
            'Local Office State': 'local_office_state',
            'Local Office Code': 'local_office_code',
            'Payment Mode Code New': 'payment_mode_code_new',
            'Payment Mode Code Renew': 'payment_mode_code_renew',
            'Status': 'is_active',

        }, inplace=True)
        dataframe = dataframe.astype({
            "dealer_code": "string"
        })
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["insurer_id"] = dataframe["insurer_id"].apply(
            lambda x: validate_id(insurer_dict, x))
        dataframe["dealer_state"] = dataframe["dealer_state"].apply(
            lambda x: validate_id(state_dict, x))
        dataframe["dealer_city"] = dataframe["dealer_city"].apply(
            lambda x: validate_id(city_dict, x))
        dataframe["local_office_state"] = dataframe["local_office_state"].apply(
            lambda x: validate_id(state_dict, x))
        dataframe["local_office_code"] = dataframe["local_office_code"].apply(
            lambda x: validate_id(ic_local_office_dict, x)).replace(to_replace=np.nan, value=None)
        dataframe["payment_mode_code_new"] = dataframe["payment_mode_code_new"].apply(
            lambda x: validate_id(payment_mode_dict, x))
        dataframe["payment_mode_code_renew"] = dataframe["payment_mode_code_renew"].apply(
            lambda x: validate_id(payment_mode_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['dealer_name'].isna()) | (data['dealer_code'].isna()) |
                          (data['dealer_state'].isna()) | (data['dealer_city'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


class AddonInsert(BaseInsert):
    SQLALCHEMY_MODEL = Addon

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")

        return dataframe


class BundleInsert(BaseInsert):
    SQLALCHEMY_MODEL = Bundle

    @classmethod
    async def get_insurer_ids_map(cls):
        insurers = await Insurer.fetch_all()
        return {insurer.name.lower(): insurer.id for insurer in insurers}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        insurer_dict = await cls.get_insurer_ids_map()
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe.rename(columns={
            'insurer_name': 'insurer_id'
        }, inplace=True)
        dataframe["insurer_id"] = dataframe["insurer_id"].apply(
            lambda x: validate_id(insurer_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")

        return dataframe


class AddonBundleInsert(BaseInsert):
    SQLALCHEMY_MODEL = AddonBundle

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        addon_dict = await cls.get_addon_ids_map()
        bundle_dict = await cls.get_bundle_ids_map()
        dataframe.rename(columns={
            'addon_name': 'addon_id',
            'bundle_name': 'bundle_id'
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["addon_id"] = dataframe["addon_id"].apply(
            lambda x: validate_id(addon_dict, x))
        dataframe["bundle_id"] = dataframe["bundle_id"].apply(
            lambda x: validate_id(bundle_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(
            lambda x: x == "yes")

        return dataframe
