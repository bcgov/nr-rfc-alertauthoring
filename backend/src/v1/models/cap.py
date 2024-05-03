import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from src.core.config import Settings
from src.v1.models.basins import BasinBase, Basins, BasinsRead

# from src.v1.models.alerts as alert_models
if TYPE_CHECKING:
    from src.v1.models.alerts import Alert_Levels, Alert_Levels_Base, Alert_Levels_Read

default_schema = Settings.DEFAULT_SCHEMA


class Cap_Event_Base(SQLModel):
    """
    base model for cap events, used for write

    This table is used to track the cap events that have been emitted.  When
    a new alert is created logic will be used to determine what cap events
    what the previous events that have been emitted are required.

    :param SQLModel: _description_
    :type SQLModel: _type_
    """

    alert_id: int = Field(default=None, foreign_key=f"{default_schema}.alerts.alert_id")
    cap_event_status: str = Field(nullable=False, default="active")
    cap_event_created_date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )
    cap_event_updated_date: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )

class Cap_Event_Read(Cap_Event_Base):
    cap_event_id: int = Field(default=None, primary_key=True)


class Cap_Event(Cap_Event_Read, table=True):
    """
    table model used for read and database definition

    :param Cap_Event_Base: inheriting from the base cap event model that is used
                           for write operations
    :type Cap_Event_Base: SQLModel
    :param table: indicate that this is a table model, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}
    alert_level_id: int = Field(
        default=None, foreign_key=f"{default_schema}.alert_levels.alert_level_id"
    )

    event_areas: List["Cap_Event_Areas"] = Relationship(back_populates="event_links")
    alert_level: "Alert_Levels" = Relationship(back_populates="cap_link")


class Cap_Event_Areas_Base(SQLModel):
    cap_event_area_id: int = Field(default=None, primary_key=True)
    #basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.basin_id")

class Cap_Event_Areas_Read(Cap_Event_Areas_Base):
    cap_event_id: int = Field(default=None, foreign_key=f"{default_schema}.cap_event.cap_event_id")
    basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.basin_id")

class Cap_Event_Areas(Cap_Event_Areas_Read, table=True):
    """
    a junction table that manages the relationship between cap events and the
    basins that are impacted by the event

    :param SQLModel: inherits from SQLModel
    :type SQLModel: SQLModel
    :param table: specifying that this model defines a table, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}
    
    event_links: List["Cap_Event"] = Relationship(back_populates="event_areas")
    cap_area_basin: List["Basins"] = Relationship(back_populates="basin_cap_links")

class Cap_Event_Areas_Basins(Cap_Event_Areas_Base):
    # cap_event_area_id: int
    #basin_cap_links: List["BasinsRead"] | None = None
    cap_area_basin: Optional["Basins"] | None = None

# class Alert_Levels_Read_Public()

class Cap_Event_And_Areas(Cap_Event_Read):
    cap_event_id: int
    alert_level: Optional["Alert_Levels_Read"] | None = None 
    event_areas: List["Cap_Event_Areas_Basins"] | None = None
