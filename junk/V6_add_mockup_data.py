"""add mockup data

Revision ID: V6
Revises: V5
Create Date: 2024-01-29 12:28:16.951414

"""
import logging
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from src.v1.models import model

LOGGER = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = "V6"
down_revision: Union[str, None] = "V5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # rename id to alert_id

    model.Alerts(
        alert_description="Alert Description 1",
        alert_hydro_conditions="Alert Hydro Conditions 1",
        alert_meteorological_conditions="Alert Meteorological Conditions 1",
        basin_id=1,
        id=1,
    )
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
