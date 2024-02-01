"""rename basin and sub basin pks

Revision ID: V7
Revises: V6
Create Date: 2024-01-31 12:01:14.390799

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "V4"
down_revision: Union[str, None] = "V3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE py_api.basins RENAME COLUMN id TO basin_id;")
    op.execute("ALTER TABLE py_api.subbasins RENAME COLUMN id TO subbasin_id;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE py_api.basins RENAME  COLUMN basin_id TO id;")
    op.execute("ALTER TABLE py_api.subbasins RENAME COLUMN subbasin_id TO id;")
    # ### end Alembic commands ###
