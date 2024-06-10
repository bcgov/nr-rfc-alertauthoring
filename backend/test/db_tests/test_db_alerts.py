import datetime
import logging
from typing import List

import pytest
from helpers.alert_helpers import (
    create_alertlvl_basin_dict,
    create_fake_alert,
)
from sqlmodel import Session, select
from src.types import AlertAreaLevel
from src.v1.crud import crud_alerts
from src.v1.models import alerts as alerts_models
from src.v1.models import basins as basins_model

LOGGER = logging.getLogger(__name__)


def test_create_alert_with_basins_and_level(
    db_test_connection: Session,
) -> List[AlertAreaLevel]:
    # tests the crud functions in the crud_alerts.py file
    test_levels: List[AlertAreaLevel] = [
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
    alert = alerts_models.Alerts(
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
    alert_select = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_updated == alert.alert_updated
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
    alerts_list = crud_alerts.get_alerts(session=session)
    alert_id = alerts_list[0].alert_id
    alert_single = crud_alerts.get_alert(session=session, alert_id=alert_id)
    LOGGER.debug(f"alert data: {alert_single}")
    assert alert_single.alert_id == alert_id


def test_update_alert_parameter(
    db_with_alert: Session, alert_data_only: alerts_models.Alerts
):
    """
    tests the update method to update the alert_description attribute of an
    alert record.

    Verifies:
    * the alert record is updated
    * a history record is created, that shows the previous state of the alert
    * makes sure the other attributes have not been modified

    :param db_with_alert: incomming database session with an existing alert in it
    :type db_with_alert: Session
    :param alert_data_only: the alert data as a SQLMODEL data struct that exists
        in the database
    :type alert_data_only: alerts_models.Alerts
    """

    session = db_with_alert
    # for this test to work the data created by the fixtures needs to be written
    # to the database.
    session.add(alert_data_only)
    session.flush()

    # query for the record described in alert_data
    alert_query = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_id == alert_data_only.alert_id
    )
    alert_record = session.exec(alert_query)
    alert_record_results = alert_record.all()
    # cache the state of the record in a dict so can verify later that the
    # correct changes have been made in the database by the update method
    alert_record_dict = crud_alerts.results_to_dict(alert_record_results)[0]

    # create Alert_Basins_Write which is sent to the crud method, copying most
    # of the info from the original record
    alert_description = f"new description with timestamp: {datetime.datetime.now()}"
    alert_write_record = alerts_models.Alert_Basins_Write(
        alert_description=alert_description,
        alert_hydro_conditions=alert_record_dict["alert_hydro_conditions"],
        alert_meteorological_conditions=alert_record_dict[
            "alert_meteorological_conditions"
        ],
        author_name=alert_record_dict["author_name"],
        alert_status=alert_record_dict["alert_status"],
        alert_links=alert_record_results[0].alert_links,
    )

    # before the record gets updated need to write the history record
    crud_alerts.create_history_record(session=session, alert=alert_record_results[0])

    # pass the updated record with the new description to the update_alert
    # function, which should create a new history record and a new alert record
    updated_record = crud_alerts.update_alert(
        session=session,
        alert_id=alert_record_results[0].alert_id,
        updated_alert=alert_write_record,
    )

    # get the history record for this alert and verify it contains the old description
    # value
    alert_history_query = select(alerts_models.Alert_History).where(
        alerts_models.Alert_History.alert_id == alert_record_dict["alert_id"]
    )
    history_data = session.exec(alert_history_query).first()
    assert history_data.alert_description == alert_record_dict["alert_description"]

    # get the alert record independently and verify that the alert_description
    #   has been updated
    post_update_alert_query = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_id == alert_record_dict["alert_id"]
    )
    post_update_alert_record = session.exec(post_update_alert_query).first()
    assert post_update_alert_record.alert_description == alert_description
    assert updated_record.alert_description == alert_description

    # verify that none of the other fields have been changed
    fields_to_check = [
        "alert_id",
        "alert_hydro_conditions",
        "alert_meteorological_conditions",
        "alert_status",
        "author_name",
        "alert_created",
    ]
    for field_to_check in fields_to_check:
        assert getattr(post_update_alert_record, field_to_check) == getattr(
            updated_record, field_to_check
        )

    # verify that the field alert_updated, was updated
    assert updated_record.alert_updated != alert_record_dict["alert_updated"]

    # verify that the alert_history_created field has been updated
    LOGGER.debug(f"history_data record created: {history_data.alert_history_created}")
    assert history_data.alert_history_created is not None

    # test to make sure no history record is created when the data is the same
    # test modifying the basin and alert levels data
    #   - add a new record
    #   - modify a record (basin)
    #   - modify a record (alert level)
    #   - remove a record


