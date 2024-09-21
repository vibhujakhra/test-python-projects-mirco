from sqladmin import ModelAdmin

from app.models.pricing import CoverRate, TPRate, PARate, AddOnBundlePrice, Depreciation, ODRate, Discount, \
    VoluntaryDeductible, NCB


class CoverRateAdmin(ModelAdmin, model=CoverRate):
    column_list = [CoverRate.id, CoverRate.name, CoverRate.code, CoverRate.valid_from, CoverRate.valid_till,
                   CoverRate.max_amount, CoverRate.cover_percent]


class TPRateAdmin(ModelAdmin, model=TPRate):
    column_list = [TPRate.id, TPRate.vehicle_type, TPRate.fuel_type, TPRate.min_cc, TPRate.valid_from,
                   TPRate.valid_till, TPRate.rate]


class PARateAdmin(ModelAdmin, model=PARate):
    column_list = [PARate.id, PARate.vehicle_type, PARate.insurer_code, PARate.tp_tenure, PARate.cover_code,
                   PARate.valid_from,
                   PARate.valid_till, PARate.per_10k_rate]


class DiscountAdmin(ModelAdmin, model=Discount):
    column_list = [Discount.id, Discount.vehicle_type, Discount.insurer_code, Discount.min_cc, Discount.min_cc,
                   Discount.city_cluster, Discount.business_type, Discount.dealer_code, Discount.fuel_type_id,
                   Discount.city_id, Discount.min_ncb, Discount.max_ncb, Discount.model_id, Discount.renewal_type,
                   Discount.state_id, Discount.rto_code, Discount.vin_no, Discount.city_id, Discount.variant_id,
                   Discount.vehicle_min_age, Discount.vehicle_max_age, Discount.rto_cluster, Discount.valid_from,
                   Discount.valid_till]


class DeductibleAdmin(ModelAdmin, model=VoluntaryDeductible):
    column_list = [VoluntaryDeductible.id, VoluntaryDeductible.name, VoluntaryDeductible.vehicle_type,
                   VoluntaryDeductible.discount_percent,
                   VoluntaryDeductible.deductible, VoluntaryDeductible.valid_from, VoluntaryDeductible.valid_till,
                   VoluntaryDeductible.max_discount]


class NCBAdmin(ModelAdmin, model=NCB):
    column_list = [NCB.id, NCB.business_type, NCB.insurer_code, NCB.claim_count,
                   NCB.is_claimed_last_year, NCB.last_year_ncb, NCB.prev_policy_type, NCB.valid_from, NCB.valid_till,
                   NCB.applicable_ncb]


class AddOnBundlePriceAdmin(ModelAdmin, model=AddOnBundlePrice):
    column_list = [AddOnBundlePrice.id, AddOnBundlePrice.vehicle_type_id,
                   AddOnBundlePrice.min_cc, AddOnBundlePrice.max_cc, AddOnBundlePrice.variant_id,
                   AddOnBundlePrice.vehicle_min_age, AddOnBundlePrice.vehicle_max_age,
                   AddOnBundlePrice.add_on_prev_policy, AddOnBundlePrice.addon_bundle_id, AddOnBundlePrice.is_ncb]


class DepreciationAdmin(ModelAdmin, model=Depreciation):
    column_list = [Depreciation.id, Depreciation.min_vehicle_age,
                   Depreciation.max_vehicle_age, Depreciation.valid_from, Depreciation.valid_till,
                   Depreciation.depreciation_rate]


class ODRateAdmin(ModelAdmin, model=ODRate):
    column_list = [ODRate.id, ODRate.vehicle_type, ODRate.min_vehicle_age, ODRate.max_vehicle_age, ODRate.min_cc,
                   ODRate.max_cc, ODRate.od_term, ODRate.rto_zone, ODRate.rate_percent]
