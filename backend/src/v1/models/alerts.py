# coding: utf-8
import datetime
from typing import List, Optional

from sqlalchemy import UniqueConstraint

# from sqlalchemy import MetaData
from sqlmodel import Field, Relationship, SQLModel

from src.core.config import Settings
from src.v1.models.basins import BasinBase, Basins, BasinsRead
from src.v1.models.cap import Cap_Event

default_schema = Settings.DEFAULT_SCHEMA


class AlertsBase(SQLModel):
    alert_description: str = Field(nullable=False)
    # todo: come back and verify that this creates a varchar or something that
    #       can accomodate a lot of text
    alert_hydro_conditions: str = Field(nullable=False)
    alert_meteorological_conditions: str = Field(nullable=False)
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
    alert_created: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    alert_updated: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )

class Alert_Areas_Read(SQLModel):
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

class Alert_Areas(Alert_Areas_Read, table=True):
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

    basin: "Basins" = Relationship(back_populates="basin_links")
    alert_level: "Alert_Levels" = Relationship(back_populates="alert_level_links")
    alert: "Alerts" = Relationship(back_populates="alert_links")

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

class AlertsWithAreaLevels(AlertsRead, table=False):
    basin: Alert_Areas_Read | None = None

class Alert_Levels_Base(SQLModel):
    alert_level: str

class Alert_Levels_Read(Alert_Levels_Base):
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
    cap_link: Cap_Event = Relationship(back_populates="alert_level")
    cap_hist_link: "Cap_Event_History" = Relationship(back_populates="alert_levels")

class Alert_Areas_Write(SQLModel):
    basin: BasinBase
    alert_level: Alert_Levels_Base

class Alert_Areas_Read(SQLModel):
    basin: BasinsRead
    alert_level: Alert_Levels_Read

class Alert_Basins(AlertsRead):
    alert_id: int
    # alert_links: List[Alert_Areas]
    alert_links: List[Alert_Areas_Read]


class Alert_Basins_Write(AlertsBase):
    alert_links: List[Alert_Areas_Write]
    # alert_links: List[Alert_Areas]


class Alert_History_Base(AlertsBase):
    alert_id: int
    alert_updated: datetime.datetime
    alert_history_created: datetime.datetime


class Alert_History(Alert_History_Base, table=True):
    __table_args__ = {
        "schema": default_schema,
        "comment": "This table is used to track the changes over time of alerts",
    }

    alert_history_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Primary key for the alert history table",
    )
    alert_id: int = Field(default=None, foreign_key=f"{default_schema}.alerts.alert_id")
    alert_description: str = Field(
        nullable=False, description="description of the alert"
    )
    alert_hydro_conditions: str = Field(nullable=False, default="active")
    alert_meteorological_conditions: str = Field(nullable=False, default="active")
    author_name: str = Field(nullable=False, default="active")
    alert_status: str = Field(nullable=False, default="active")
    alert_updated: datetime.datetime = Field(
        description="The timestamp for when this historical record was last changed in the original table"
    )
    alert_history_created: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
        description="The timestamp for when this history record was created",
    )
    alert_history_links: List["Alert_Area_History"] = Relationship(
        back_populates="alert_history"
    )
    # alert_created: datetime.datetime = Field(
    #     default_factory=datetime.datetime.utcnow, nullable=False
    # )


class Alert_Area_History(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("alert_history_id", "basin_id", "alert_level_id"),
        {
            "schema": default_schema,
            "comment": "This table is used to track the changes over time of area and alert levels for a specific alert",
        },
    )
    alert_history_id: int = Field(
        default=None,
        foreign_key=f"{default_schema}.alert_history.alert_history_id",
        description="Primary key for the alert history table",
        primary_key=True,
    )
    basin_id: int = Field(
        default=None,
        foreign_key=f"{default_schema}.basins.basin_id",
        description="Foreign key relationship to the basin associated with this historical record",
        primary_key=True,
    )
    alert_level_id: int = Field(
        default=None,
        foreign_key=f"{default_schema}.alert_levels.alert_level_id",
        description="Foreign key relationship to the alert level associated with this historical record",
        primary_key=True,
    )
    alert_history: "Alert_History" = Relationship(back_populates="alert_history_links")


from .cap import Cap_Event_And_Areas, Cap_Event_History  # noqa: E402

Cap_Event_And_Areas.model_rebuild()
Cap_Event_History.model_rebuild()