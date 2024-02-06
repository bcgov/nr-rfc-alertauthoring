import logging
from logging.config import fileConfig

import src.core.config as app_config
from sqlalchemy import create_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateSchema
from sqlmodel import SQLModel
from src.v1.models.model import *

from alembic import context
from alembic.script import ScriptDirectory

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# override logging setup for debugging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.debug("test test test")


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = SQLModel.metadata
target_metadata = SQLModel.metadata
# target_metadata = MetaData()

# for datum in target_metadata_sql_model:
#     for table in datum.tables.values():
#         print(f'table: {table}')
#         table.to_metadata(target_metadata)

print("target_metadata: ", target_metadata)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(context, revision, directives):
    """overriding the default generation of revision ids to use a
    sequential integer instead of a hex string.

    :param context: _description_
    :type context: _type_
    :param revision: _description_
    :type revision: _type_
    :param directives: _description_
    :type directives: _type_
    """
    # extract Migration
    migration_script = directives[0]
    # extract current head revision
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        # edge case with first migration
        new_rev_id = 1
    else:
        # default branch with incrementation
        last_rev_id = int(head_revision.lstrip("V"))
        new_rev_id = last_rev_id + 1
    # fill zeros up to 4 digits: 1 -> 0001
    # migration_script.rev_id = '{0:04}'.format(new_rev_id)
    migration_script.rev_id = f"V{new_rev_id}"


def get_url():
    url = None
    x_param_url = context.get_x_argument(as_dictionary=True).get("url")
    LOGGER.debug(f"x_param_url: {x_param_url}")
    if x_param_url:
        url = x_param_url
        LOGGER.debug(f"url from -x: {url}")

    if not url:
        LOGGER.debug(
            f"app_config.Configuration.SQLALCHEMY_DATABASE_URI: {app_config.Configuration.SQLALCHEMY_DATABASE_URI}"
        )
        url = app_config.Configuration.SQLALCHEMY_DATABASE_URI.unicode_string()
        LOGGER.debug(f"url from app config: {url}")
    LOGGER.debug(f"captured the url string: {url}")
    return url
    # return "postgresql://postgres:default@localhost:5432/postgres"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    include_schemas = True
    LOGGER.debug("running migrations offline")
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        target_metadata=target_metadata,
        version_table="alembic_version",
        version_table_schema=app_config.Configuration.DEFAULT_SCHEMA,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    include_schemas = True
    url = get_url()
    LOGGER.debug(f"using url: {url}")
    connectable = create_engine(
        url,
        execution_options={
            "schema_translate_map": {
                "tenant_schema": app_config.Configuration.DEFAULT_SCHEMA
            }
        },
    )

    with connectable.connect() as connection:
        # connection(execution_options={"schema_translate_map": {"tenant_schema": app_config.Configuration.DEFAULT_SCHEMA}})

        context.configure(
            include_schemas=True,
            connection=connection,
            compare_type=True,
            version_table="alembic_version",
            target_metadata=target_metadata,
            version_table_schema=app_config.Configuration.DEFAULT_SCHEMA,
            process_revision_directives=process_revision_directives,
        )
        schema_create = CreateSchema(
            app_config.Configuration.DEFAULT_SCHEMA, if_not_exists=True
        )
        LOGGER.debug(f"schema_create: {schema_create}")
        connection.execute(schema_create)
        # create_schema_sql = 'CREATE SCHEMA IF NOT EXISTS {}'
        # connection.execute(create_schema_sql)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
