from sqlalchemy import select
from rb_utils.database import sqldb
from rb_utils.database import initiate_database

from settings import CONNECTION_CONFIG

initiate_database(database_type="sql", connection_config=CONNECTION_CONFIG)


def get_session():
    return sqldb