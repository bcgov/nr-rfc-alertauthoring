import logging
import typing

from sqlmodel import Session, select
from src.v1.crud import crud_cap
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basin_models

LOGGER = logging.getLogger(__name__)


def test_create_cap_event(db_with_alert_and_data, alert_dict: typing.Dict):
    session = db_with_alert_and_data[0]
    alert_data = db_with_alert_and_data[1]
    session.flush()
    caps = crud_cap.create_cap_event(session=session, alert=alert_data)
    session.flush()
    LOGGER.debug(f"cap: {caps}")
    # each cap event can only contain a single alert level.
    # separate the dict data into the unique number of alert levels then 
    # verify that the number of alert levels in the alert corresponds with the 
    # number of cap events
    alert_levels = [alert_link["alert_level"]["alert_level"] for alert_link in alert_dict["alert_links"] ]
    alert_levels = set(alert_levels)
    assert len(alert_levels) == len(caps)

    # getting the alert level id's from the db
    alert_lvl_dict = get_alert_level_dict(session)
    LOGGER.debug(f"alert_lvl_dict: {alert_lvl_dict}")

    # getting the basin_id to basin name lookup table
    basin_dict = get_basin_dict(session)
    basin_query = select(basin_models.Basins)
    basin_results = session.exec(basin_query).all()
    basin_dict = {}
    for basin in basin_results:
        basin_dict[basin.basin_id] = basin.basin_name

    # verify all the alert levels in the cap are in the original alert
    for cap in caps:
        assert alert_lvl_dict[cap.alert_level.alert_level_id] in alert_levels
        # get the basins in the original alert that have the alert_level set
        # to the current alert level
        alert_basins = [alert_link['basin']['basin_name'] for alert_link in alert_dict['alert_links'] if alert_link['alert_level']['alert_level'] == alert_lvl_dict[cap.alert_level.alert_level_id]]
        LOGGER.debug(f"basins for the alert level {alert_lvl_dict[cap.alert_level.alert_level_id]}: {alert_basins}")
        # now get the basins for the cap event and verify they are in the original
        # alert
        for event_area in cap.event_areas:
            LOGGER.debug(f"event area link: {event_area}")
            # get the basins in the original alert that have the alert_level set
            # to the current alert level
            assert basin_dict[event_area.basin_id] in alert_basins

def test_get_cap_event(db_with_alert_and_caps, alert_dict):
    LOGGER.debug(f"db_with_alert_and_caps: {db_with_alert_and_caps}")
    # session = db_with_alert_and_caps[0]
    alert = db_with_alert_and_caps[1]
    caps = db_with_alert_and_caps[2]

    LOGGER.debug(f"alert: {alert}")

    # alert_lvl_dict = get_alert_level_dict(session)
    # basin_dict = get_basin_dict(session)

    # organize the alert / basin combinations into groupings by alert level
    alert_lvls_basins = {}
    for alert_link in alert.alert_links:
        LOGGER.debug(f"alert_link: {alert_link}")
        if alert_link.alert_level_id not in alert_lvls_basins:
            alert_lvls_basins[alert_link.alert_level_id] = []
        alert_lvls_basins[alert_link.alert_level_id].append(alert_link.basin_id)
    
    for cap in caps:
        LOGGER.debug(f"cap: {cap}")
        # assert that the returned caps are associated with the alert
        assert cap.alert_id == alert.alert_id
        # assert that the alert level is in the original alert
        assert cap.alert_level_id in alert_lvls_basins
        for event_area in cap.event_areas:
            # assert that the basin is associated with the correct alert level
            assert event_area.basin_id in alert_lvls_basins[cap.alert_level_id]

def test_get_cap_events(db_with_alert_and_caps, alert_dict):
    session = db_with_alert_and_caps[0]
    # alert = db_with_alert_and_caps[1]
    caps = db_with_alert_and_caps[2]
    LOGGER.debug("got here")

    caps = crud_cap.get_cap_events(session=session)
    LOGGER.debug(f"caps: {caps}")
    # TODO: do some assertions to make sure that the caps are correct
    #       could search for the cap assocated with the cap that was sent
    #       and then verify the fields are the same

def get_alert_level_dict(session: Session):
    """
    queries the database and returns a dictionary of alert levels where the 
    key is the alert id and the value is the alert level string value.  
    alert_level is something like 'high streamflow advisory'

    :param session: a database session to be used for the query
    :type session: Session
    """
    alert_lvl_query = select(alerts_models.Alert_Levels)
    alert_lvl_results = session.exec(alert_lvl_query).all()
    alert_lvl_dict = {}
    for alert_lvl in alert_lvl_results:
        LOGGER.debug(f"alert_lvl: {alert_lvl}")
        alert_lvl_dict[alert_lvl.alert_level_id] = alert_lvl.alert_level
    return alert_lvl_dict


def get_basin_dict(session: Session):
    """
    queries the database and returns a dictionary of basins where the key is the
    basin_id and the value is the basin name.

    :param session: a database session used for the database query
    :type session: Session
    """
    basin_query = select(basin_models.Basins)
    basin_results = session.exec(basin_query).all()
    basin_dict = {}
    for basin in basin_results:
        basin_dict[basin.basin_id] = basin.basin_name
    return basin_dict