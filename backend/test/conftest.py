import json
import logging
import os
import sys
from typing import Generator

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
from src.v1.models.cap import *  # noqa: F403

LOGGER = logging.getLogger(__name__)

# add fixture modules here
pytest_plugins = [
    "fixtures.alert_fixtures",
    "fixtures.data_fixtures",
    "fixtures.cap_fixtures",
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
    if (os.getenv("USE_POSTGRES_FOR_TESTS") is None) or (
        os.getenv("USE_POSTGRES_FOR_TESTS").lower() != "true"
    ):
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
    # test_db = sqlmodel.Session(engine)

    yield engine
    if engine is not None:
        engine.dispose()


@pytest.fixture(scope="session")
def db_pg_session(db_pg_connection: sqlmodel.Session):
    yield db_pg_connection
    db_pg_connection.rollback()


@pytest.fixture(scope="session")
def db_sqllite_engine(alert_level_data, basin_data) -> Generator[Engine, None, None]:
    # should re-create the database every time the tests are run, the following
    # line ensure database that maybe hanging around as a result of a failed
    # test is deleted

    # only need to do something if we are going to use the sqllite database
    engine = None
    if (os.getenv("USE_POSTGRES_FOR_TESTS") is None) or (
        os.getenv("USE_POSTGRES_FOR_TESTS").lower() != "true"
    ):
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

        for basin in basin_data:
            basin = Basins(basin_name=basin["basin_name"])  # noqa: F405
            session.add(basin)
        # loading alert level data
        for alert in alert_level_data:
            alert_level = Alert_Levels(alert_level=alert["alert_level"])  # noqa: F405
            session.add(alert_level)

        # loading the cap_status_data
        cap_status_file = os.path.join(
            os.path.dirname(__file__), "..", "alembic", "data", "cap_statuses.json"
        )
        with open(cap_status_file, "r") as js_fh:
            cap_statuses = json.load(js_fh)

        for cap in cap_statuses:
            LOGGER.debug(
                f"adding the cap event status record: {cap['cap_event_status']}"
            )
            cap_status = Cap_Event_Status(  # noqa: F405
                cap_event_status=cap["cap_event_status"]
            )
            session.add(cap_status)

        # caps got entered incorrectly, there is a migration to address that.  This
        # method fixes that for the sqllite tests.
        old_value = "CREATE"
        new_value = "ALERT"
        query = sqlmodel.select(Cap_Event_Status).where(  # noqa: F405
            Cap_Event_Status.cap_event_status == old_value  # noqa: F405
        )
        db_record = session.exec(query)
        record = db_record.all()
        if len(record):
            LOGGER.debug(f"number of records: {len(record)}")
            record = record[0]
            record.cap_event_status = new_value
        session.commit()

    yield engine

    # dropping all objects in the test database and...
    # delete the test database
    if os.path.exists("./test_db.db"):
        LOGGER.debug("remove the database: ./test_db.db'")
        # os.remove("./test_db.db")


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
def test_app_with_auth(db_test_connection, mock_access_token):
    # def test_client_fixture(db_test_connection, mock_access_token) -> Generator[TestClient, None, None]:

    token = mock_access_token

    def get_db() -> Generator[sqlmodel.Session, None, None]:
        yield db_test_connection

    def authorize() -> Generator[bool, None, None]:
        LOGGER.debug("override the authroizations")
        yield True

    def get_current_user():
        LOGGER.debug("current user called")
        return token

    app.dependency_overrides[src.db.session.get_db] = get_db
    app.dependency_overrides[oidcAuthorize.authorize] = lambda: authorize()
    app.dependency_overrides[oidcAuthorize.get_current_user] = (
        lambda: get_current_user()
    )

    yield app
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_client_fixture(test_app_with_auth) -> Generator[TestClient, None, None]:
    """returns a requests object of the current app,
    with the objects defined in the model created in it.

    :rtype: starlette.testclient
    """

    yield TestClient(test_app_with_auth)

    # reset other dependency override back to app default in each test
    # during test case teardown.


@pytest.fixture(scope="function")
def test_client_fixture_w_alert_cap(
    test_app_with_auth,
) -> Generator[TestClient, None, None]:

    def get_db() -> Generator[sqlmodel.Session, None, None]:
        yield db_test_connection
