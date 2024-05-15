"""fix alert status table

Revision ID: V11
Revises: V10
Create Date: 2024-05-15 10:21:06.351463

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
import src.v1.models.cap as cap_model
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'V11'
down_revision: Union[str, None] = 'V10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from_to_values = ['CREATE', 'ALERT']


def upgrade() -> None:
    old_value = from_to_values[0]
    new_value = from_to_values[1]
    update(old_value, new_value)

def downgrade() -> None:
    old_value = from_to_values[1]
    new_value = from_to_values[0]
    update(old_value, new_value)

def update(old_value, new_value):
    bind = op.get_bind()
    session = sqlmodel.Session(bind=bind)

    query = sqlmodel.select(cap_model.Cap_Event_Status).where(cap_model.Cap_Event_Status.cap_event_status==old_value)
    record = session.exec(query).one()
    record.cap_event_status = new_value
    session.commit()
