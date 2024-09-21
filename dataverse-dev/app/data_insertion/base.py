from asyncio.log import logger
import http3
from rb_utils.async_http_client import AsyncHttpClient
from rb_utils.database import sqldb
from rb_utils.database.sql.sql_base import Base
from pandas import DataFrame
from app.models.addons import Addon, Bundle, AddonBundle
from app.models.location import State, City, RtoZone, Rto, Pincode, Region, CityCluster, RtoCluster
from app.models.vehicle_details import FuelType, Variant, VehicleType, VehicleModel, VehicleClass
from app.settings import SERVICE_CREDENTIALS, PAYMENT_LIST_URL

client = http3.AsyncClient()


async def call_api(url: str):
    get_model_data = await client.get(url)
    return get_model_data.json()


class BaseInsert:
    SQLALCHEMY_MODEL: Base

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        pass

    @classmethod
    async def get_payment_mode_ids_map(cls):
        # service_url = SERVICE_CREDENTIALS["muneem"]["dns"] + \
        #     "/api/v1/payment_mode/"
        payment_mode_list = await call_api(PAYMENT_LIST_URL)
        return {payment_mode['name'].lower(): payment_mode['id'] for payment_mode in payment_mode_list}

    @classmethod
    async def get_city_ids_map(cls):
        cities = await City.fetch_all()
        return {city.name.lower(): city.id for city in cities}

    @classmethod
    async def get_state_ids_map(cls) -> dict:
        states = await State.fetch_all()
        return {state.name.lower(): state.id for state in states}

    @classmethod
    async def get_region_ids_map(cls) -> dict:
        regions = await Region.fetch_all()
        return {region.name.lower(): region.id for region in regions}

    @classmethod
    async def get_pincode_ids_map(cls):
        pincode_list = await Pincode.fetch_all()
        return {pincode.name.lower(): pincode.id for pincode in pincode_list}

    @classmethod
    async def get_fuel_type_ids_map(cls):
        fuel_types = await FuelType.fetch_all()
        return {fuel_type.name.lower(): fuel_type.id for fuel_type in fuel_types}

    @classmethod
    async def get_exshowroom_variant_ids_map(cls):
        variants = await Variant.fetch_all()
        models = await VehicleModel.fetch_all()
        vehicle_model_data = {model.id: model.name.lower() for model in models}

        return {variant.name.lower() + "_" + vehicle_model_data[variant.model_id]: variant.id
                for variant in variants}

    @classmethod
    async def get_variant_ids_map(cls):
        variants = await Variant.fetch_all()
        return {variant.name.lower(): variant.id for variant in variants}

    @classmethod
    async def get_vehicle_type_ids_map(cls):
        vehicle_types = await VehicleType.fetch_all()
        return {vehicle_type.name.lower(): vehicle_type.id for vehicle_type in vehicle_types}

    @classmethod
    async def get_vehicle_class_ids_map(cls):
        vehicle_classes = await VehicleClass.fetch_all()
        return {vehicle_class.name.lower(): vehicle_class.id for vehicle_class in vehicle_classes}

    @classmethod
    async def get_addon_ids_map(cls):
        addons = await Addon.fetch_all()
        return {addon.name.lower(): addon.id for addon in addons}

    @classmethod
    async def get_bundle_ids_map(cls):
        bundles = await Bundle.fetch_all()
        return {bundle.name.lower(): bundle.id for bundle in bundles}

    @classmethod
    async def get_addon_bundle_ids_map(cls):
        addons = await AddonBundle.fetch_all()
        return {addon.name.lower(): addon.id for addon in addons}

    @classmethod
    async def get_rto_zone_ids_map(cls):
        rto_zones = await RtoZone.fetch_all()
        return {rto_zone.zone_name.lower(): rto_zone.id for rto_zone in rto_zones}

    @classmethod
    async def get_rto_ids_map(cls):
        rtos = await Rto.fetch_all()
        return {rto.name.lower(): rto.id for rto in rtos}

    @classmethod
    async def get_city_cluster_ids_map(cls):
        city_clusters = await CityCluster.fetch_all()
        return {city_cluster.name.lower(): city_cluster.id for city_cluster in city_clusters}

    @classmethod
    async def get_rto_cluster_ids_map(cls):
        rto_clusters = await RtoCluster.fetch_all()
        return {rto_cluster.name.lower(): rto_cluster.id for rto_cluster in rto_clusters}

    @classmethod
    async def insert_data(cls, dataframe: DataFrame):
        res = {}

        try:
            sqldb.add_all([cls.SQLALCHEMY_MODEL(**i)
                           for i in dataframe.to_dict(orient="records")])
            await sqldb.commit()
            res.update(
                {"message": f"{len(dataframe.index)}  Records inserted successfully"})

        except Exception as e:
            logger.exception(str(e))
            res.update({"error": "Records are incorrect"})
        return res
