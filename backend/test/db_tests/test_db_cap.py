import logging
import typing

import pytest
from helpers.alert_helpers import create_fake_alert, update_fake_alert
from sqlmodel import Session, select
from src.types import AlertDataDict
from src.v1.crud import crud_alerts, crud_cap
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basin_models
from src.v1.models import cap as cap_models

LOGGER = logging.getLogger(__name__)


def test_create_cap_event(
    db_with_alert_and_data: typing.Tuple[typing.Any, typing.Any],
    alert_dict: typing.Dict,
):
    """
    Tests the creation of a cap event from an alert.  For example, a net new
    alert is created, this method tests that a cap event is created from that
    net new alert

    :param db_with_alert_and_data: database session and a dictionary describing an
        alert that should exist inside that database session
    :type db_with_alert_and_data: typing.List[Session, alerts_models.Alerts]
    :param alert_dict: a dictionary that describes the alert that should contain
        the same data as was used for the alert that was created in the database
    :type alert_dict: typing.Dict
    """
    # TODO: parameterize the test so that it can be run with multiple alerts

    session = db_with_alert_and_data[0]
    alert_data = db_with_alert_and_data[1]

    # create cap events from the alert
    caps = crud_cap.create_cap_event(session=session, alert=alert_data)
    session.flush()
    LOGGER.debug(f"cap: {caps}")

    # create a list of alert levels associated with the current alert
    alert_levels = [
        alert_link["alert_level"]["alert_level"]
        for alert_link in alert_dict["alert_links"]
    ]
    alert_levels = list(set(alert_levels))  # remove any duplicates
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
        alert_basins = [
            alert_link["basin"]["basin_name"]
            for alert_link in alert_dict["alert_links"]
            if alert_link["alert_level"]["alert_level"] == cap.alert_level.alert_level
        ]
        LOGGER.debug(
            f"basins for the alert level {alert_lvl_dict[cap.alert_level.alert_level_id]}: {alert_basins}"
        )

        # now get the basins for the cap event and verify they are in the original
        # alert
        for event_area in cap.event_areas:
            LOGGER.debug(f"event area link: {event_area}")
            LOGGER.debug(
                f"event area link basin: {event_area.cap_area_basin.basin_name}"
            )

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
    nc_query = select(basin_models.Basins).where(
        basin_models.Basins.basin_name == "North Coast"
    )
    nc_record = session.exec(nc_query).first()
    new_alert_area = alerts_models.Alert_Areas(
        alert_id=alert.alert_links[0].alert_id,
        alert_level_id=alert.alert_links[0].alert_level_id,
        basin_id=nc_record.basin_id,
    )
    alert.alert_links.append(new_alert_area)
    LOGGER.debug(f"alert.alert_links: {alert.alert_links}")

    # send to cap update
    crud_cap.update_cap_event(session, alert)


@pytest.mark.parametrize(
    "input_alert_list,updated_alert_list",
    [
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast"],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast"],
                }
            ],
            [{"alert_level": "Flood Watch", "basin_names": ["Central Coast"]}],
        ],
        [
            [{"alert_level": "Flood Watch", "basin_names": ["Central Coast"]}],
            [{"alert_level": "Flood Watch", "basin_names": ["Central Coast"]}],
        ],
        [
            [{"alert_level": "Flood Watch", "basin_names": ["Central Coast"]}],
            [{"alert_level": "Flood Watch", "basin_names": []}],
        ],
    ],
)
def test_record_cap_event_history(
    db_test_connection: Session,
    input_alert_list: typing.List[AlertDataDict],
    updated_alert_list: typing.List[AlertDataDict],
):
    session = db_test_connection

    test_setup_dict = pre_test_setup(
        session=session,
        existing_alert_list=input_alert_list,
        incomming_alert_list=updated_alert_list,
    )
    input_alert_db = test_setup_dict["existing_alert"]
    updated_alert_db = test_setup_dict["incomming_alert"]

    caps = crud_cap.create_cap_event(session=session, alert=input_alert_db)
    LOGGER.debug(f"caps for new alert: {caps}")

    LOGGER.debug(f"input alert: {input_alert_db}, {type(input_alert_db)}")
    LOGGER.debug(f"updated alert: {updated_alert_db}, {type(updated_alert_db)}")

    # now create the cap event history records
    crud_cap.record_history(session, updated_alert_db)

    # finally verify the data in the cap history records created
    for cap_event in caps:
        cap_hist_query = select(alerts_models.Cap_Event_History).where(
            alerts_models.Cap_Event_History.cap_event_id == cap_event.cap_event_id
        )
        cap_hist_records = session.exec(cap_hist_query).all()

        # if there are no changes, then there will not be any history records and
        # this loop will not be entered
        for cap_hist_record in cap_hist_records:
            LOGGER.debug(f"cap_hist_records: {cap_hist_record}")
            LOGGER.debug(
                f"cap_hist_records alert_level: {cap_hist_record.alert_levels}"
            )
            LOGGER.debug(f"cap_hist_records status: {cap_hist_record.cap_event_status}")
            LOGGER.debug(
                f"cap_hist_records areas: {cap_hist_record.cap_event_areas_hist}"
            )

            basin_names = []
            for basin in cap_hist_record.cap_event_areas_hist:
                basin_names.append(basin.basins.basin_name)
                input_alert_dict = [
                    alert
                    for alert in input_alert_list
                    if alert["alert_level"] == cap_hist_record.alert_levels.alert_level
                ][0]
                assert basin.basins.basin_name in input_alert_dict["basin_names"]
            # there should be a record that corresponds with the alert level

            assert (
                cap_hist_record.alert_levels.alert_level
                == input_alert_dict["alert_level"]
            )
    session.rollback()


