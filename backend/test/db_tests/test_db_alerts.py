import datetime
import logging

from sqlmodel import Session, select
from src.types import AlertAreaLevel
from src.v1.crud import crud_alerts
from src.v1.models import model

# from testspg.constants import TEST_NEW_USER, TEST_NOT_EXIST_USER_TYPE

LOGGER = logging.getLogger(__name__)


def test_create_alert_with_basins_and_level(db_test_connection: Session):
    # tests the crud functions in the crud_alerts.py file
    test_levels: [AlertAreaLevel] = [
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

    session = db_test_connection
    # create an alert to set
    alert = model.Alerts(
        alert_created=datetime.datetime.utcnow(),
        alert_updated=datetime.datetime.utcnow(),
        author_name="test_author",
        alert_status="active",
        alert_hydro_conditions="testing conditions",
        alert_meteorological_conditions="testing meteor conditions",
        alert_description="testing alert description",
    )
    # add alert to db
    alert = crud_alerts.create_alert_with_basins_and_level(
        session=session, alert=alert, basin_levels=test_levels
    )
    # verify that its there
    alert_select = select(model.Alerts).where(
        model.Alerts.alert_updated == alert.alert_updated
    )
    alert_result = session.exec(alert_select).one()
    assert alert_result.alert_created == alert.alert_created


def test_create_alert(db_test_connection: Session, alert_basin_write_data):
    session = db_test_connection
    alert = alert_basin_write_data
    written_alert = crud_alerts.create_alert(session=session, alert=alert)
    assert written_alert.alert_description == alert.alert_description
    assert written_alert.alert_status == alert.alert_status
    assert written_alert.alert_hydro_conditions == alert.alert_hydro_conditions
    assert (
        written_alert.alert_meteorological_conditions
        == alert.alert_meteorological_conditions
    )
    assert len(written_alert.alert_links) == len(alert.alert_links)

    for area_lvl in alert.alert_links:
        areas_lvl_exists = False
        for area_lvl_written in written_alert.alert_links:
            if (
                area_lvl_written.alert_level.alert_level
                == area_lvl.alert_level.alert_level
                and area_lvl_written.basin.basin_name == area_lvl.basin.basin_name
            ):
                areas_lvl_exists = True
        assert areas_lvl_exists


def test_get_alerts(db_with_alert: Session):
    session = db_with_alert
    alerts = crud_alerts.get_alerts(session=session)
    LOGGER.debug(f"alerts: {alerts}")
    assert len(alerts) >= 1


def test_get_alert(db_with_alert: Session):
    session = db_with_alert
    alerts = crud_alerts.get_alerts(session=session)
    alert_id = alerts[0].alert_id
    alert = crud_alerts.get_alert(session=session, alert_id=alert_id)
    LOGGER.debug(f"alert data: {alert}")
    assert alert.alert_id == alert_id
