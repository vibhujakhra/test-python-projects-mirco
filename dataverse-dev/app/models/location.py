from datetime import datetime

from rb_utils.database.sql.sql_base import Base
from rb_utils.database.sql.sql_crud_operations import SQLBaseCrud
from sqlalchemy import Column, ForeignKey, Integer, Boolean, VARCHAR, DateTime
from sqlalchemy.orm import relationship


class Config:
    orm_mode = True


class TimeStamp:
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime)


class Country(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "country"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)


class RtoZone(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "rto_zone"
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_type = Column(VARCHAR, nullable=True)
    zone_name = Column(VARCHAR, nullable=True)
    is_active = Column(Boolean, default=True)


class Region(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "region"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    group_type = Column(VARCHAR, nullable=True)
    rto_zone_id = Column(Integer, ForeignKey(RtoZone.id))
    is_active = Column(Boolean, default=True)


class State(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    group_type = Column(VARCHAR, nullable=True)
    code = Column(VARCHAR, unique=False, nullable=True)
    zone = Column(VARCHAR, unique=False, nullable=True)
    region = Column(Integer, ForeignKey(Region.id), nullable=True)
    gst_code = Column(VARCHAR)
    country_id = Column(Integer, ForeignKey(Country.id))
    is_union_territory = Column(Boolean, default=False, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)


class City(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    code = Column(VARCHAR, unique=False, nullable=True)
    state_id = Column(Integer, ForeignKey(State.id))
    is_active = Column(Boolean, default=True)


class Pincode(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "pincode"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR, nullable=False)
    state_id = Column(Integer, ForeignKey(State.id))
    city_id = Column(Integer, ForeignKey(City.id))
    is_active = Column(Boolean, default=True)


class Rto(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "rto"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    code = Column(VARCHAR, unique=False, nullable=True)
    city_id = Column(Integer, ForeignKey(City.id))
    city = relationship('City')
    state_id = Column(Integer, ForeignKey(State.id))
    state = relationship('State')
    rto_zone_id = Column(Integer, ForeignKey(RtoZone.id))
    rto_zone = relationship('RtoZone')
    is_active = Column(Boolean, default=True)


class RtoCluster(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "rto_cluster"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    code = Column(VARCHAR)
    is_active = Column(Boolean, default=True)


class RtoClusterRtoMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "rto_cluster_rto_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rto_id = Column(Integer, ForeignKey(Rto.id))
    rto_cluster_id = Column(Integer, ForeignKey(RtoCluster.id))
    is_active = Column(Boolean, default=True)


class CityCluster(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "city_cluster"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR)
    code = Column(VARCHAR)
    is_active = Column(Boolean, default=True)


class CityClusterCityMapping(TimeStamp, Base, Config, SQLBaseCrud):
    __tablename__ = "city_cluster_city_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    city_id = Column(Integer, ForeignKey(City.id))
    city_cluster_id = Column(Integer, ForeignKey(CityCluster.id))
    is_active = Column(Boolean, default=True)