@pytest.mark.parametrize(
    "existing_alert_list,updated_alert_list",
    [
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
                {
                    "alert_level": "Flood Warning",
                    "basin_names": ["Skeena", "Northwest"],
                },
            ],
        ],
    ],
)
def test_new_cap_for_alert(
    db_test_connection: Session,
    existing_alert_list: typing.List[AlertDataDict],
    updated_alert_list: typing.List[AlertDataDict],
):
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

    test_setup_dict = pre_test_setup(
        session=session,
        existing_alert_list=existing_alert_list,
        incomming_alert_list=updated_alert_list,
    )
    test_setup_dict["existing_alert"]
    updated_alert_db = test_setup_dict["incomming_alert"]
    cap_delta = test_setup_dict["cap_delta"]
    creates = cap_delta.getCreates()

    # create a new cap event for an existing alert
    crud_cap.new_cap_for_alert(
        session=session, alert=updated_alert_db, cap_comps=creates
    )

    # testing to make sure the new cap event for the existing alert is correct

    # - retrieve the existing caps for the alert
    cap_query = select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == updated_alert_db.alert_id
    )
    existing_caps = session.exec(cap_query).all()

    # - verify that the cap events for the alert align with what is expected
    #   - create a dict for lookup of alert levels
    alert_lvl_dict = {}
    for alert_lvl in updated_alert_list:
        alert_lvl_dict[alert_lvl["alert_level"]] = alert_lvl

    for cap in existing_caps:
        LOGGER.debug(f"cap: {cap}")
        # - verify that the alert id is correct
        assert cap.alert_id == updated_alert_db.alert_id

        # - verify that the alert level is correct
        assert cap.alert_level.alert_level in alert_lvl_dict.keys()

        # - verify that the basins are correct
        for event_area in cap.event_areas:
            assert (
                event_area.cap_area_basin.basin_name
                in alert_lvl_dict[cap.alert_level.alert_level]["basin_names"]
            )

    assert len(existing_caps) == len(updated_alert_list)

    # TODO: verify that the cap status is set to ALERT


