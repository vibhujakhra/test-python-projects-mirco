from sqladmin import ModelAdmin

from app.models.vehicle_details import ExShowRoomPrice, FuelType, SubVariant, Variant, VehicleModel
from app.models.admin_details import Dealer, DesignatedPerson, Oem, SalesManager, Broker


class OemDetailAdmin(ModelAdmin, model=Oem):
    column_list = [Oem.id, Oem.name, Oem.code]


class DealerDetailAdmin(ModelAdmin, model=Dealer):
    column_list = [Dealer.id, Dealer.dealer_name, Dealer.oem_id, Dealer.city_id, Dealer.dealer_code, Dealer.is_active]


class DesignatedPersonDetailAdmin(ModelAdmin, model=DesignatedPerson):
    column_list = [DesignatedPerson.id, DesignatedPerson.designated_person_name, DesignatedPerson.oem_id, DesignatedPerson.dealer_id,
                   DesignatedPerson.is_active]


class SalesManagerDetailAdmin(ModelAdmin, model=SalesManager):
    column_list = [SalesManager.id, SalesManager.sales_manager_name, SalesManager.oem_id, SalesManager.dealer_id,
                   SalesManager.designated_person_id, SalesManager.is_active]


class VehicleDetailAdmin(ModelAdmin, model=VehicleModel):
    column_list = [VehicleModel.id, VehicleModel.name, VehicleModel.code, VehicleModel.is_active]


class VehicleVariantDetailAdmin(ModelAdmin, model=Variant):
    column_list = [Variant.id, Variant.name, Variant.is_active, Variant.model_id, Variant.fuel_type_id,
                   Variant.body_type, Variant.variant_code]


class SubVariantDetailAdmin(ModelAdmin, model=SubVariant):
    column_list = [SubVariant.id, SubVariant.tone, SubVariant.color, SubVariant.variant_id]


class FuelTypeDetailAdmin(ModelAdmin, model=FuelType):
    column_list = [FuelType.id, FuelType.name, FuelType.is_active]


class ExshowroomPriceDetailAdmin(ModelAdmin, model=ExShowRoomPrice):
    column_list = [ExShowRoomPrice.id, ExShowRoomPrice.sub_variant_id, ExShowRoomPrice.city]


class BrokerDetailAdmin(ModelAdmin, model=Broker):
    column_list = [Broker.id, Broker.name, Broker.cin, Broker.category, Broker.validity, Broker.irda_license_no, Broker.address,Broker.category,
                    Broker.mobile, Broker.email]