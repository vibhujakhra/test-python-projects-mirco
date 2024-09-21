import numpy as np
import pandas as pd
from asyncio.log import logger
from pandas import DataFrame
from rb_utils.database import sqldb
from app.data_insertion.base import BaseInsert
from app.models.vehicle_details import VehicleModel, Variant, SubVariant, ExShowRoomPrice
from app.utils.service import validate_id
from app.models.admin_details import Oem


# pd.options.mode.chained_assignment = None

# insert to oem
class OemInsert(BaseInsert):
    SQLALCHEMY_MODEL = Oem

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


# insert to Vehicle Model

class VehicleModelInsert(BaseInsert):
    SQLALCHEMY_MODEL = VehicleModel

    @classmethod
    async def get_oem_ids_map(cls):
        oems = await Oem.fetch_all()
        return {oem.name.lower(): oem.id for oem in oems}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        oem_dict = await cls.get_oem_ids_map()
        vehicle_class_dict = await cls.get_vehicle_class_ids_map()
        vehicle_type_dict = await cls.get_vehicle_type_ids_map()
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe.rename(columns={
            'Model Name': 'name',
            'Make Name': 'oem_id',
            'Vehicle Class': 'vehicle_class_id',
            'Vehicle Type': 'vehicle_type_id',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["oem_id"] = dataframe["oem_id"].apply(lambda x: validate_id(oem_dict, x))
        dataframe["code"] = dataframe["name"].replace(' ', '_', regex=True)
        dataframe["vehicle_class_id"] = dataframe["vehicle_class_id"].apply(lambda x: validate_id(vehicle_class_dict, x))
        dataframe["vehicle_type_id"] = dataframe["vehicle_type_id"].apply(lambda x: validate_id(vehicle_type_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['oem_id'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


# insert to variant

class VariantInsert(BaseInsert):
    SQLALCHEMY_MODEL = Variant
    SQLALCHEMY_MODEL_SUB = SubVariant

    @classmethod
    async def get_model_ids_map(cls):
        models = await VehicleModel.fetch_all()
        return {model.name.lower(): model.id for model in models}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        res = {}
        model_dict = await cls.get_model_ids_map()
        fuel_type_dict = await cls.get_fuel_type_ids_map()
        dataframe.rename(columns={
            'Variant Name': 'name',
            'Variant Code': 'variant_code',
            'Cubic Capacity': 'cubic_capacity',
            'Kilowatt Range': 'kilowatt_range',
            'Seating Capacity': 'seating_capacity',
            'License Carrying Capacity': 'license_carrying_capacity',
            'Carrying Capacity': 'carrying_capacity',
            'Body Type': 'body_type',
            'Segment Type': 'segment_type',
            'Bifuel': 'is_bifuel',
            'Fuel Type Name': 'fuel_type_id',
            'Model Name': 'model_id',
            'Status': 'is_active',
            'Color': 'color',
            'Tone': 'tone',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe = dataframe.astype({"variant_code": "string"})
        dataframe["model_id"] = dataframe["model_id"].apply(lambda x: validate_id(model_dict, x))
        dataframe["fuel_type_id"] = dataframe["fuel_type_id"].apply(lambda x: validate_id(fuel_type_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        dataframe['kilowatt_range'] = dataframe['kilowatt_range'].replace(to_replace=np.nan, value=0)
        dataframe['license_carrying_capacity'] = dataframe['license_carrying_capacity'].replace(to_replace=np.nan,
                                                                                                value=0)
        dataframe['body_type'] = dataframe['body_type'].replace(to_replace=np.nan, value='')
        dataframe['segment_type'] = dataframe['segment_type'].replace(to_replace=np.nan, value='')
        dataframe['cubic_capacity'] = dataframe['cubic_capacity'].replace(to_replace=np.nan, value=0)
        dataframe['carrying_capacity'] = dataframe['carrying_capacity'].replace(to_replace=np.nan, value=None)
        dataframe["is_bifuel"] = dataframe["is_bifuel"].apply(lambda x: x == "yes")
        variant_data = dataframe[['name', 'variant_code', 'model_id', 'fuel_type_id', 'is_active', 'kilowatt_range',
                                  'license_carrying_capacity', 'body_type', 'segment_type', 'cubic_capacity',
                                  'carrying_capacity', 'is_bifuel', 'seating_capacity', 'created_at', 'modified_at',
                                  ]]
        nan_values = variant_data[(variant_data['name'].isna()) | (variant_data['model_id'].isna()) | (
            variant_data['cubic_capacity'].isna()) | (variant_data['fuel_type_id'].isna()) | (variant_data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values

        sub_variant = dataframe[['created_at', 'modified_at', 'name', 'color', 'tone', 'is_active']]
        nan_values = sub_variant[(sub_variant['tone'].isna()) | (sub_variant['color'].isna())
                                 | (sub_variant['is_active'].isna())]
        if nan_values.values.size:
            return nan_values

        try:
            sqldb.add_all([cls.SQLALCHEMY_MODEL(**i) for i in variant_data.to_dict(orient="records")])
            await sqldb.commit()
            res.update({"message": f"{len(dataframe.index)}   Variant Records inserted successfully"})
        except Exception as e:
            logger.exception(str(e))
            res.update({"error": "variant Records are incorrect"})

        variant_dict = await cls.get_variant_ids_map()
        sub_variant.rename(columns={
            'name': 'variant_id',
        }, inplace=True)
        sub_variant["variant_id"] = sub_variant["variant_id"].apply(lambda x: validate_id(variant_dict, x))
        data = sub_variant
        try:
            sqldb.add_all([cls.SQLALCHEMY_MODEL_SUB(**i) for i in data.to_dict(orient="records")])
            await sqldb.commit()
            res.update({"message": f"{len(variant_data.index)}"
                                   f" variant and {len(data.index)} sub variant Records inserted successfully"})
        except Exception as e:
            logger.exception(str(e))
            res.update({"error": "sub-variant Records are incorrect"})
        return res


class ExShowroomPriceInsert(BaseInsert):
    SQLALCHEMY_MODEL = ExShowRoomPrice

    @classmethod
    def remove_all_null_rows(cls, x, df):
        if sum(x.isnull()) == len(df.columns):
            return x.name

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        ex_showroom_dataframe = dataframe
        if {'id', 'color', 'tone', 'variant_info'}.issubset(ex_showroom_dataframe.columns):
            ex_showroom_dataframe = ex_showroom_dataframe.drop(['id', 'color', 'tone', 'variant_info'], axis=1)
            nan_rows = ex_showroom_dataframe.apply(lambda x: cls.remove_all_null_rows(x, ex_showroom_dataframe),
                                                   axis=1).to_list()[1:]
            ex_showroom_dataframe = ex_showroom_dataframe.drop(nan_rows)
        variant_dict = await cls.get_exshowroom_variant_ids_map()
        state_dict = await cls.get_state_ids_map()
        city_dict = await cls.get_city_ids_map()
        ex_showroom_dataframe["created_at"] = pd.Timestamp("now")
        ex_showroom_dataframe["modified_at"] = pd.Timestamp("now")
        ex_showroom_dataframe.rename(columns={
            'Variant Name': 'variant_id',
            'State Name': 'state_id',
            'City Name': 'city',
            'Model Name': 'model_name',
            'ExShowRoomPrice': 'exShowRoomPrice',
            'Charges Price': 'charges_price',
            'Sub Variant id': 'sub_variant_id',
        }, inplace=True)

        variant_model = ex_showroom_dataframe['variant_id'] + "_" + ex_showroom_dataframe['model_name']
        ex_showroom_dataframe = ex_showroom_dataframe.drop(['model_name', ], axis=1)
        ex_showroom_dataframe["variant_id"] = variant_model.apply(
            lambda x: validate_id(variant_dict, x))
        ex_showroom_dataframe["state_id"] = ex_showroom_dataframe["state_id"].apply(
            lambda x: validate_id(state_dict, x))
        ex_showroom_dataframe["city"] = ex_showroom_dataframe["city"].apply(lambda x: validate_id(city_dict, x))
        ex_showroom_dataframe["charges_price"] = ex_showroom_dataframe["charges_price"].replace(to_replace=np.nan,
                                                                                                value=0)
        data = ex_showroom_dataframe
        nan_values = data[(data['exShowRoomPrice'].isna()) | (data['state_id'].isna()) | (data['variant_id'].isna()) |
                          (data['charges_price'].isna()) | (data['city'].isna()) | (data['sub_variant_id'].isna())
                          | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return ex_showroom_dataframe
