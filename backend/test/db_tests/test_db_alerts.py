import copy
import datetime
import logging
from typing import List

import pytest
import sqlalchemy
import sqlalchemy.orm.session
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
    session.commit()

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
    session.commit()

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


# fraser and liard are net new, Skeena is an existing record with a new alert level
@pytest.mark.parametrize(
    "new_basin_name,new_alert_level",
    [
        ["Fraser River", None],
        ["Liard", None],
        ["Skeena", "Flood Warning"],
        ["Fraser River", "Flood Watch"],
    ],
)
def test_update_existing_basin_alert_level(
    db_with_alert, alert_dict, alert_basin_write, new_basin_name, new_alert_level
):
    """
    This method gets the two parameters:
        * new_basin_name
        * new_alert_level

    The test will take the default alert record, change the basin name to the new_basin_name
    and the alert_level to the new alert level, then make sure that the changes
    exist in the database, and then also verify that the history of the record
    has been tracked correctly.

    Should:
        * update the existing record in the database
        * create a history record that tracks the changes of the alert / alert levels
          in the database


    :param db_with_alert: database session with the data that is described in
        alert_dict in the database
    :type db_with_alert: session
    :param alert_dict: a dictionary representing the alert that exists in the
        database session
    :type alert_dict: dict
    :param alert_basin_write: same data as the dict, except is in a sqlmodel
        data structure
    :type alert_basin_write: alerts_models.Alert_Basins_Write
    :param alert_data: again same data but as a database model object
    :type alert_data: alerts_models.Alerts
    """
    session = db_with_alert

    # if the basin is new then we overwrite the first record with a new basin
    alert_link_index = 0
    # check if there is already a record, and if there is make sure we are updating
    # that one instead of the default position 0
    alert_link_cntr = 0
    for alert_link in alert_dict["alert_links"]:
        if alert_link["basin"]["basin_name"] == new_basin_name:
            alert_link_index = alert_link_cntr
            break
        alert_link_cntr += 1

    # going to update the sample record that exists in the database, created
    # in the fixture db_with_alert
    old_basin_name = alert_dict["alert_links"][alert_link_index]["basin"]["basin_name"]
    old_alert_level = alert_dict["alert_links"][alert_link_index]["alert_level"][
        "alert_level"
    ]
    if not new_basin_name:
        # if the basin isn't provided then just set it to be old basin.. nothing shoul
        # actually get changed
        new_basin_name = old_basin_name
    if not new_alert_level:
        new_alert_level = old_alert_level

    LOGGER.info(
        f"updating the basin: {old_basin_name}, with the basin {new_basin_name}"
    )
    LOGGER.info(
        f"updating the alert level: {old_alert_level}, with the basin {new_alert_level}"
    )

    # get the record for the recently added basin
    alrt_link_index = 0
    for alert_lnk in alert_basin_write.alert_links:
        LOGGER.debug(f"alert_lnk: {alert_lnk}, {alert_lnk.basin.basin_name}")
        if alert_lnk.basin.basin_name == old_basin_name:
            break
        alrt_link_index += 1

    # modify the basin for an incomming record, simulates the data structure
    # that would be comming from an api request
    alert_basin_write.alert_links[alrt_link_index].basin.basin_name = new_basin_name
    alert_basin_write.alert_links[alrt_link_index].alert_level.alert_level = (
        new_alert_level
    )

    # update the alert description with a new timestamp
    alert_basin_write.alert_description = (
        f"updated descriptions {datetime.datetime.now()}"
    )

    # getting the alert record that is going to be updated, only so we can retrieve
    # the alert_id, that is required for the update_alert method that is being
    # tested
    alert_data_sql = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_description == alert_dict["alert_description"]
    )
    alert_data = session.exec(alert_data_sql).one()

    # now call the update method, to update the database
    updated_record = crud_alerts.update_alert(
        session=session,
        alert_id=alert_data.alert_id,
        updated_alert=alert_basin_write,
    )

    LOGGER.debug(f"updated_record: {updated_record}")
    assert crud_alerts.is_alert_equal(updated_record, alert_basin_write)
    assert crud_alerts.is_alert_equal(updated_record, alert_data)

    # assert that the updated record contains what it should
    alert_query = (
        select(
            alerts_models.Alert_Areas, basins_model.Basins, alerts_models.Alert_Levels
        )
        .where(alerts_models.Alert_Areas.alert_id == updated_record.alert_id)
        .where(alerts_models.Alert_Areas.basin_id == basins_model.Basins.basin_id)
        .where(
            alerts_models.Alert_Areas.alert_level_id
            == alerts_models.Alert_Levels.alert_level_id
        )
        .where(basins_model.Basins.basin_name == new_basin_name)
    )
    LOGGER.debug(f"sql: {alert_query}")
    query_record = session.exec(alert_query).first()
    assert query_record.Basins.basin_name == new_basin_name
    assert query_record.Alert_Levels.alert_level == new_alert_level

    # get the history record for this alert
    history_record = crud_alerts.get_latest_history(
        session=session, alert_id=updated_record.alert_id
    )

    # for alert_history_link in history_record.alert_history_links:
    #     LOGGER.debug(f"area_lvl: {alert_history_link}")
    LOGGER.debug(f"history_record: {history_record}")
    # need to verify that the history record relationship to the history area
    # is the same as the alert record, prior to the update.
    hist_basin_lvls = []
    for hist_rec in history_record:
        hist_basin_lvls.append(
            [hist_rec.Basins.basin_name, hist_rec.Alert_Levels.alert_level]
        )

    # now get the basin / levels from the original data:
    original_basin_lvls = []
    for alert_link in alert_dict["alert_links"]:
        original_basin_lvls.append(
            [
                alert_link["basin"]["basin_name"],
                alert_link["alert_level"]["alert_level"],
            ]
        )

    # sort for comparison
    original_basin_lvls.sort()
    hist_basin_lvls.sort()
    LOGGER.debug(f"orginal levels: {original_basin_lvls}")
    LOGGER.debug(f"hist levels: {hist_basin_lvls}")
    assert original_basin_lvls == hist_basin_lvls


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
    alert_data = session.exec(alert_data_sql).one()
    # now call the update method, to update the database
    updated_record = crud_alerts.update_alert(
        session=session,
        alert_id=alert_data.alert_id,
        updated_alert=alert_basin_write,
    )
    LOGGER.debug(f"updated_record.alert_links: {updated_record.alert_links}")
    # verify that the link has been removed by checking the length of the alert links
    assert len(updated_record.alert_links) != len(alert_dict["alert_links"])


def test_is_alert_equal(db_with_alert: Session, alert_data: alerts_models.Alerts):
    session = db_with_alert

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
    assert different_obj_not_equal == False

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
    assert different_obj_not_equal2 == False
    assert different_obj_not_equal2 == False
