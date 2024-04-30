import datetime
import logging
from typing import Generator

import pytest
import sqlmodel
import src.db.session
import src.v1.models.alerts as alerts_models
from src.v1.crud import crud_alerts

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

    # alert = crud_alerts.create_alert_with_basins_and_level(
    #     session=db_test_connection,
    #     alert=alert_data_only,
    #     basin_levels=alert_basin_write,
    # )

    alert = crud_alerts.create_alert(
        session=db_test_connection, alert=alert_basin_write
    )
    db_test_connection.flush()



    yield [db_test_connection, alert]

    db_test_connection.rollback()



@pytest.fixture(scope="function")
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
 