from sqladmin import ModelAdmin

from app.models.addons import Bundle
from app.models.coverage_details import GeoExtension, VoluntaryDeductible, PaCover, ncb
from app.models.insurer import Insurer


class GeoExtensionDetailAdmin(ModelAdmin, model=GeoExtension):
    column_list = [GeoExtension.id, GeoExtension.name]


class VoluntaryDeductibleDetailAdmin(ModelAdmin, model=VoluntaryDeductible):
    column_list = [VoluntaryDeductible.id, VoluntaryDeductible.text, VoluntaryDeductible.value]


class NCBDetailAdmin(ModelAdmin, model=ncb):
    column_list = [ncb.id, ncb.name, ncb.value]


class PaCoverDetailAdmin(ModelAdmin, model=PaCover):
    column_list = [PaCover.id, PaCover.text, PaCover.value]


class InsurerDetailAdmin(ModelAdmin, model=Insurer):
    column_list = [Insurer.id, Insurer.name]


class InsurerBundleDetailAdmin(ModelAdmin, model=Bundle):
    column_list = [Bundle.id, Bundle.name, Bundle.insurer_id]
