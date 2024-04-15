"""adding the alert history table

Revision ID: V8
Revises: V7
Create Date: 2024-03-28 16:17:53.225484

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "V8"
down_revision: Union[str, None] = "V7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "alert_history",
        sa.Column("alert_history_id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column(
            "alert_description", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "alert_hydro_conditions", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "alert_meteorological_conditions",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("author_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("alert_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("alert_updated", sa.DateTime(), nullable=False),
        sa.Column("alert_history_created", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["alert_id"],
            ["py_api.alerts.alert_id"],
        ),
        sa.PrimaryKeyConstraint("alert_history_id"),
        schema="py_api",
        comment="This table is used to track the changes over time of alerts",
    )
    op.create_table(
        "alert_area_history",
        sa.Column("alert_history_id", sa.Integer(), nullable=False),
        sa.Column("basin_id", sa.Integer(), nullable=False),
        sa.Column("alert_level_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["alert_level_id"],
            ["py_api.alert_levels.alert_level_id"],
        ),
        sa.ForeignKeyConstraint(
            ["basin_id"],
            ["py_api.basins.basin_id"],
        ),
        sa.PrimaryKeyConstraint("alert_history_id", "basin_id", "alert_level_id"),
        schema="py_api",
        comment="This table is used to track the changes over time of area and alert levels for a specific alert",
    )
    op.create_unique_constraint(
        "alert_areas_uc",
        "alert_areas",
        ["alert_id", "basin_id", "alert_level_id"],
        schema="py_api",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("alert_areas_uc", "alert_areas", schema="py_api", type_="unique")
    op.drop_table("alert_area_history", schema="py_api")
    op.drop_table("alert_history", schema="py_api")
    # ### end Alembic commands ###
