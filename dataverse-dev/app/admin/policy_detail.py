from sqladmin import ModelAdmin

from app.models.policy_details import PolicyType, VehicleCover, TransactionType, AgreementType, VB64Type, \
    PolicyTypeVehicleCoverMapping
from app.models.vehicle_details import VehicleType


class PolicyDetailAdmin(ModelAdmin, model=PolicyType):
    column_list = [PolicyType.id, PolicyType.name]


class VehicleTypeDetailAdmin(ModelAdmin, model=VehicleType):
    column_list = [VehicleType.id, VehicleType.name]


class TransactionTypeAdmin(ModelAdmin, model=TransactionType):
    column_list = [TransactionType.id, TransactionType.name, TransactionType.code]


class AgreementTypeAdmin(ModelAdmin, model=AgreementType):
    column_list = [AgreementType.id, AgreementType.name, AgreementType.code]


class VB64TypeAdmin(ModelAdmin, model=VB64Type):
    column_list = [VB64Type.id, VB64Type.name, VB64Type.code]
