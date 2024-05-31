import datetime
import logging
import typing

import faker
import pytest
from sqlmodel import Session, select
from src.v1.crud import crud_alerts, crud_cap
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basin_models
from src.v1.models import cap as cap_models

LOGGER = logging.getLogger(__name__)


def test_create_cap_event(db_with_alert_and_data, alert_dict: typing.Dict):
    session = db_with_alert_and_data[0]
    alert_data = db_with_alert_and_data[1]

    # create cap events from the alert
    caps = crud_cap.create_cap_event(session=session, alert=alert_data)
    session.flush()
    LOGGER.debug(f"cap: {caps}")

    # create a list of alert levels associated with the current alert
    alert_levels = [alert_link["alert_level"]["alert_level"] for alert_link in alert_dict["alert_links"] ]
    alert_levels = list(set(alert_levels)) # remove any duplicates
    assert len(alert_levels) == len(caps)

    # dictionary mapping the primary keys to the alert level strings
    alert_lvl_dict = get_alert_level_dict(session)
    LOGGER.debug(f"alert_lvl_dict: {alert_lvl_dict}")

    # getting the basin_id (fk) to basin name lookup table
    basin_dict = get_basin_dict(session)
    basin_query = select(basin_models.Basins)
    basin_results = session.exec(basin_query).all()
    basin_dict = {}
    for basin in basin_results:
        basin_dict[basin.basin_id] = basin.basin_name

    # verify all the alert levels in the cap are in the original alert
    for cap in caps:
        # verify that the primary key aligns with the table
        assert cap.alert_level.alert_level in alert_levels

        # get the basins in the original alert that have the alert_level set
        # to the current alert level
        alert_basins = [alert_link['basin']['basin_name'] for alert_link in alert_dict['alert_links'] if alert_link['alert_level']['alert_level'] == cap.alert_level.alert_level]
        LOGGER.debug(f"basins for the alert level {alert_lvl_dict[cap.alert_level.alert_level_id]}: {alert_basins}")

        # now get the basins for the cap event and verify they are in the original
        # alert
        for event_area in cap.event_areas:
            LOGGER.debug(f"event area link: {event_area}")
            LOGGER.debug(f"event area link basin: {event_area.cap_area_basin.basin_name}")

            # get the basins in the original alert that have the alert_level set
            # to the current alert level
            assert event_area.cap_area_basin.basin_name in alert_basins

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

def test_edit_alert_cap_events(db_with_alert_and_caps):
        session = db_with_alert_and_caps[0]
        alert = db_with_alert_and_caps[1]
        caps = db_with_alert_and_caps[2]

        LOGGER.debug(f"caps: {caps}")
        LOGGER.debug(f"alert: {alert}")
        for alert_lnk in alert.alert_links:
            LOGGER.debug(f"alert_lnk: {alert_lnk} {alert_lnk.basin}")

        # modify the alert adding a new alert_link
        # add an alert link for 'North Coast'
        nc_query = select(basin_models.Basins).where(basin_models.Basins.basin_name=='North Coast')
        nc_record = session.exec(nc_query).first()
        new_alert_area = alerts_models.Alert_Areas(
            alert_id=alert.alert_links[0].alert_id,
            alert_level_id=alert.alert_links[0].alert_level_id,
            basin_id=nc_record.basin_id
        )
        alert.alert_links.append(new_alert_area)
        LOGGER.debug(f"alert.alert_links: {alert.alert_links}")

        # send to cap update
        crud_cap.update_cap_event(session, alert)