@pytest.mark.parametrize(
    "existing_alert_list,updated_alert_list",
    [
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                }
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skeena",
                    ],
                },
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skeena",
                    ],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast", "Eastern Vancouver Island"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine", "Skeena"],
                },
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skeena",
                    ],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine", "Skeena"],
                },
            ],
        ],
    ],
)
def test_update_cap_for_alert(
    db_test_connection: Session,
    existing_alert_list: typing.List[AlertDataDict],
    updated_alert_list: typing.List[AlertDataDict],
):
    session = db_test_connection

    test_setup_dict = pre_test_setup(
        session=session,
        existing_alert_list=existing_alert_list,
        incomming_alert_list=updated_alert_list,
    )
    input_alert_db = test_setup_dict["existing_alert"]  # noqa: F841
    updated_alert_db = test_setup_dict["incomming_alert"]
    cap_delta = test_setup_dict["cap_delta"]
    creates = cap_delta.getCreates()
    updates = cap_delta.getUpdates()

    # create a new cap event for an existing alert
    crud_cap.update_cap_for_alert(
        session=session, alert=updated_alert_db, cap_comps=updates
    )

    # now to the assertions
    # - retrieve the existing caps for the alert
    cap_query = select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == updated_alert_db.alert_id
    )
    existing_caps = session.exec(cap_query).all()

    # - verify that the cap events for the alert align with what is expected
    #   - create a dict for lookup of alert levels
    alert_lvl_dict = {}
    for alert_lvl in updated_alert_list:
        alert_lvl_dict[alert_lvl["alert_level"]] = alert_lvl

    for cap in existing_caps:
        LOGGER.debug(f"cap: {cap}")
        # - verify that the alert id is correct
        assert cap.alert_id == updated_alert_db.alert_id

        # - verify that the alert level is correct
        assert cap.alert_level.alert_level in alert_lvl_dict.keys()

        # - verify that the basins are correct
        for event_area in cap.event_areas:
            assert (
                event_area.cap_area_basin.basin_name
                in alert_lvl_dict[cap.alert_level.alert_level]["basin_names"]
            )

    assert len(existing_caps) == len(updated_alert_list)

    # if the cap status is in cap_comparison object for update then should be UPDATE
    # otherwise its a ALERT

    for cap in existing_caps:
        cap.alert_level.alert_level
        if cap_delta.is_alert_level_in_cap_comp(
            cap_comps=updates, alert_level=cap.alert_level.alert_level
        ):
            assert cap.cap_event_status.cap_event_status == "UPDATE"
        elif cap_delta.is_alert_level_in_cap_comp(
            cap_comps=creates, alert_level=cap.alert_level.alert_level
        ):
            assert cap.cap_event_status.cap_event_status == "ALERT"
        else:
            assert cap.cap_event_status.cap_event_status == "CANCEL"

        # Once implement cancel need to add to this logic

    session.rollback()


@pytest.mark.parametrize(
    "existing_alert_list,cancel_alert_list",
    [
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skeena",
                    ],
                }
            ],
            [
                {"alert_level": "High Streamflow Advisory", "basin_names": []},
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": [
                        "Central Coast",
                        "Eastern Vancouver Island",
                        "Skeena",
                    ],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
            [
                {"alert_level": "High Streamflow Advisory", "basin_names": []},
                {"alert_level": "Flood Watch", "basin_names": []},
            ],
        ],
        [
            [
                {
                    "alert_level": "High Streamflow Advisory",
                    "basin_names": ["Central Coast"],
                },
                {
                    "alert_level": "Flood Watch",
                    "basin_names": ["North Coast", "Stikine"],
                },
            ],
            [
                {"alert_level": "High Streamflow Advisory", "basin_names": []},
                {"alert_level": "Flood Watch", "basin_names": []},
            ],
        ],
    ],
)
def test_cancel_cap_for_alert(
    db_test_connection,
    existing_alert_list: typing.List[AlertDataDict],
    cancel_alert_list: typing.List[AlertDataDict],
):
    """
    _summary_

    :param db_test_connection: _description_
    :type db_test_connection: _type_
    :param existing_alert_list: _description_
    :type existing_alert_list: _type_
    :param updated_alert_list: _description_
    :type updated_alert_list: _type_
    """
    session = db_test_connection
    test_setup_dict = pre_test_setup(
        session=session,
        existing_alert_list=existing_alert_list,
        incomming_alert_list=cancel_alert_list,
    )
    input_alert_db = test_setup_dict["existing_alert"]
    cancel_alert_db = test_setup_dict["incomming_alert"]
    cap_delta = test_setup_dict["cap_delta"]

    cancels = cap_delta.getCancels()

    assert cancel_alert_db.alert_id == input_alert_db.alert_id

    # create a new cap event for an existing alert
    crud_cap.cancel_cap_for_alert(
        session=session, alert=cancel_alert_db, cap_comps=cancels
    )

    # now verify that the cancel operation was performed correctly
    # in a nutshell the state in the database should be the same as the previous
    # state, but only the status should be set to CANCEL vs UPDATE or ALERT
    cap_query = select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == cancel_alert_db.alert_id
    )
    cap_data_from_db = session.exec(cap_query).all()
    LOGGER.debug(f"cap_data_from_db: {cap_data_from_db}")

    # need to make sure the database record aligns with the data comming into
    # the test in the parameter `existing_alert_list`.  Organizing the existing_alert_list
    # by alert level to allow for easy lookup
    existing_alert_dict = {}
    for alert in existing_alert_list:
        existing_alert_dict[alert["alert_level"]] = alert["basin_names"]

    # now assert that the caps associated
    for cap in cap_data_from_db:
        # make sure the cap status was modified
        assert cap.cap_event_status.cap_event_status == "CANCEL"

        # make sure the alert id is correct
        assert cap.alert_id == cancel_alert_db.alert_id

        # make sure the alert level corresponds with an alert level that should have a cap
        # associated with it
        assert cap.alert_level.alert_level in existing_alert_dict

        # make sure we have the same number or areas associated with the alert
        assert len(cap.event_areas) == len(
            existing_alert_dict[cap.alert_level.alert_level]
        )

        # make sure the basins are the same
        for event_area in cap.event_areas:
            assert (
                event_area.cap_area_basin.basin_name
                in existing_alert_dict[cap.alert_level.alert_level]
            )
        event_basin_areas = [
            event_area.cap_area_basin.basin_name for event_area in cap.event_areas
        ]
        for basin_name in existing_alert_dict[cap.alert_level.alert_level]:
            assert basin_name in event_basin_areas


