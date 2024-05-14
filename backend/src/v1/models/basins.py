from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from src.core.config import Settings

if TYPE_CHECKING:
    from src.v1.models.alerts import Alert_Areas
    from src.v1.models.cap import Cap_Event_Areas, Cap_Event_Areas_History

default_schema = Settings.DEFAULT_SCHEMA


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

    basin_links: List["Alert_Areas"] = Relationship(back_populates="basin")
    basin_cap_links: List["Cap_Event_Areas"] = Relationship(back_populates="cap_area_basin")
    basin_cap_hist_links: List["Cap_Event_Areas_History"] = Relationship(back_populates="basins")