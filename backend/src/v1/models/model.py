# coding: utf-8
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from ...core.config import Settings

default_schema = Settings.DEFAULT_SCHEMA
 
class Subbasins(SQLModel, table=True):
    # __tablename__ = 'subbasins'
    __table_args__ = {'schema':default_schema}
    id: Optional[int] = Field(default=None, primary_key=True)
    sub_basin_name: str = Field(nullable=False)
    basins: List['Basins'] = Relationship(back_populates="subbasins")


class BasinBase(SQLModel):
    basin_name: str = Field(nullable=False)

class BasinsRead(BasinBase):
    id: Optional[int] = Field(default=None, primary_key=True)

class Basins(BasinsRead, table=True):
    __table_args__ = {'schema':default_schema}

    subbasins_id: Optional[int] = Field(default=None, foreign_key=f"{default_schema}.subbasins.id")
    subbasins: Optional[Subbasins] = Relationship(back_populates="basins")
