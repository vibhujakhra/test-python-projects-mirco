from sqladmin import ModelAdmin

from app.models.location import Country, State, City, Rto, RtoZone


class CountryDetailAdmin(ModelAdmin, model=Country):
    column_list = [Country.id, Country.name]


class StateDetailAdmin(ModelAdmin, model=State):
    column_list = [State.id, State.name, State.country_id, State.gst_code]


class CityDetailAdmin(ModelAdmin, model=City):
    column_list = [City.id, City.name, City.state_id]


class RtoDetailAdmin(ModelAdmin, model=Rto):
    column_list = [Rto.id, Rto.name, Rto.city_id, Rto.code, Rto.is_active]


class RtoZoneDetailAdmin(ModelAdmin, model=RtoZone):
    column_list = [RtoZone.id, RtoZone.zone_name]
