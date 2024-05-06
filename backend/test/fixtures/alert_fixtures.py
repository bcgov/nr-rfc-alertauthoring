import datetime
import logging
from typing import Generator

import pytest
import sqlmodel
import src.db.session
import src.v1.models.alerts as alerts_models
from fastapi.testclient import TestClient
from src.v1.crud import crud_alerts, crud_cap

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def alert_data_only(alert_dict) -> Generator[alerts_models.Alerts, None, None]:
    alert = alerts_models.Alerts(
        alert_created=datetime.datetime(2024, 2, 3, 0, 32, 50, 468722),
        alert_updated=datetime.datetime(2024, 2, 3, 0, 32, 50, 468722),
        author_name=alert_dict["author_name"],
        alert_status=alert_dict["alert_status"],
        alert_hydro_conditions=alert_dict["alert_hydro_conditions"],
        alert_meteorological_conditions=alert_dict["alert_meteorological_conditions"],
        alert_description=alert_dict["alert_description"],
    )
    yield alert


@pytest.fixture(scope="function")
def alert_basin_write(
    alert_dict,
) -> Generator[alerts_models.Alert_Basins_Write, None, None]:
    """returns the test alert record as a Alert_Basins_Write
    data model"""
    new_alert_basin_write = alerts_models.Alert_Basins_Write(**alert_dict)
    yield new_alert_basin_write


@pytest.fixture(scope="function")
def alert_basin_write_data(
    alert_dict, alert_basin_write
) -> Generator[alerts_models.Alert_Basins_Write, None, None]:
    alert_data = alert_basin_write
    yield alert_data


@pytest.fixture(scope="function")
def db_with_alert(
    db_test_connection: sqlmodel.Session,
    alert_basin_write,
    alert_data_only,
    monkeypatch,
):
    """returns the database session object with alert test data loded to it"""

    # need to monkey patch this, as the update_alert method needs to compare what
    # exists in the database, vs what exists in the current session, which requires
    # creating a new session.  This patch ensures the session uses the same database
    # ie the sqllite version as the tests are using, and not the postgres one that
    # the code is configured to use when running the app.
    # monkeypatch.setattr(src.db.session, "engine", session.bind)

    monkeypatch.setattr(src.db.session, "engine", db_test_connection.bind)

    # alert = crud_alerts.create_alert_with_basins_and_level(
    #     session=db_test_connection,
    #     alert=alert_data_only,
    #     basin_levels=alert_basin_write,
    # )

    crud_alerts.create_alert(
        session=db_test_connection, alert=alert_basin_write
    )
    yield db_test_connection

    db_test_connection.rollback()


@pytest.fixture(scope="function")
def db_with_alert_and_data(db_test_connection, monkeypatch, alert_basin_write):
    monkeypatch.setattr(src.db.session, "engine", db_test_connection.bind)

    alert = crud_alerts.create_alert(
        session=db_test_connection, alert=alert_basin_write
    )
    db_test_connection.flush()
    yield [db_test_connection, alert]
    db_test_connection.rollback()


@pytest.fixture(scope="function")
def db_with_alert_and_caps(db_with_alert_and_data):
    session = db_with_alert_and_data[0]
    alert = db_with_alert_and_data[1]
    caps = crud_cap.create_cap_event(session=session, alert=alert)
    session.flush()
    yield [session, alert, caps]
    session.rollback()


@pytest.fixture(scope="session")
def alert_dict():
    """provides a dictionary that can be used to construct an alert object.
    The dictionary mimics the structure of an incomming object from a create
    new alert endpoint.

    all alert tests that require data should start with this data struct"""
    alert_date = datetime.datetime.utcnow()
    alert_dict = {
        "alert_status": "active",
        "author_name": "tony",
        "alert_description": f"testing alert description {alert_date}",
        "alert_hydro_conditions": "testing hydro conditions",
        "alert_meteorological_conditions": "testing meteorological conditions",
        "alert_links": [
            {
                "basin": {"basin_name": "Central Coast"},
                "alert_level": {
                    "alert_level": "High Streamflow Advisory",
                },
            },
            {
                "basin": {
                    "basin_name": "Skeena",
                },
                "alert_level": {
                    "alert_level": "Flood Watch",
                },
            },
            {
                "basin": {
                    "basin_name": "Northern Vancouver Island",
                },
                "alert_level": {
                    "alert_level": "Flood Warning",
                },
            },
            {
                "basin": {
                    "basin_name": "Eastern Vancouver Island",
                },
                "alert_level": {
                    "alert_level": "High Streamflow Advisory",
                },
            },
            {
                "basin": {
                    "basin_name": "Western Vancouver Island",
                },
                "alert_level": {
                    "alert_level": "Flood Watch",
                },
            },
        ],
    }
    yield alert_dict
 

@pytest.fixture(scope="function")
def test_client_with_alert_and_cap(test_app_with_auth, db_with_alert_and_caps, monkeypatch, alert_dict):
    session = db_with_alert_and_caps[0]
    alert = db_with_alert_and_caps[1]


    LOGGER.debug(f"alert id in database sent to client: {alert.alert_id}")
    # alert_from_session = db_with_alert_and_data[1]
    # caps_from_session = db_with_alert_and_caps[2]

    def session_commit_patch():
        LOGGER.debug("session commit patch called")

    def get_db() -> Generator[sqlmodel.Session, None, None]:
        LOGGER.debug(f"get_db called, return type: {type(session)}")
        monkeypatch.setattr(session, "commit", session_commit_patch)
        all_alerts = session.exec(sqlmodel.select(alerts_models.Alerts)).all()

        yield session
    LOGGER.debug("here")
    test_app_with_auth.dependency_overrides[src.db.session.get_db] = get_db
    # query does NOT return the alert object that aligns with the alert_dict
    all_alerts = session.exec(sqlmodel.select(alerts_models.Alerts)).all()
    yield [TestClient(test_app_with_auth), session]
    session.rollback()

    # the client session will automatically call 
