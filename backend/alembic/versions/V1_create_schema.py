#import sqlalchemy as sa
#from sqlalchemy import orm
import logging
from typing import Union

from alembic import op

LOGGER = logging.getLogger(__name__)

revision: str = 'V1'
down_revision: Union[str, None] = None
# branch_labels]: Union[str, Sequence[str], None] = None
# depends_on: Union[str, Sequence[str], None] = None

db_setup_sql = """
    CREATE SCHEMA IF NOT EXISTS py_api;
    SET SEARCH_PATH TO py_api;
    CREATE SEQUENCE IF NOT EXISTS "user_id_seq"
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    CREATE SEQUENCE IF NOT EXISTS "user_addresses_id_seq"
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE;
    """

db_takedown_sql = """
    drop schema if exists py_api cascade;
"""


def upgrade() -> None:

    sql_statements_list = db_setup_sql.replace("\n", "").split(";")
    LOGGER.debug(f"sql_statements_list: {sql_statements_list}")
    for sql_statement in sql_statements_list:
        if sql_statement.strip():
            LOGGER.debug(f"sql_statement: {sql_statement}")
            op.execute(sql_statement + ";")

def downgrade() -> None:
    db_takedown_sql_list = db_takedown_sql.replace("\n", '').split(";")
    for sql_statement in db_takedown_sql_list:
        if sql_statement.strip():
            LOGGER.debug(f"sql_statement: {sql_statement}")
            op.execute(sql_statement)
