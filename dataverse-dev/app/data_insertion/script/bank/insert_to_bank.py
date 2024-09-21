import logging
import pandas as pd
from pandas import DataFrame
from app.data_insertion.base import BaseInsert
from app.models.financier import Bank, Financier

logger = logging.getLogger('api')


class BankInsert(BaseInsert):
    SQLALCHEMY_MODEL = Bank

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe.rename(columns={
            'Bank Name': 'name',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        data["code"] = data.apply(
            lambda x: x['name'].replace(" ", "_"), axis=1).str.lower()
        nan_values = data[(data['name'].isna())]
        if nan_values.values.size:
            return nan_values

        return dataframe


class FinancierInsert(BaseInsert):
    SQLALCHEMY_MODEL = Financier

    @classmethod
    async def process_data(cls, dataframe: DataFrame) -> DataFrame:
        dataframe.rename(columns={
            'Financier Name': 'name',
            'Status': 'is_active',
        }, inplace=True)
        dataframe["created_at"] = pd.Timestamp("now")
        dataframe["modified_at"] = pd.Timestamp("now")
        dataframe["is_active"] = dataframe["is_active"].apply(lambda x: x == "yes")
        data = dataframe
        data["code"] = data.apply(
            lambda x: x['name'].replace(" ", "_"), axis=1).str.lower()
        nan_values = data[(data['name'].isna())]
        if nan_values.values.size:
            return nan_values
        return dataframe