def test_add_new_alert_links(db_test_connection, alert_dict, alert_basin_write):
    """
    tests, adding a net new basin / alert level to an existing alert record
    through the update method.

    verifies:
        * the alert has the new basin / alert level associated with it
        * checks that the previous state ov the basin / alert level are tracked
          in the database.

    :param db_test_connection: input database session with an alert record in it
    :type db_test_connection: session
    :param alert_dict: a dictionary representation of the alert record that has
        been written to the database (exists in the session)
    :type alert_dict: dict
    :param alert_basin_write: same as above but in a sqlmodel data structure
    :type alert_basin_write: alerts_models.Alert_Areas_Write
    """
    session = db_test_connection

    # create a new alert record, and write to the db
    # alert_basin_write = alerts_models.Alert_Basins_Write(**alert_dict)
    new_alert = crud_alerts.create_alert(session=session, alert=alert_basin_write)
    # session.commit()

    # now modify the object with a new basin / alert level
    #  - create a new alert_area record to add to the alert, then add it
    basin_name_to_add = "Similkameen"
    alert_level_to_add = "High Streamflow Advisory"
    # creates an alert / areas record, the junction table between basins / alert levels
    # -- establishes the relationship between the alert and those lookup tables
    alert_area_simi_high = crud_alerts.create_area_alert_record(
        session=session,
        basin_name=basin_name_to_add,
        alert_level=alert_level_to_add,
        alert=alert_basin_write,
    )
    alert_basin_write.alert_links.append(alert_area_simi_high)

    # create the history record
    crud_alerts.create_history_record(session=session, alert=new_alert)

    # do the actual update that we are testing
    #   - write the new alert level / basin data to the database
    updated_record = crud_alerts.update_alert(
        session=session,
        alert_id=new_alert.alert_id,
        updated_alert=alert_basin_write,
    )

    # assert that the updated record is the same record as the one that was sent
    assert updated_record.alert_id == new_alert.alert_id

    # verify that the history records have been written for the previous change
    history_query = select(alerts_models.Alert_History).where(
        alerts_models.Alert_History.alert_id == new_alert.alert_id
    )
    history_record = session.exec(history_query).first()
    LOGGER.debug(
        f"history description: {history_record.alert_description}, {new_alert.alert_description}"
    )
    assert history_record.alert_description == new_alert.alert_description
    session.flush()

    # verify that the HISTORY for the alert links has been written:
    #   history record should have the alert_history_id with the basin /
    #   alert levels of the original data
    #  -- query for alert_history for the alert_area_history
    query = (
        select(
            alerts_models.Alert_Area_History,
            alerts_models.Basins,
            alerts_models.Alert_Levels,
        )
        .where(
            alerts_models.Alert_Area_History.alert_history_id
            == history_record.alert_history_id
        )
        .where(
            alerts_models.Alert_Area_History.basin_id == alerts_models.Basins.basin_id
        )
        .where(
            alerts_models.Alert_Area_History.alert_level_id
            == alerts_models.Alert_Levels.alert_level_id
        )
    )
    verify_rec = session.exec(query).all()

    # extract the basin / alert levels from the history query to verify the
    # historical basin alert levels have been recorded
    historical_alert_levels = []
    for (
        alrt_history_data,
        basin_data,
        alert_level_data,
    ) in verify_rec:
        LOGGER.debug(f"history: {alrt_history_data.alert_history_id}")
        LOGGER.debug(f"basin: {basin_data.basin_name}")
        LOGGER.debug(f"alert_level: {alert_level_data}")
        area_level = [
            basin_data.basin_name,
            alert_level_data.alert_level,
        ]
        historical_alert_levels.append(area_level)

    # finally do the assertions that the expected alert levels / basins have
    # been written to the history table
    area_level_cnt = 0
    for area_level in alert_dict["alert_links"]:
        current_area_level = [
            area_level["basin"]["basin_name"],
            area_level["alert_level"]["alert_level"],
        ]
        assert current_area_level in historical_alert_levels
        area_level_cnt += 1

    assert len(historical_alert_levels) == area_level_cnt
    LOGGER.debug(f"verify_rec: {verify_rec}")

    # verify the update of alert record, that it contains the changes that
    # were requested
    alert_query = (
        select(
            alerts_models.Alert_Areas, basins_model.Basins, alerts_models.Alert_Levels
        )
        .where(alerts_models.Alert_Areas.alert_id == new_alert.alert_id)
        .where(alerts_models.Alert_Areas.basin_id == basins_model.Basins.basin_id)
        .where(
            alerts_models.Alert_Areas.alert_level_id
            == alerts_models.Alert_Levels.alert_level_id
        )
        .where(alerts_models.Alert_Areas.alert_id == new_alert.alert_id)
        .where(basins_model.Basins.basin_name == basin_name_to_add)
        .where(alerts_models.Alert_Levels.alert_level == alert_level_to_add)
    )
    LOGGER.debug(f"sql: {alert_query}")
    query_record = session.exec(alert_query).all()
    LOGGER.debug(f"verify_rec: {query_record}")
    assert len(query_record) == 1
    assert query_record[0].Basins.basin_name == basin_name_to_add
    assert query_record[0].Alert_Levels.alert_level == alert_level_to_add
    assert query_record[0].Alert_Areas.alert_id == new_alert.alert_id

    # cleanup... delete the record that was created.


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
def test_alert_history(db_test_connection, existing_alert_list):
    session = db_test_connection

    fake_alert = create_fake_alert(existing_alert_list)
    LOGGER.debug(f"fake_alert: {fake_alert}")
    input_alert = create_fake_alert(existing_alert_list)
    input_alert_db = crud_alerts.create_alert(session=session, alert=input_alert)

    # write the record to history
    crud_alerts.create_history_record(session=session, alert=input_alert_db)

    # now assert that the history record has been written
    history_query = (
        select(alerts_models.Alert_History)
        .where(alerts_models.Alert_History.alert_id == input_alert_db.alert_id)
        .order_by(alerts_models.Alert_History.alert_history_created)
    )

    history_record = session.exec(history_query).first()

    # verify that the history record contains the correct data
    assert history_record.alert_description == input_alert_db.alert_description
    assert history_record.alert_status == input_alert_db.alert_status
    assert (
        history_record.alert_hydro_conditions == input_alert_db.alert_hydro_conditions
    )
    assert (
        history_record.alert_meteorological_conditions
        == input_alert_db.alert_meteorological_conditions
    )
    assert history_record.author_name == input_alert_db.author_name
    assert history_record.alert_updated == input_alert_db.alert_updated

    # create a dictionary of expected basins for easier assertion of history
    # alert area records.
    alert_lvl_basin_dict = create_alertlvl_basin_dict(existing_alert_list)

    # verify related records have been captured
    for history_area in history_record.alert_history_links:
        LOGGER.debug(f"history_area: {history_area}")
        LOGGER.debug(f"history basins: {history_area.basins}")

        assert history_area.alert_levels.alert_level in alert_lvl_basin_dict
        assert (
            history_area.basins.basin_name
            in alert_lvl_basin_dict[history_area.alert_levels.alert_level]
        )


