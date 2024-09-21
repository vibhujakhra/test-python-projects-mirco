import logging
import numpy as np
import pandas as pd
from pandas import DataFrame
from rb_utils.database import sqldb
from sqlalchemy import select

from app.data_insertion.base import BaseInsert
from app.models.location import City, State, Pincode, Rto, RtoZone, Region, Country, CityCluster, RtoCluster, \
    CityClusterCityMapping, RtoClusterRtoMapping
from app.utils.service import validate_id

logger = logging.getLogger('api')


# insert to country table
class CountryInsert(BaseInsert):
    SQLALCHEMY_MODEL = Country

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        data = dataframe
        nan_values = data[(data['name'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


# insert to state table

class StateInsert(BaseInsert):
    SQLALCHEMY_MODEL = State

    @classmethod
    async def get_country_ids_map(cls) -> dict:
        countries = await Country.fetch_all()
        return {country.name.lower(): country.id for country in countries}

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        country_dict = await cls.get_country_ids_map()
        region_dict = await cls.get_region_ids_map()
        dataframe.rename(columns={
            'Country Name': 'country_id',
            'State Name': 'name',
            'Region': 'region',
            'Gst Code': 'gst_code',
            'Status': 'is_active',
        }, inplace=True)

        dataframe["country_id"] = dataframe["country_id"].apply(lambda x: validate_id(country_dict, x))
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe = dataframe.astype({"gst_code": 'string'})
        dataframe['gst_code'] = dataframe['gst_code'].replace(to_replace=np.nan, value='')
        dataframe['region'] = dataframe['region'].apply(lambda x: validate_id(region_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['country_id'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values

        return dataframe


# insert to city table

class CityInsert(BaseInsert):
    SQLALCHEMY_MODEL = City

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        state_dict = await cls.get_state_ids_map()

        dataframe.rename(columns={
            'City Name': 'name',
            'State Name': 'state_id',
            'Status': 'is_active',
        }, inplace=True)

        dataframe["state_id"] = dataframe["state_id"].apply(lambda x: validate_id(state_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['state_id'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values

        return dataframe


# insert to pincode

class PincodeInsert(BaseInsert):
    SQLALCHEMY_MODEL = Pincode

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        city_dict = await cls.get_city_ids_map()
        state_dict = await cls.get_state_ids_map()
        dataframe.rename(columns={
            'Pincode': 'name',
            'State Name': 'state_id',
            'City Name': 'city_id',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe = dataframe.astype({"name": "string"})
        dataframe["city_id"] = dataframe["city_id"].apply(lambda x: validate_id(city_dict, x))
        dataframe["state_id"] = dataframe["state_id"].apply(lambda x: validate_id(state_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['city_id'].isna()) | (data['state_id'].isna())
                          | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


# insert to rto zone

class RtoZoneInsert(BaseInsert):
    SQLALCHEMY_MODEL = RtoZone

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe.rename(columns={
            'Zone Name': 'zone_name',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['zone_name'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


# insert to rto

class RtoInsert(BaseInsert):
    SQLALCHEMY_MODEL = Rto

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        city_dict = await cls.get_city_ids_map()
        rto_zone_dict = await cls.get_rto_zone_ids_map()
        state_dict = await cls.get_state_ids_map()
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe.rename(columns={
            'Rto Name': 'name',
            'City Name': 'city_id',
            'State Name': 'state_id',
            'Zone Name': 'rto_zone_id',
            'Rto Code': 'code',
            'Status': 'is_active',

        }, inplace=True)
        dataframe["state_id"] = dataframe["state_id"].apply(lambda x: validate_id(state_dict, x))
        dataframe["city_id"] = dataframe["city_id"].apply(lambda x: validate_id(city_dict, x))
        dataframe["rto_zone_id"] = dataframe["rto_zone_id"].apply(lambda x: validate_id(rto_zone_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['city_id'].isna()) | (data['rto_zone_id'].isna())
                          | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


class RegionInsert(BaseInsert):
    SQLALCHEMY_MODEL = Region

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        rto_zone_dict = await cls.get_rto_zone_ids_map()
        dataframe.rename(columns={
            'Region Name': 'name',
            'Zone Name': 'rto_zone_id',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["rto_zone_id"] = dataframe["rto_zone_id"].apply(lambda x: validate_id(rto_zone_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        nan_values = data[(data['name'].isna()) | (data['rto_zone_id'].isna()) | (data['is_active'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe


class CityClusterInsert(BaseInsert):
    SQLALCHEMY_MODEL = CityCluster
    SQLALCHEMY_MODEL_ = CityClusterCityMapping

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        res = {}
        city_dict = await cls.get_city_ids_map()
        dataframe.rename(columns={
            'City Cluster name': 'name',
            'Status': 'is_active'
        }, inplace=True)
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        city_cluster_dict = dataframe[['name', 'is_active']]
        for city_cluster in city_cluster_dict.to_dict(orient="records"):
            query = await sqldb.execute(select(CityCluster).where(CityCluster.name == city_cluster["name"]))
            city_cluster_data = query.scalars().all()
            if city_cluster_data:
                cluster_dict = await cls.get_city_cluster_ids_map()
            else:
                await CityCluster.create(**{"name": city_cluster["name"]})
                cluster_dict = await cls.get_city_cluster_ids_map()
        dataframe.rename(columns={
            'name': 'city_cluster_id',
            'City name': 'city_id',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["city_id"] = dataframe["city_id"].apply(lambda x: validate_id(city_dict, x))
        dataframe["city_cluster_id"] = dataframe["city_cluster_id"].apply(lambda x: validate_id(cluster_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        try:
            sqldb.add_all([cls.SQLALCHEMY_MODEL_(**i) for i in dataframe.to_dict(orient="records")])
            await sqldb.commit()
            res.update(
                {"message": f"{len(dataframe.index)}   City cluster mapping Records inserted successfully"})
        except Exception as e:
            logger.exception(str(e))
            res.update({"error": "City Cluster Mapping Records are incorrect"})
        return res


class RtoClusterInsert(BaseInsert):
    SQLALCHEMY_MODEL = RtoCluster
    SQLALCHEMY_MODEL_ = RtoClusterRtoMapping

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        res = {}
        rto_dict = await cls.get_rto_ids_map()
        dataframe.rename(columns={
            'Rto Cluster name': 'name',
            'Status': 'is_active'
        }, inplace=True)
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        rto_cluster_dict = dataframe[['name', 'is_active']]
        for rto_cluster in rto_cluster_dict.to_dict(orient="records"):
            query = await sqldb.execute(select(RtoCluster).where(RtoCluster.name == rto_cluster["name"]))
            rto_cluster_data = query.scalars().all()
            if rto_cluster_data:
                cluster_dict = await cls.get_rto_cluster_ids_map()
            else:
                await RtoCluster.create(**{"name": rto_cluster["name"]})
                cluster_dict = await cls.get_rto_cluster_ids_map()
        dataframe.rename(columns={
            'name': 'rto_cluster_id',
            'Rto': 'rto_id',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["rto_id"] = dataframe["rto_id"].apply(lambda x: validate_id(rto_dict, x))
        dataframe["rto_cluster_id"] = dataframe["rto_cluster_id"].apply(lambda x: validate_id(cluster_dict, x))
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        try:
            sqldb.add_all([cls.SQLALCHEMY_MODEL_(**i) for i in dataframe.to_dict(orient="records")])
            await sqldb.commit()
            res.update(
                {"message": f"{len(dataframe.index)}  Rto cluster mapping Records inserted successfully"})
        except Exception as e:
            logger.exception(str(e))
            res.update({"error": "RTo Cluster Mapping Records are incorrect"})
        return res
