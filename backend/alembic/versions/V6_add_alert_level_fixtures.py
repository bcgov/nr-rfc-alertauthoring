"""add alert level fixtures

Revision ID: V5
Revises: V4
Create Date: 2024-01-29 11:38:30.304621

"""

import json
import logging
import os
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
import src.v1.models.alerts as alerts_model
from alembic import op

LOGGER = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = "V6"
down_revision: Union[str, None] = "V5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

alert_level_data_file = os.path.join(
    os.path.dirname(__file__), "..", "data", "alert_levels.json"
)
with open(alert_level_data_file, "r") as json_file:
    alert_level_data = json.load(json_file)
alert_levels = []
for alert in alert_level_data:
    alert_levels.append(alerts_model.Alert_Levels(alert_level=alert["alert_level"]))

# alert_levels = [
#     model.Alert_Levels(alert_level="High Streamflow Advisory"),
#     model.Alert_Levels(alert_level="Flood Watch"),
#     model.Alert_Levels(alert_level="Flood Warning"),
# ]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = sqlmodel.Session(bind=bind)

    for alert_level in alert_levels:
        LOGGER.debug(f"adding alert_level: {alert_level}")
        session.add(alert_level)

    session.commit()
    session.close()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = sqlmodel.Session(bind=bind)

    for alert_level in alert_levels:
        stmt = sqlmodel.select(alerts_model.Alert_Levels).where(  # noqa: F405
            alerts_model.Alert_Levels.alert_level == alert_level.alert_level
        )
        results = session.exec(stmt)
        print("results: ", results.all())
        if results.all():
            alert_level_result = results.one()
            session.delete(alert_level_result)

    session.commit()
    session.close()

    # ### end Alembic commands ###
