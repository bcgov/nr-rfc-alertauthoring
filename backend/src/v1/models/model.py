# coding: utf-8
import datetime
from typing import List, Optional

from sqlalchemy import UniqueConstraint

# from sqlalchemy import MetaData
from sqlmodel import Field, Relationship, SQLModel

from ...core.config import Settings

default_schema = Settings.DEFAULT_SCHEMA
# metadata = MetaData(schema=default_schema)


class Subbasins(SQLModel, table=True):
    """
    not currently in use, will be used later should we want to emit events
    associated with basins / subbasins.

    :param SQLModel: inherits from SQLModel
    :type SQLModel: SQLModel
    :param table: _description_, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}
    # __tablename__ = f"{default_schema}.subbasins"
    # metadata = meta
    # TODO: rename this to subbasin_id in migration file
    subbasin_id: Optional[int] = Field(default=None, primary_key=True)
    sub_basin_name: str = Field(nullable=False)
    basins: List["Basins"] = Relationship(back_populates="subbasins")


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

    # junction_id: Optional["Alert_Areas"]
    basin_id: Optional[int] = Field(default=None, primary_key=True)


class AlertsBase(SQLModel):
    alert_description: str = Field(nullable=False)
    # todo: come back and verify that this creates a varchar or something that
    #       can accomodate a lot of text
    alert_hydro_conditions: str = Field(nullable=False)
    alert_meteorological_conditions: str = Field(nullable=False)
    alert_created: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    alert_updated: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    author_name: str = Field(nullable=True)

    # TODO: could further normalize and create a status table...
    alert_status: str = Field(nullable=False, default="active")


class AlertsRead(AlertsBase):
    """
    model for requesting alert data (read), inherits from Base alert and
    adds the id field

    :param Alerts: _description_
    :type Alerts: _type_
    """

    alert_id: Optional[int] = Field(default=None, primary_key=True)


class Alert_Areas(SQLModel, table=True):
    """
    This table (junction table) manages the relationship between an alert event and:
        * the basins impacted
        * the alert level for each basin that is impacted

    :param SQLModel: _description_
    :type SQLModel: _type_
    """

    __table_args__ = (
        UniqueConstraint("alert_id", "basin_id", "alert_level_id"),
        {"schema": default_schema},
    )

    # __tablename__ = f"{default_schema}.alert_areas"

    # metadata = meta

    # alert_area_id: int = Field(default=None, primary_key=True)
    alert_id: int = Field(
        default=None, foreign_key=f"{default_schema}.alerts.alert_id", primary_key=True
    )
    basin_id: int = Field(
        default=None, foreign_key=f"{default_schema}.basins.basin_id", primary_key=True
    )
    alert_level_id: int = Field(
        default=None,
        foreign_key=f"{default_schema}.alert_levels.alert_level_id",
        primary_key=True,
    )
    basin: "Basins" = Relationship(back_populates="basin_links")
    alert_level: "Alert_Levels" = Relationship(back_populates="alert_level_links")
    alert: "Alerts" = Relationship(back_populates="alert_links")


# class AlertBasinLevels(Alert_Areas):


class Alerts(AlertsRead, table=True):
    """
    The definition for the database table that will store alerts
    relates to junction table Alert_Areas

    :param AlertsRead: the inheriting model
    :type AlertsRead: SQLModel
    :param table: Tells sql model that this is a table def, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}

    alert_links: List["Alert_Areas"] = Relationship(back_populates="alert")


class Basins(BasinsRead, table=True):
    """
    model for basins table, used to identify area that an alert will apply to

    :param BasinsRead: _description_
    :type BasinsRead: _type_
    :param table: _description_, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}
    # __tablename__ = f"{default_schema}.basins"

    subbasins_id: Optional[int] = Field(
        default=None, foreign_key=f"{default_schema}.subbasins.subbasin_id"
    )
    subbasins: Optional[Subbasins] = Relationship(back_populates="basins")

    basin_links: List[Alert_Areas] = Relationship(back_populates="basin")


class Alert_Levels_Read(SQLModel):
    alert_level_id: int
    alert_level: str


class Alert_Levels(Alert_Levels_Read, table=True):
    """
    Contains the allowed values for alert levels

    :param SQLModel: _description_
    :type SQLModel: _type_
    """

    __table_args__ = {"schema": default_schema}
    alert_level_id: int = Field(default=None, primary_key=True)
    alert_level: str = Field(nullable=False)

    alert_level_links: List[Alert_Areas] = Relationship(back_populates="alert_level")


class Cap_Event_Base(SQLModel):
    """
    base model for cap events, used for write

    This table is used to track the cap events that have been emitted.  When
    a new alert is created logic will be used to determine what cap events
    need to be emitted.  To calculate what events need to be emitted knowing
    what the previous events that have been emitted are required.

    :param SQLModel: _description_
    :type SQLModel: _type_
    """

    alert_id: int = Field(default=None, foreign_key=f"{default_schema}.alerts.alert_id")
    alert_level_id: int = Field(
        default=None, foreign_key=f"{default_schema}.alert_levels.alert_level_id"
    )
    cap_event_status: str = Field(nullable=False, default="active")
    cap_event_created_date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    cap_event_updated_date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class Cap_Event(Cap_Event_Base, table=True):
    """
    table model used for read and database definition

    :param Cap_Event_Base: inheriting from the base cap event model that is used
                           for write operations
    :type Cap_Event_Base: SQLModel
    :param table: indicate that this is a table model, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}

    cap_event_id: int = Field(default=None, primary_key=True)


class Cap_Event_Areas(SQLModel, table=True):
    """
    a junction table that manages the relationship between cap events and the
    basins that are impacted by the event

    :param SQLModel: inherits from SQLModel
    :type SQLModel: SQLModel
    :param table: specifying that this model defines a table, defaults to True
    :type table: bool, optional
    """

    cap_event_area_id: int = Field(default=None, primary_key=True)
    basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.basin_id")


class Alert_Areas_Read(SQLModel):
    basin: BasinsRead
    alert_level: Alert_Levels_Read


class Alert_Basins(AlertsRead):
    alert_id: int
    # alert_links: List[Alert_Areas]
    alert_links: List[Alert_Areas_Read]
