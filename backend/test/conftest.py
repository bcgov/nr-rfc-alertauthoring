import json
import logging
import os
import sys

import pytest
import sqlmodel
import testcontainers.compose
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# from mock_alchemy.mocking import UnifiedAlchemyMagicMock
import constants
import src.core.config as config
import src.db.session
from sqlalchemy import Engine, create_engine
from src.main import app
from src.v1.models.model import *

LOGGER = logging.getLogger(__name__)
# the folder contains test docker-compose.yml, ours in the root directory
COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "../../")
COMPOSE_FILE_NAME = "docker-compose-tests.yml"

# add fixture modules here
pytest_plugins = [
    "fixtures.alert_fixtures",
]


# used for postgres testing
@pytest.fixture(scope="session")
def set_env():
    os.environ["POSTGRES_USER"] = constants.POSTGRES_USER
    os.environ["POSTGRES_PASSWORD"] = constants.POSTGRES_PASSWORD
    os.environ["POSTGRES_HOST"] = constants.POSTGRES_HOST
    os.environ["POSTGRES_DATABASE"] = constants.POSTGRES_DATABASE
    os.environ["POSTGRES_PORT"] = str(constants.POSTGRES_PORT)
    os.environ["POSTGRES_SCHEMA"] = constants.POSTGRES_SCHEMA


# used for postgres testing
@pytest.fixture(scope="session")
def db_pg_connection(set_env):
    engine = create_engine(
        "postgresql+psycopg2://"
        + f"{os.environ.get('POSTGRES_USER')}:"
        + f"{os.environ.get('POSTGRES_PASSWORD')}@"
        + f"{os.environ.get('POSTGRES_HOST')}:"
        f"{os.environ.get('POSTGRES_PORT')}/"
        f"{os.environ.get('POSTGRES_DATABASE')}"
    )

    # session_local = sessionmaker(bind=engine)
    # test_db = session_local()
    test_db = sqlmodel.Session(engine)

    yield test_db
    test_db.close()


@pytest.fixture(scope="function")
def db_pg_session(db_pg_connection: sqlmodel.Session):
    yield db_pg_connection
    db_pg_connection.rollback()


@pytest.fixture(scope="session")
def db_sqllite_connection() -> Engine:
    # should re-create the database every time the tests are run, the following
    # line ensure database that maybe hanging around as a result of a failed
    # test is deleted
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        os.remove("./test_db.db")

    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
    LOGGER.debug(f"SQL Alchemy URL: {SQLALCHEMY_DATABASE_URL}")
    execution_options = {"schema_translate_map": {"py_api": None}}

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        execution_options=execution_options,
    )

    # model.Base.metadata.create_all(bind=engine)
    # metadata = model.Base.metadata
    sqlmodel.SQLModel.metadata.create_all(engine)

    LOGGER.debug(f"engine type: {type(engine)}")
    yield engine

    # dropping all objects in the test database and...
    # delete the test database
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        # os.remove("./test_db.db")


@pytest.fixture(scope="session")
def db_test_load_data(db_sqllite_connection):
    """
    loads test data
    """
    session = sqlmodel.Session(db_sqllite_connection)
    basin_file = os.path.join(
        os.path.dirname(__file__), "..", "alembic", "data", "basins.json"
    )
    LOGGER.debug(f"src file: {basin_file}")

    with open(basin_file, "r") as json_file:

        basins_data = json.load(json_file)

    for basin in basins_data:
        basin = Basins(basin_name=basin["basin_name"])
        session.add(basin)

    alert_level_data_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "alembic",
        "data",
        "alert_levels.json",
    )

    with open(alert_level_data_file, "r") as json_file:
        alert_level_data = json.load(json_file)
    for alert in alert_level_data:
        alert_level = Alert_Levels(alert_level=alert["alert_level"])
        session.add(alert_level)
    session.commit()


@pytest.fixture(scope="session")
def db_test_connection(db_test_load_data, db_sqllite_connection):
    # quick and dirty database mocking using
    engine = db_sqllite_connection
    session = sqlmodel.Session(engine)
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_client_fixture(db_test_connection) -> TestClient:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """

    def get_db() -> sqlmodel.Session:
        yield db_test_connection

    # reset to default database which points to postgres container
    app.dependency_overrides[src.db.session.get_db] = get_db

    yield TestClient(app)

    # reset other dependency override back to app default in each test
    # during test case teardown.
    app.dependency_overrides = {}