@pytest.mark.parametrize(
        "input_alert_list,updated_alert_list",
        [
            [
                [{'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']}],
                [{'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast']}]
            ],
            [
                [{'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast']}],
                [{'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']}]
            ],
            [
                [{'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast']}],
                [{'alert_level': 'Flood Watch', 'basin_names': ['Central Coast']}]
            ],
            [
                [{'alert_level': 'Flood Watch', 'basin_names': ['Central Coast']}],
                [{'alert_level': 'Flood Watch', 'basin_names': ['Central Coast']}]
            ],
            [
                [{'alert_level': 'Flood Watch', 'basin_names': ['Central Coast']}],
                [{'alert_level': 'Flood Watch', 'basin_names': []}]
            ],

        ]
)
def test_record_cap_event_history(db_test_connection, input_alert_list, updated_alert_list):
    session = db_test_connection
    LOGGER.debug(f"sesion: {db_test_connection}")

    # create two fake alerts
    input_alert = create_fake_alert(input_alert_list)
    updated_alert = create_fake_alert(updated_alert_list)
    LOGGER.debug(f"input_alert: {input_alert}")

    # add the 'input_alert' alert to the database transaction, and generate caps for 
    # that alert
    input_alert_db = crud_alerts.create_alert(session=session, alert=input_alert)
    caps = crud_cap.create_cap_event(session=session, alert=input_alert_db)
    LOGGER.debug(f"caps for new alert: {caps}")
    
    # now add updated version of the alert to the database transaction.
    updated_alert_db = crud_alerts.update_alert(session=session, alert_id=input_alert_db.alert_id, updated_alert=updated_alert)
    session.flush()

    LOGGER.debug(f"input alert: {input_alert_db}, {type(input_alert_db)}")
    LOGGER.debug(f"updated alert: {updated_alert_db}, {type(updated_alert_db)}")

    # now create the cap event history records
    crud_cap.record_history(session, updated_alert_db)

    # finally verify the data in the cap history records created
    for cap_event in caps:
        cap_hist_query = select(alerts_models.Cap_Event_History).where(
            alerts_models.Cap_Event_History.cap_event_id == cap_event.cap_event_id)
        cap_hist_records = session.exec(cap_hist_query).all()

        # if there are no changes, then there will not be any history records and 
        # this loop will not be entered
        for cap_hist_record in cap_hist_records:
            LOGGER.debug(f"cap_hist_records: {cap_hist_record}")
            LOGGER.debug(f"cap_hist_records alert_level: {cap_hist_record.alert_levels}")
            LOGGER.debug(f"cap_hist_records status: {cap_hist_record.cap_event_status}")
            LOGGER.debug(f"cap_hist_records areas: {cap_hist_record.cap_event_areas_hist}")

            basin_names = []
            for basin in cap_hist_record.cap_event_areas_hist:
                basin_names.append(basin.basins.basin_name)
                input_alert_dict = [alert for alert in input_alert_list if alert['alert_level'] == cap_hist_record.alert_levels.alert_level][0]
                assert basin.basins.basin_name in input_alert_dict['basin_names']
            # there should be a record that corresponds with the alert level
            
            assert cap_hist_record.alert_levels.alert_level == input_alert_dict['alert_level']
    session.rollback()

@pytest.mark.parametrize(
        "existing_alert_list,updated_alert_list",
        [
            [
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']}
                ],
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine']}
                ]
            ],
            [
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine']}
                ],
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine']},
                    {'alert_level': 'Flood Warning', 'basin_names': ['Skeena', 'Northwest']}
                ],
            ]
        ]
)
def test_new_cap_for_alert(db_test_connection, existing_alert_list, updated_alert_list):
    """
    _summary_

    :param db_test_connection: a database session / transaction
    :type db_test_connection: Session.session
    :param existing_alert_list: a list of dictionaries that describes the alert level 
        and the basins for a hypothetical alert.  This represents the state of the 
        alert in the database prior to an update
    :type existing_alert_list: typing.List[typing.Dict]
    :param updated_alert_list: a list of dictionaries that describe the new state
        of the alert levels and basins for an incomming update for an alert
    :type updated_alert_list: typing.List[typing.Dict]
    """
    session = db_test_connection
    LOGGER.debug(f"input_alert_list: {existing_alert_list}")
    LOGGER.debug(f"updated_alert_list: {updated_alert_list}")
    
    # create the fake alerts, and caps.  These represent the existing state before
    # an update is performed
    input_alert = create_fake_alert(existing_alert_list)
    input_alert_db = crud_alerts.create_alert(session=session, alert=input_alert)
    caps = crud_cap.create_cap_event(session=session, alert=input_alert_db)
    LOGGER.debug(f"caps for new alert: {caps}")

    # create the updated alert
    updated_alert = create_fake_alert(updated_alert_list)
    updated_alert_db = crud_alerts.create_alert(session=session, alert=updated_alert)

    # generate a cap comp object
    cap_comp = crud_cap.CapCompare(session, updated_alert_db)
    cap_delta = cap_comp.get_delta()
    creates = cap_delta.getCreates()

    LOGGER.debug(f"creates {creates}")

    # create a new cap event for an existing alert
    crud_cap.new_cap_for_alert(
        session=session, alert=updated_alert_db, cap_comps=creates)

    # testing to make sure the new cap event for the existing alert is correct

    # - retrieve the existing caps for the alert
    cap_query = select(cap_models.Cap_Event).where(cap_models.Cap_Event.alert_id == updated_alert_db.alert_id)
    existing_caps = session.exec(cap_query).all()

    # - verify that the cap events for the alert align with what is expected
    #   - create a dict for lookup of alert levels
    alert_lvl_dict = {}
    for alert_lvl in updated_alert_list:
        alert_lvl_dict[alert_lvl['alert_level']] = alert_lvl

    for cap in existing_caps:
        LOGGER.debug(f"cap: {cap}")
        # - verify that the alert id is correct
        assert cap.alert_id == updated_alert_db.alert_id

        # - verify that the alert level is correct
        assert cap.alert_level.alert_level in alert_lvl_dict.keys()

        # - verify that the basins are correct
        for event_area in cap.event_areas:
            assert event_area.cap_area_basin.basin_name in alert_lvl_dict[cap.alert_level.alert_level]['basin_names']

    assert len(existing_caps) == len(updated_alert_list)
    # TODO: verify that the cap status is set to ALERT