def test_delete_alert_link(db_with_alert, alert_dict, alert_basin_write):
    session = db_with_alert
    # alert_basin_write.__annotations__
    LOGGER.debug(f"alert_basin_write: {alert_basin_write}")
    LOGGER.debug("done")

    # going to remove the first alert link
    link_2_delete = alert_basin_write.alert_links.pop(0)
    LOGGER.debug(f"link_2_delete: {link_2_delete}")

    # now getting the alert id:
    alert_data_sql = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_description == alert_dict["alert_description"]
    )
    # this query fails when run all tests.
    LOGGER.debug(f"alert_data_sql: {alert_data_sql}")
    alert_results = session.exec(alert_data_sql)
    # LOGGER.debug(f"alert_results: {alert_results.all()}")
    # grab the last record
    alert_data = alert_results.all()[-1]
    # now call the update method, to update the database
    updated_record = crud_alerts.update_alert(
        session=session,
        alert_id=alert_data.alert_id,
        updated_alert=alert_basin_write,
    )
    LOGGER.debug(f"updated_record.alert_links: {updated_record.alert_links}")
    # verify that the link has been removed by checking the length of the alert links
    assert len(updated_record.alert_links) != len(alert_dict["alert_links"])


def test_is_alert_equal(db_with_alert: Session, alert_data_only: alerts_models.Alerts):
    session = db_with_alert
    session.add(alert_data_only)
    session.flush()
    alert_data = alert_data_only

    LOGGER.debug(f"query for : {alert_data.alert_id}")
    # query of same alert object
    second_alert_query = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_id == alert_data.alert_id
    )
    second_alert_record = session.exec(second_alert_query).first()

    are_equal = crud_alerts.is_alert_equal(
        alert1=alert_data, alert2=second_alert_record
    )

    # verify that comparison returns true when comparing the same object
    assert are_equal is True

    # adding a new record to a
    new_alert = alerts_models.Alerts(
        alert_created=second_alert_record.alert_created,
        alert_updated=second_alert_record.alert_updated,
        author_name=second_alert_record.author_name,
        alert_status=second_alert_record.alert_status,
        alert_hydro_conditions=second_alert_record.alert_hydro_conditions,
    )

    session.add(new_alert)
    different_obj_not_equal = crud_alerts.is_alert_equal(
        alert1=alert_data, alert2=new_alert
    )
    assert not different_obj_not_equal

    # now add the same areas / alerts to the record
    for alert_link in alert_data.alert_links:
        LOGGER.debug(f"alert_link: {alert_link}")
        alert_area_level = alerts_models.Alert_Areas(
            alert_level_id=alert_link.alert_level_id,
            basin_id=alert_link.basin_id,
            alert=new_alert,
        )
        new_alert.alert_links.append(alert_area_level)
    different_obj_not_equal2 = crud_alerts.is_alert_equal(
        alert1=alert_data, alert2=new_alert
    )
    assert not different_obj_not_equal2
    assert not different_obj_not_equal2


def test_get_alert_levels(db_with_alert: Session, alert_level_data):
    session = db_with_alert
    alert_levels = crud_alerts.get_alert_levels(session=session)
    LOGGER.debug(f"alert_levels: {alert_levels}")

    level_strs = [level.alert_level for level in alert_levels]
    for alert_level in alert_levels:
        assert alert_level.alert_level in level_strs

    assert len(alert_levels) == len(alert_level_data)
