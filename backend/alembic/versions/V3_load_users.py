from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

import logging

from typing import Sequence, Union

import src.v1.models.model as model
LOGGER = logging.getLogger(__name__)

revision: str = 'V3'
down_revision: str = 'V2'
# branch_labels: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None

table_data =  [
            {'name': 'John',
            'email': 'John.ipsum@test.com',
            },
            {'name': 'Jane',
            'email': 'Jane.ipsum@test.com',
            },
            {'name': 'Jack',
            'email': 'Jack.ipsum@test.com',
            },
            {'name': 'Jill',
            'email': 'Jill.ipsum@test.com',
            },
            {'name': 'Joe',
            'email': 'Joe.ipsum@test.com',
            }
        ]


def upgrade() -> None:
    userTable = model.User.__table__
    op.bulk_insert(userTable, table_data)
    op.execute("commit")


def downgrade() -> None:
    userTable = model.User.__table__

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for row in table_data:
        LOGGER.debug(f"deleting user: {row['name']}")
        session.execute(userTable.delete().where(userTable.c.name == row['name']))
    session.commit()
