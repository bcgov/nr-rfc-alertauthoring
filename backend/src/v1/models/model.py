# coding: utf-8
import datetime
from typing import List, Optional

# from sqlalchemy import MetaData
from sqlmodel import Field, Relationship, SQLModel

from ...core.config import Settings

default_schema = Settings.DEFAULT_SCHEMA
# metadata = MetaData(schema=default_schema)

 
class Subbasins(SQLModel, table=True ):
    """
    not currently in use, will be used later should we want to emit events 
    associated with basins / subbasins.

    :param SQLModel: inherits from SQLModel
    :type SQLModel: SQLModel
    :param table: _description_, defaults to True
    :type table: bool, optional
    """
    __table_args__ = {'schema':default_schema}
    #__tablename__ = f"{default_schema}.subbasins"
    #metadata = meta

    id: Optional[int] = Field(default=None, primary_key=True)
    sub_basin_name: str = Field(nullable=False)
    basins: List['Basins'] = Relationship(back_populates="subbasins")


class BasinBase(SQLModel):
    """
    starting point for basin data, used for both read and write

    :param SQLModel: _description_
    :type SQLModel: _type_
    """
    basin_name: str = Field(nullable=False)

class BasinsRead(BasinBase):
    """
    model for requesting basin data (read), inherits from Base basin and 
    adds the id field

    :param BasinBase: _description_
    :type BasinBase: _type_
    """
    id: Optional[int] = Field(default=None, primary_key=True)

class Basins(BasinsRead, table=True):
    """
    model for basins table, used to identify area that an alert will apply to

    :param BasinsRead: _description_
    :type BasinsRead: _type_
    :param table: _description_, defaults to True
    :type table: bool, optional
    """
    __table_args__ = {'schema':default_schema}
    #__tablename__ = f"{default_schema}.basins"

    #metadata = meta

    subbasins_id: Optional[int] = Field(default=None, foreign_key=f"{default_schema}.subbasins.id")
    subbasins: Optional[Subbasins] = Relationship(back_populates="basins")


class Alert_Levels(SQLModel, table=True):
    """
    Contains the allowed values for alert levels

    :param SQLModel: _description_
    :type SQLModel: _type_
    """
    __table_args__ = {'schema':default_schema}
    #__tablename__ = f"{default_schema}.alert_levels"

    #metadata = meta

    alert_level_id: int = Field(default=None, primary_key=True)
    alert_level: str = Field(nullable=False)


class AlertsBase(SQLModel):

    alert_description: str = Field(nullable=False)
    # todo: come back and verify that this creates a varchar or something that 
    #       can accomodate a lot of text
    alert_hydro_conditions: str = Field(nullable=False)
    alert_meteorological_conditions: str = Field(nullable=False)
    created_date: datetime.datetime = Field(default=datetime.datetime.utcnow)
    basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.id")

class AlertsRead(AlertsBase):
    """
    model for requesting alert data (read), inherits from Base alert and 
    adds the id field

    :param Alerts: _description_
    :type Alerts: _type_
    """
    id: Optional[int] = Field(default=None, primary_key=True)

class Alerts(AlertsRead, table=True):
    """
    The definition for the database table that will store alerts

    :param AlertsRead: the inheriting model
    :type AlertsRead: SQLModel
    :param table: Tells sql model that this is a table def, defaults to True
    :type table: bool, optional
    """
    __table_args__ = {'schema':default_schema}
    #__tablename__ = f"{default_schema}.alerts"

    # metadata = meta
    # one to many relationship to alert areas, where the linkages to the alert
    # level table and basins will be managed
    # alert_area_id: Optional[int] = Field(default=None, foreign_key=f"{default_schema}.alert_areas.alert_area_id")

class Alert_Areas(SQLModel, table=True):
    """
    This table manages the relationship between an alert event and:
        * the basins impacted
        * the alert level for each basin that is impacted

    :param SQLModel: _description_
    :type SQLModel: _type_
    """
    __table_args__ = {'schema':default_schema}
    #__tablename__ = f"{default_schema}.alert_areas"

    #metadata = meta


    alert_area_id: int = Field(default=None, primary_key=True)
    alert_id: int = Field(default=None, foreign_key=f"{default_schema}.alerts.id")
    basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.id")
    alert_level_id: int = Field(default=None, foreign_key=f"{default_schema}.alert_levels.alert_level_id")

        