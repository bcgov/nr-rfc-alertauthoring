import datetime
from typing import TYPE_CHECKING, List, Optional, Required

from sqlmodel import Field, Relationship, SQLModel

from src.core.config import Settings
from src.v1.models.basins import Basins

# from src.v1.models.alerts as alert_models
if TYPE_CHECKING:
    from src.v1.models.alerts import Alert_Levels, Alert_Levels_Read

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
    # cap_event_status: str = Field(nullable=False, default="create")
    cap_event_status_id: int = Field(default=None, foreign_key=f"{default_schema}.cap_event_status.cap_event_status_id")
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
    cap_event_status: Optional["Cap_Event_Status"] = Relationship(back_populates="cap_event_status_lnk")


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

class Cap_Event_And_Areas(Cap_Event_Read):
    cap_event_id: int
    alert_level: Optional["Alert_Levels_Read"] | None = None 
    event_areas: List["Cap_Event_Areas_Basins"] | None = None

class Cap_Event_History(SQLModel, table=True):
    """
    table model used for read and database definition

    :param Cap_Event_History_Base: inheriting from the base cap event model that is used
                           for write operations
    :type Cap_Event_History_Base: SQLModel
    :param table: indicate that this is a table model, defaults to True
    :type table: bool, optional
    """

    __table_args__ = {"schema": default_schema}

    cap_event_id: int = Field(default=None, foreign_key=f"{default_schema}.cap_event.cap_event_id")
    alert_id: int = Field(default=None, foreign_key=f"{default_schema}.alerts.alert_id")
    cap_event_updated_date: datetime.datetime
    cap_event_hist_created_date: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    alert_level: int = Field(
        default=None, foreign_key=f"{default_schema}.alert_levels.alert_level_id"
    )
    # don't provide default value as this is a history record and is only a copy
    # of the previous state of the cap_event
    cap_event_status_id: int = Field(default=None, foreign_key=f"{default_schema}.cap_event_status.cap_event_status_id")
    # cap_event_status: str

    cap_event_history_id: int = Field(default=None, primary_key=True)

    # relationship parameters for serialization
    alert_levels: "Alert_Levels" = Relationship(back_populates="cap_hist_link")
    cap_event_areas_hist: List["Cap_Event_Areas_History"] = Relationship(back_populates="events_history")
    cap_event_status: Optional["Cap_Event_Status"] = Relationship(back_populates="cap_event_hist_status_lnk")

class Cap_Event_Areas_History(SQLModel, table=True):
    __table_args__ = {"schema": default_schema}

    cap_event_area_history_id: int = Field(default=None, primary_key=True)
    cap_event_history_id: int = Field(default=None, foreign_key=f"{default_schema}.cap_event_history.cap_event_history_id")
    basin_id: int = Field(default=None, foreign_key=f"{default_schema}.basins.basin_id")


    basins: List["Basins"] = Relationship(back_populates="basin_cap_hist_links")
    events_history: "Cap_Event_History" = Relationship(back_populates="cap_event_areas_hist")

class Cap_Event_Status(SQLModel, table=True):
    __table_args__ = {"schema": default_schema}

    cap_event_status_id: int = Field(default=None, primary_key=True)
    cap_event_status: str
    # cap_event_status
    cap_event_status_lnk: Optional["Cap_Event"] = Relationship(back_populates="cap_event_status")
    cap_event_hist_status_lnk: Optional["Cap_Event_History"] = Relationship(back_populates="cap_event_status")
