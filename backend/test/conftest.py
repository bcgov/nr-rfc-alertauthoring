import json
import logging
import os
import sys
from typing import Dict, Generator

import pytest
import sqlmodel
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# from mock_alchemy.mocking import UnifiedAlchemyMagicMock
import constants
import src.db.session
from sqlalchemy import Engine, create_engine
from src.main import app
from src.oidc import oidcAuthorize
from src.v1.models.alerts import *  # noqa: F403
from src.v1.models.basins import *  # noqa: F403

LOGGER = logging.getLogger(__name__)

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
def db_pg_engine(set_env):
    LOGGER.debug(f"postgres param: {os.getenv('USE_POSTGRES')}")
    # if the env var USE_POSTGRES is not set, then use the sqlite database
    if ( os.getenv("USE_POSTGRES_FOR_TESTS") is None) or (os.getenv("USE_POSTGRES_FOR_TESTS").lower() != "true"):
        engine = None
    else:
        LOGGER.debug("creating postgres database")
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
    #test_db = sqlmodel.Session(engine)

    yield engine
    if engine is not None:
        engine.dispose()


@pytest.fixture(scope="session")
def db_pg_session(db_pg_connection: sqlmodel.Session):
    yield db_pg_connection
    db_pg_connection.rollback()


@pytest.fixture(scope="session")
def db_sqllite_engine(alert_level_data) -> Generator[Engine, None, None]:
    # should re-create the database every time the tests are run, the following
    # line ensure database that maybe hanging around as a result of a failed
    # test is deleted

    # only need to do something if we are going to use the sqllite database
    engine = None
    if ( os.getenv("USE_POSTGRES_FOR_TESTS") is None) or (os.getenv("USE_POSTGRES_FOR_TESTS").lower() != "true"):
        if os.path.exists("./test_db.db"):
            LOGGER.debug("remove the database: ./test_db.db'")
            os.remove("./test_db.db")

        SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
        LOGGER.debug(f"SQL Alchemy URL: {SQLALCHEMY_DATABASE_URL}")
        execution_options = {"schema_translate_map": {"py_api": None}}

        engine: Engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            execution_options=execution_options,
        )

        sqlmodel.SQLModel.metadata.create_all(engine)

        LOGGER.debug(f"engine type: {type(engine)}")

        # for sqllite database we need to load the data
            
        # loading basin data
        LOGGER.info("loading basin data into test database")
        session = sqlmodel.Session(engine)
        basin_file = os.path.join(
            os.path.dirname(__file__), "..", "alembic", "data", "basins.json"
        )
        LOGGER.debug(f"src file for basin data: {basin_file}")
        with open(basin_file, "r") as json_file:
            basins_data = json.load(json_file)

        for basin in basins_data:
            basin = Basins(basin_name=basin["basin_name"])  # noqa: F405
            session.add(basin)
        # loading alert level data
        for alert in alert_level_data:
            alert_level = Alert_Levels(alert_level=alert["alert_level"])  # noqa: F405
            session.add(alert_level)
        session.commit()

    yield engine

    # dropping all objects in the test database and...
    # delete the test database
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        # os.remove("./test_db.db")

@pytest.fixture(scope="session")
def alert_level_data() -> Generator[Alert_Levels_Read, None, None]:
    """
    reads the alert levels json file and loads to a List[Dict] structure.

    :yield: List
    :rtype: Generator[Alert_Levels_Read, None, None]
    """

    alert_level_data_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "alembic",
        "data",
        "alert_levels.json",
    )

    with open(alert_level_data_file, "r") as json_file:
        alert_level_data = json.load(json_file)
    yield alert_level_data


# TODO: Delete this... don't need anymore
@pytest.fixture(scope="session")
def db_test_load_data(db_engine, alert_level_data):
    """
    loads test data, this should only be run on the sqllite test database,
    postgres db should already have the data loaded through the migrations.
    """
    engine = db_engine


@pytest.fixture(scope="session")
def db_engine(db_sqllite_engine, db_pg_engine):
    if db_pg_engine is not None:
        LOGGER.info("using postgres database for tests")
        engine = db_pg_engine
    else:
        LOGGER.info("using sqllite database for tests")
        engine = db_sqllite_engine
    yield engine
    engine.dispose()

# db_pg_engine db_sqllite_engine
@pytest.fixture(scope="session")
# def db_test_connection(db_pg_engine):
#     engine = db_pg_engine
def db_test_connection(db_engine):

    session = sqlmodel.Session(db_engine)

    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def mock_access_token():
    token = {
        "exp": 1712792801,
        "iat": 1712792501,
        "auth_time": 1712792501,
        "azp": "hydrological-alerting-5261",
        "scope": "openid email profile",
        "idir_user_guid": "3DKJFOSCBMXLAJHFHQPUE39KSVKSLAZX",
        "client_roles": ["editor", "user"],
        "identity_provider": "idir",
        "idir_username": "GLAFLEUR",
        "email_verified": False,
        "name": "Lafleur, Guy H WLRS:EX",
        "display_name": "Lafleur, Guy H WLRS:EX",
        "given_name": "Guy",
        "family_name": "Lafleur",
        "email": "guy.lafleur@gov.bc.ca",
    }
    yield token

@pytest.fixture(scope="function")
def test_client_fixture(db_test_connection, mock_access_token) -> Generator[TestClient, None, None]:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """
    token = mock_access_token

    def get_db() -> Generator[sqlmodel.Session, None, None]:
        yield db_test_connection

    def authorize() -> Generator[bool, None, None]:
        LOGGER.debug("override the authroizations")
        yield True

    def get_current_user():
        LOGGER.debug("current user called")
        return token

    # reset to default database which points to postgres container
    app.dependency_overrides[src.db.session.get_db] = get_db
    app.dependency_overrides[oidcAuthorize.authorize] = lambda: authorize()
    app.dependency_overrides[oidcAuthorize.get_current_user] = (
        lambda: get_current_user()
    )

    yield TestClient(app)

    # reset other dependency override back to app default in each test
    # during test case teardown.
    app.dependency_overrides = {}