@pytest.mark.parametrize(
    "existing_alert_list",
    [
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
        ],
        [
            {
                "alert_level": "High Streamflow Advisory",
                "basin_names": ["Central Coast", "Eastern Vancouver Island"],
            },
            {"alert_level": "Flood Watch", "basin_names": ["Skeena"]},
            {
                "alert_level": "Flood Warning",
                "basin_names": ["Northern Vancouver Island"],
            },
        ],
    ],
)
def test_alert_cancelled(
    db_test_connection, existing_alert_list: typing.List[AlertDataDict]
):
    """
    This test will cancel an alert and then call 'update_caps' method and verify
    that the related caps have been cancelled

    :param db_test_connection: incomming database session
    :type db_test_connection: Session
    :param existing_alert_list: _description_
    :type existing_alert_list: _type_
    """
    session = db_test_connection

    # create an initial alert record
    existing_alert = create_fake_alert(existing_alert_list)
    LOGGER.debug(f"fake_alert: {existing_alert}")
    existing_alert_db = crud_alerts.create_alert(session=session, alert=existing_alert)

    # create the related caps for this alert
    caps = crud_cap.create_cap_event(session=session, alert=existing_alert_db)

    # modify the alert record
    updated_alert = existing_alert
    updated_alert.alert_status = alerts_models.AlertStatus.cancelled.value
    updated_record_db = crud_alerts.update_alert(
        session=session,
        alert_id=existing_alert_db.alert_id,
        updated_alert=updated_alert,
    )
    assert updated_record_db.alert_status == alerts_models.AlertStatus.cancelled.value
    # update the caps
    crud_cap.update_cap_event(session=session, alert=updated_record_db)

    # verify that the caps associated with the alert have all been cancelled.
    cap_query = select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == updated_record_db.alert_id
    )
    cap_data = session.exec(cap_query).all()
    for cap in cap_data:
        LOGGER.debug(f"cap: {cap}")
        # assert cap.cap_event_status.cap_event_status ==
        assert cap.cap_event_status.cap_event_status == "CANCEL"


# Utility Methods to help with setting up test conditions
# ---------------------------------------------------------------------------
# TODO: move these to a helper or utility module


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


def pre_test_setup(
    session: Session,
    existing_alert_list: typing.List[typing.Dict],
    incomming_alert_list: typing.List[typing.Dict],
) -> typing.Dict:
    """
    This is a utility method to help make it easier to define data that goes into
    tests, and what the expected outcome is of that data.

    The method recieves two pieces of information that describe the state of a
    hypothetical alert.  The first piece represents the state of that alert as it
    would exist prior to an update.  The second piece represents the state of the
    incomming changes to that alert.

    The method will create both of the alerts in the database, however it will
    only create caps for the data that represents the existing state of the alert.

    This allows subsequent tests to be written that verify that the anticipated
    changes to the caps are correct.
    """
    # create the fake alerts, and caps.  These represent the existing state before
    # an update is performed
    input_alert = create_fake_alert(existing_alert_list)
    input_alert_db = crud_alerts.create_alert(session=session, alert=input_alert)
    caps = crud_cap.create_cap_event(session=session, alert=input_alert_db)

    LOGGER.debug(f"caps created for alert: {caps}, {type(caps)}")

    # update the alert previously created
    incomming_alert = update_fake_alert(
        existing_alert=input_alert_db, alert_list=incomming_alert_list
    )
    incomming_alert_db = crud_alerts.update_alert(
        session=session, alert_id=input_alert_db.alert_id, updated_alert=incomming_alert
    )
    LOGGER.debug(f"cancel alert: {incomming_alert_db}")

    # generate a cap comp object
    cap_comp = crud_cap.CapCompare(session, incomming_alert_db)
    cap_delta = cap_comp.get_delta()

    return {
        "cap_delta": cap_delta,
        "existing_alert": input_alert_db,
        "incomming_alert": incomming_alert_db,
    }
