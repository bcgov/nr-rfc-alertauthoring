import datetime
import logging

import pytest
import sqlmodel
import src.v1.models.model as model
from src.v1.crud import crud_alerts

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def alert_data_test_levels():
    test_levels: [model.AlertAreaLevel] = [
        {"basin": "Central Coast", "alert_level": "High Streamflow Advisory"},
        {"basin": "Skeena", "alert_level": "Flood Watch"},
        {"basin": "Northern Vancouver Island", "alert_level": "Flood Warning"},
        {
            "basin": "Eastern Vancouver Island",
            "alert_level": "High Streamflow Advisory",
        },
        {"basin": "Western Vancouver Island", "alert_level": "Flood Watch"},
        {"basin": "Central Vancouver Island", "alert_level": "Flood Warning"},
    ]
    yield test_levels


@pytest.fixture(scope="function")
def alert_data():
    alert = model.Alerts(
        alert_created=datetime.datetime(2024, 2, 3, 0, 32, 50, 468722),
        alert_updated=datetime.datetime(2024, 2, 3, 0, 32, 50, 468722),
        author_name="test_author",
        alert_status="active",
        alert_hydro_conditions="testing conditions",
        alert_meteorological_conditions="testing meteor conditions",
        alert_description="testing alert description",
    )
    yield alert


@pytest.fixture(scope="function")
def db_with_alert(
    db_test_connection: sqlmodel.Session, alert_data, alert_data_test_levels
):
    """returns the database session object with alert test data loded to it"""
    alert = alert_data

    alert = crud_alerts.create_alert_with_basins_and_level(
        session=db_test_connection, alert=alert, basin_levels=alert_data_test_levels
    )

    yield db_test_connection

    db_test_connection.rollback()