@pytest.mark.parametrize(
        "existing_alert_list,updated_alert_list",
        [
            [
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']}
                ],
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island', 'Skeena']},
                ]
            ],
            [
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island', 'Skeena']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine']}
                ],
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine', "Skeena"]}
                ],
            ],
            [
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine']}
                ],
                [
                    {'alert_level': 'High Streamflow Advisory', 'basin_names': ['Central Coast', 'Eastern Vancouver Island', 'Skeena']},
                    {'alert_level': 'Flood Watch', 'basin_names': ['North Coast', 'Stikine', "Skeena"]}
                ],
            ]
        ]
)
def test_update_cap_for_alert(db_test_connection, existing_alert_list, updated_alert_list):
    session = db_test_connection
    
    # create the fake alerts, and caps.  These represent the existing state before
    # an update is performed
    input_alert = create_fake_alert(existing_alert_list)
    input_alert_db = crud_alerts.create_alert(session=session, alert=input_alert)
    caps = crud_cap.create_cap_event(session=session, alert=input_alert_db)
    # session.flush()
    # HERE.... something is wrong with the caps... relationships are not loading
    # debugging to verify that relationships where added

    LOGGER.debug(f"caps created for alert: {caps}, {type(caps)}")

    # LOGGER.debug(f"input_alert_db: {input_alert_db}, {type(input_alert_db)}")
    # LOGGER.debug(f"alert id: {input_alert_db.alert_id}")
    # LOGGER.debug(f"input_alert_db.alert_level_id: {input_alert_db.alert_level_id}")
    # cap_query = select(cap_models.Cap_Event).where(
    #     cap_models.Cap_Event.alert_id == input_alert_db.alert_id).where(
    #     cap_models.Cap_Event.alert_level_id == input_alert_db.alert_level_id)
    # cap_data = session.exec(cap_query).all()
    # LOGGER.debug(f"cap_query: {cap_query}")
    # LOGGER.debug(f"cap_query: {cap_data}")


    # update the alert previously created
    updated_alert = update_fake_alert(existing_alert=input_alert_db, alert_list=updated_alert_list)
    updated_alert_db = crud_alerts.update_alert(
        session=session, alert_id=input_alert_db.alert_id, updated_alert=updated_alert)
    LOGGER.debug(f"updated_alert: {updated_alert_db}")

    # generate a cap comp object
    cap_comp = crud_cap.CapCompare(session, updated_alert_db)
    cap_delta = cap_comp.get_delta()
    updates = cap_delta.getUpdates()

    LOGGER.debug(f"updates {updates}")

    # create a new cap event for an existing alert
    crud_cap.update_cap_for_alert(
        session=session, alert=updated_alert_db, cap_comps=updates)
    
    # now to the assertions
    # - retrieve the existing caps for the alert
    cap_query = select(cap_models.Cap_Event).where(cap_models.Cap_Event.alert_id == updated_alert_db.alert_id)
    existing_caps = session.exec(cap_query).all()

    # - verify that the cap events for the alert align with what is expected
    #   - create a dict for lookup of alert levels
    alert_lvl_dict = {}
    for alert_lvl in updated_alert_list:
        alert_lvl_dict[alert_lvl['alert_level']] = alert_lvl

    for cap in existing_caps:
        LOGGER.debug(f"cap: {cap}")
        # - verify that the alert id is correct
        assert cap.alert_id == updated_alert_db.alert_id

        # - verify that the alert level is correct
        assert cap.alert_level.alert_level in alert_lvl_dict.keys()

        # - verify that the basins are correct
        for event_area in cap.event_areas:
            assert event_area.cap_area_basin.basin_name in alert_lvl_dict[cap.alert_level.alert_level]['basin_names']

    assert len(existing_caps) == len(updated_alert_list)
    # TODO: verify that the cap status is set to UPDATE
    for cap in existing_caps:
        assert cap.cap_event_status.cap_event_status == "UPDATE"

    session.rollback()



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


