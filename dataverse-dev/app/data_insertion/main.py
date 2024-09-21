import logging
import tempfile
from pandas import DataFrame

from app.data_insertion.base import BaseInsert
from app.data_insertion.script.bank.insert_to_bank import BankInsert, FinancierInsert
from app.data_insertion.script.insurer.insert_to_insurer import InsurerInsert, AddonInsert, BundleInsert, \
    AddonBundleInsert, InsurerLocalOfficeInsert, InsurerDealerMappingInsert
from app.data_insertion.script.location.insert_to_location import CityInsert, CountryInsert, RtoInsert, RegionInsert, \
    CityClusterInsert, RtoClusterInsert, StateInsert, RtoZoneInsert, PincodeInsert
from app.data_insertion.script.vehicle_details.insert_to_vehicle import OemInsert, VehicleModelInsert, VariantInsert, \
    ExShowroomPriceInsert


logger = logging.getLogger("api")


def get_insert_class(data_type: str) -> BaseInsert:
    _class_map = {
        "city": CityInsert,
        "country": CountryInsert,
        "insurer": InsurerInsert,
        "addon": AddonInsert,
        "state": StateInsert,
        "pincode": PincodeInsert,
        "rto_zone": RtoZoneInsert,
        "rto": RtoInsert,
        "oem": OemInsert,
        "model": VehicleModelInsert,
        "variant": VariantInsert,
        "ex_showroom_price": ExShowroomPriceInsert,
        "bundle": BundleInsert,
        "addon_bundle": AddonBundleInsert,
        "bank": BankInsert,
        "financier": FinancierInsert,
        "region": RegionInsert,
        "city_cluster": CityClusterInsert,
        "rto_cluster": RtoClusterInsert,
        "insurer_local_office": InsurerLocalOfficeInsert,
        "insurer_dealer_mapping": InsurerDealerMappingInsert

    }
    return _class_map[data_type]


async def insert_bulk_data(data_type: str, document_df: DataFrame):
    obj = get_insert_class(data_type)
    data = await obj.process_data(dataframe=document_df)
    if not isinstance(data, dict):
        if data.isnull().values.any():
            with tempfile.NamedTemporaryFile(mode='w+b', prefix='RB', suffix='.csv', delete=False) as temp:
                data.to_csv(temp, index=False, na_rep="REQUIRED")
                filename = temp.name
                response = {"status": 1,
                            "filename": filename,
                            "error_rows_no": len(data.index)}
                return response
        data = await obj.insert_data(dataframe=data)
    return data
