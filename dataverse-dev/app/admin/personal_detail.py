from sqladmin import ModelAdmin

from app.models.financier import Bank, Financier
from app.models.personal_details import Relation, Salutation


class SalutationDetailAdmin(ModelAdmin, model=Salutation):
    column_list = [Salutation.id, Salutation.name, Salutation.salutation_type]


class BankDetailAdmin(ModelAdmin, model=Bank):
    column_list = [Bank.id, Bank.name]


class FinancierDetailAdmin(ModelAdmin, model=Financier):
    column_list = [Financier.id, Financier.name]


class RelationDetailAdmin(ModelAdmin, model=Relation):
    column_list = [Relation.id, Relation.name]