def create_fake_alert(alert_list: typing.List[typing.Dict]) -> alerts_models.Alert_Basins_Write:
    """
    creates a fake alert object from a dictionary.  The dictionary is expected
    to contain the following keys:
    - alert_level: the alert level string value
    - basin_names: a list of basin names that are associated with the alert level

    :param alert_dict: a dictionary containing the alert level and basin names
    :type alert_dict: typing.Dict
    """
    LOGGER.debug(f"alert_dict: {alert_list}")
    alert_area_list = []
    for alert_dict in alert_list:
        for basin_name in alert_dict["basin_names"]:
            LOGGER.debug(f"basin_name: {basin_name}")
            alert_area = alerts_models.Alert_Areas_Write(
                alert_level=alerts_models.Alert_Levels_Base(alert_level=alert_dict["alert_level"]),
                basin=basin_models.BasinBase(basin_name=basin_name)
            )
            alert_area_list.append(alert_area)

    fakeInst = faker.Faker("en_US")

    desc = fakeInst.text()
    met_cond = fakeInst.text()
    hydro_cond = fakeInst.text()
    auth = fakeInst.name()

    alert = alerts_models.Alert_Basins_Write(
        alert_description=desc,
        alert_hydro_conditions=hydro_cond,
        alert_meteorological_conditions=met_cond,
        author_name=auth,
        alert_status="active",
        alert_created=datetime.datetime.now(datetime.timezone.utc),
        alert_updated=datetime.datetime.now(datetime.timezone.utc),
        alert_links=alert_area_list
    )
    LOGGER.debug(f"fake alert: {alert}")
    return alert


#     update_fake_alert(session=session, input_alert_db, updated_alert_list)
def update_fake_alert(
        existing_alert: alerts_models.Alerts,
        alert_list: typing.List[typing.Dict]) -> alerts_models.Alert_Basins_Write:
    """
    used to simulate the condition where an alert has been updated and now the 
    caps associated with that alert need to be updated.
    """
    # create the alert area / alert level list to be added to the alert object
    # further down in the function 
    alert_area_list = []
    for alert_dict in alert_list:
        for basin_name in alert_dict["basin_names"]:
            LOGGER.debug(f"basin_name: {basin_name}")
            alert_area = alerts_models.Alert_Areas_Write(
                alert_level=alerts_models.Alert_Levels_Base(alert_level=alert_dict["alert_level"]),
                basin=basin_models.BasinBase(basin_name=basin_name)
            )
            alert_area_list.append(alert_area)

    fakeInst = faker.Faker("en_US")
    auth = fakeInst.name()

    # mostly copy the attributes from the incomming alert, with the exception of 
    # author, update time, and alert area / alert levels
    updated_alert = alerts_models.Alert_Basins_Write(
        alert_description=existing_alert.alert_description,
        alert_hydro_conditions=existing_alert.alert_hydro_conditions,
        alert_meteorological_conditions=existing_alert.alert_meteorological_conditions,
        author_name=auth,
        alert_status=existing_alert.alert_status,
        alert_created=existing_alert.alert_created,
        alert_updated=datetime.datetime.now(datetime.timezone.utc),
        alert_links=alert_area_list
    )
    return updated_alert


