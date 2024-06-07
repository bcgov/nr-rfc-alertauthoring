import datetime
import logging

import sqlalchemy
from sqlmodel import Session, select

import src.db.session
import src.types
import src.v1.crud.crud_cap as crud_cap
import src.v1.models.alerts as alerts_models
import src.v1.models.basins as basins_model

LOGGER = logging.getLogger(__name__)


def create_alert_with_basins_and_level(
    session: Session,
    alert: alerts_models.Alerts,
    basin_levels: list[src.types.AlertAreaLevel],
):
    """
    using the session creates the alert record, then retrieves the basin and
    alert_level records to get the primary keys for the specified basin_name
    and alert_level.  Then creates a record in the junction table that links
    the alert to the appropriate basin and alert_level.

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :param alert: Alerts data model
    :type alert: model.Alerts
    :param basin_name: the name of the basin that should be associated with the
                       alert
    :type basin_name: str
    :param alert_level: the name of the alert level that should be associated
                        with the alert
    :type alert_level: str
    :return: _description_
    :rtype: _type_
    """
    session.add(alert)
    session.flush()  # flush to populate the primary key

    for basin_level in basin_levels:
        basin_query = select(alerts_models.Basins).where(
            alerts_models.Basins.basin_name == basin_level["basin"]
        )
        basin_data = session.exec(basin_query).one()

        # alert_level_select = select(alerts_models.Alert_Levels).where(
        #     alerts_models.Alert_Levels.alert_level == basin_level["alert_level"]
        # )
        # alert_level_data = session.exec(alert_level_select).one()
        alert_level_data = get_alert_level(
            session=session, alert_lvl_str=basin_level["alert_level"]
        )

        junction_table = alerts_models.Alert_Areas(
            alert=alert,
            basin=basin_data,
            alert_level=alert_level_data,
        )
        # junction_table = model.Alert_Areas(
        #     alert_id=alert.alert_id,
        #     basin_id=basin_data.basin_id,
        #     alert_level_id=alert_level_data.alert_level_id,
        # )

        session.add(junction_table)
        session.flush()

        # logging the primary keys that are added to the association/junction table
        LOGGER.debug(f"alert_id  {alert.alert_id}")
        LOGGER.debug(f"basin_id  {basin_data.basin_id}")
        LOGGER.debug(f"alert_level  {alert_level_data.alert_level_id}")
    return alert


def convert_to_alert(
    session: Session, alert: alerts_models.Alert_Basins_Write
) -> alerts_models.Alerts:
    """
    an object of type Alert_Basins_Write will not include the primary keys to
    the actual lookup tables, but will instead contains only the names of the
    basins / alert levels.  This method will retrieve the primary keys for
    those relationships and return a Alert object with the same data as the
    Alert_Basins_Write object, but with the primary keys included, allowing this
    object to be written to the database.

    :param session: a database session object
    :type session: Session
    :param alert: the input alert object
    :type alert: alerts_models.Alert_Basins_Write
    """
    LOGGER.debug(f"session type: {type(session)}, {type(session)}")

    alert_write: alerts_models.Alerts = alerts_models.Alerts(
        alert_description=alert.alert_description,
        alert_hydro_conditions=alert.alert_hydro_conditions,
        alert_meteorological_conditions=alert.alert_meteorological_conditions,
        author_name=alert.author_name,
        alert_status=alert.alert_status,
    )
    for alert_area_level in alert.alert_links:
        # get the basin object
        basin_sql = select(basins_model.Basins).where(
            basins_model.Basins.basin_name == alert_area_level.basin.basin_name
        )
        LOGGER.debug(
            f"basin_sql: {basin_sql}, {session}, {alert_area_level.basin.basin_name}"
        )
        results = session.exec(basin_sql)
        basin = results.first()

        # get the alert level object
        # alert_lvl_sql = select(alerts_models.Alert_Levels).where(
        #     alerts_models.Alert_Levels.alert_level
        #     == alert_area_level.alert_level.alert_level
        # )
        # alert_lvl = session.exec(alert_lvl_sql).first()
        alert_lvl = get_alert_level(
            session=session, alert_lvl_str=alert_area_level.alert_level.alert_level
        )

        LOGGER.debug(f"basin: {basin}")
        LOGGER.debug(f"alert level: {alert_lvl}")

        # using the alert/basin/alert_level to create a junction table
        # entry
        alert_area = alerts_models.Alert_Areas(
            alert_level=alert_lvl, basin=basin, alert=alert_write
        )
        alert_write.alert_links.append(alert_area)
    return alert_write


def create_history_record(session: Session, alert: alerts_models.Alerts):
    """
    Writes the incomming alert to a history record.  This includes writing the
    history of the related alert level and basin records.

    This method should be called before changes are made to the alert database
    record

    :param session: database session to use to communicate with the db
    :type session: Session
    :param alert: Incomming alert record that should be written as a history
        record
    :type alert: alerts_models.Alerts
    """
    history_record = alerts_models.Alert_History(
        alert_id=alert.alert_id,
        alert_created=alert.alert_created,
        alert_updated=alert.alert_updated,
        alert_description=alert.alert_description,
        alert_hydro_conditions=alert.alert_hydro_conditions,
        alert_meteorological_conditions=alert.alert_meteorological_conditions,
        author_name=alert.author_name,
        alert_status=alert.alert_status,
        alert_history_created=datetime.datetime.now(datetime.timezone.utc),
    )

    LOGGER.debug(f"recording alert history: {history_record}")

    # session.add(history_record)
    # session.flush()  # flush to populate the primary key

    # now handle the relationships to the alert_area_history table
    #             alert_history_id=history_record.alert_history_id,

    for alert_area in alert.alert_links:
        alert_area_history = alerts_models.Alert_Area_History(
            basin_id=alert_area.basin_id,
            alert_level_id=alert_area.alert_level_id,
            alert_history=history_record,
        )
        session.add(alert_area_history)
        history_record.alert_history_links.append(alert_area_history)
    session.add(history_record)
    session.flush()
    return history_record


def create_alert(
    session: Session, alert: alerts_models.Alert_Basins_Write
) -> alerts_models.Alerts:
    LOGGER.debug(f"input data: {alert})")

    alert_write: alerts_models.Alerts = convert_to_alert(session, alert)
    create_time_stamp = datetime.datetime.now(datetime.timezone.utc)
    alert_write.alert_created = create_time_stamp
    alert_write.alert_updated = create_time_stamp

    LOGGER.debug(f"alert_write before write: {alert_write}")
    session.add(alert_write)

    session.flush()
    session.refresh(alert_write)
    return alert_write


def get_alerts(session: Session):
    """
    retrieves all the alert records

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :return: a list of alert records
    :rtype: list[model.Alerts]
    """
    alerts = session.exec(select(alerts_models.Alerts)).all()
    return alerts


def get_alert(session: Session, alert_id: int) -> alerts_models.Alerts:
    """
    retrieves an alert record by the primary key

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :param alert_id: the primary key of the alert record to retrieve
    :type alert_id: int
    :return: the alert record
    :rtype: model.Alerts
    """
    alert_query = select(alerts_models.Alerts).where(
        alerts_models.Alerts.alert_id == alert_id
    )
    LOGGER.debug(f"stmt: {alert_query}")
    # returns with relationships... something wrong here
    # alert_record = session.execute(alert_query).scalars().first()
    # ^ returns a different record??!!! than query below

    alert_record = session.exec(alert_query).first()

    # alert = session.get(alerts_models.Alerts, alert_id)
    LOGGER.debug(f"single alert retrieval for id: {alert_id} {alert_record}")
    return alert_record


# multiple join example: https://stackoverflow.com/questions/74397846/how-to-join-multiple-tables-in-sql-join-using-sqlmodel-and-fastapi
def update_alert(
    session: Session, alert_id: int, updated_alert: alerts_models.Alert_Basins_Write
) -> alerts_models.Alerts:
    """
    updates an alert record,
        A) get the existing record
        B) write the existing record to the history table
        C) get the alert links (basins, alert levels)
        D) write the alert links to the alert_areas_history table
        E) update the alert record
        F) update the alert area records

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :param alert: the alert record to update
    :type alert: model.Alerts
    :return: the updated alert record
    :rtype: model.Alerts
    """
    # create an independent session to query directly what's in the db, vs
    # whats in the incomming session.
    # with Session(src.db.session.engine) as session_2:

    current_alert = get_alert(session=session, alert_id=alert_id)
    LOGGER.debug(f"current alert: {current_alert}")
    LOGGER.debug(f"current alert: {current_alert.alert_description}")

    # need to implement my own comparison
    if not is_alert_equal(current_alert, updated_alert):
        # write the history record
        # TODO: add a test that sends bad data causing the history record write
        #       to fail, then verify that it did not get written to the database
        LOGGER.debug("not the same!")

        # now update the alert record
        attributes_to_update = [
            "alert_description",
            "alert_hydro_conditions",
            "alert_meteorological_conditions",
            "author_name",
            "alert_status",
        ]
        # update core attributes if different
        for atrib in attributes_to_update:
            update_value = getattr(updated_alert, atrib)
            if getattr(current_alert, atrib) != update_value:
                LOGGER.debug(f"updating the atrib: {atrib} with {update_value}")
                setattr(current_alert, atrib, update_value)
                session.add(current_alert)
                session.flush()
        # Dealing with the related basin / alert levels
        # -- get the alert areas / levels incomming
        basin_levels_incomming = []
        for alert_link in updated_alert.alert_links:
            basin_levels_incomming.append(
                [alert_link.basin.basin_name, alert_link.alert_level.alert_level]
            )

        # -- remove the alert areas that are not in the incomming alert but are in existing
        basin_levels_existing = []
        for alert_link in current_alert.alert_links:
            cur_bas_lvl = [
                alert_link.basin.basin_name,
                alert_link.alert_level.alert_level,
            ]
            basin_levels_existing.append(cur_bas_lvl)
            if cur_bas_lvl not in basin_levels_incomming:
                LOGGER.info(
                    f"deleting the alert area: {alert_link.basin.basin_name} {alert_link.alert_level.alert_level}"
                )
                session.delete(alert_link)
                session.flush()  # have to flush or won't update the orm relationship
        session.refresh(current_alert)
        # determine what needs to be added
        alert_area_to_add = []
        for alert_link in updated_alert.alert_links:
            cur_bas_lvl = [
                alert_link.basin.basin_name,
                alert_link.alert_level.alert_level,
            ]

            if cur_bas_lvl not in basin_levels_existing:
                LOGGER.info(
                    "adding the alert area: "
                    + f"{alert_link.basin.basin_name} {alert_link.alert_level.alert_level}"
                )
                alert_area_to_add.append(cur_bas_lvl)
            # elif cur_bas_lvl not in basin_levels_incomming

        # add alert areas that are in incomming but not in existing.
        for alert_link in alert_area_to_add:
            basin_name = alert_link[0]
            alert_level = alert_link[1]
            alert_area = create_area_alert_record(
                session=session,
                basin_name=basin_name,
                alert_level=alert_level,
                alert=current_alert,
            )
            current_alert.alert_links.append(alert_area)
            session.refresh(current_alert)

        current_alert.alert_updated = datetime.datetime.now(datetime.timezone.utc)
        # ---- Alert record update complete

    LOGGER.debug(f"current alert before send: {current_alert}")
    return current_alert


def create_area_alert_record(
    session: Session,
    basin_name: str,
    alert_level: str,
    alert: alerts_models.Alerts | alerts_models.Alert_Basins_Write,
) -> alerts_models.Alert_Areas | alerts_models.Alert_Areas_Write:
    """
    helper / utility record that generates a Alert_Areas record
    given

    :param basin_name: input basin name
    :type basin_name: str
    :param alert_level: input alert level string
    :type alert_level: str
    """

    if isinstance(alert, alerts_models.Alerts):
        basin_sql = select(basins_model.Basins).where(
            basins_model.Basins.basin_name == basin_name
        )
        basin_similk = session.exec(basin_sql).first()

        alert_lvl_sql = select(alerts_models.Alert_Levels).where(
            alerts_models.Alert_Levels.alert_level == alert_level
        )
        alert_lvl = session.exec(alert_lvl_sql).first()

        alert_area = alerts_models.Alert_Areas(
            alert_level=alert_lvl, basin=basin_similk, alert=alert
        )
    else:
        basin_similk = basins_model.BasinBase(basin_name=basin_name)
        alert_lvl = alerts_models.Alert_Levels_Base(alert_level=alert_level)
        alert_area = alerts_models.Alert_Areas_Write(
            alert_level=alert_lvl, basin=basin_similk
        )
    return alert_area


def is_alert_equal(alert1, alert2, core_atributes_only=False):
    """
    compares two alert records, and returns boolean value indicating if they
    are considered equal.

    :param alert1: the first alert record to compare
    :type alert1: dict
    :param alert2: the second alert record to compare
    :type alert2: dict
    :param core_atributes_only: don't check the timestamp attributes
    :type core_atributes_only: bool
    :return: a list of the keys that are different between the two records
    :rtype: list
    """
    is_equal = True
    comparison_fields = [
        "alert_description",
        "alert_hydro_conditions",
        "alert_meteorological_conditions",
        "alert_status",
    ]

    if not core_atributes_only:
        comparison_fields.append("alert_created")
        comparison_fields.append("alert_updated")
    for comp_field in comparison_fields:
        # both objects must have the comp_field or they are not equal
        if hasattr(alert1, comp_field) and hasattr(alert2, comp_field):
            # both alerts have the property, now checking to see if they are not equal
            if getattr(alert1, comp_field) != getattr(alert2, comp_field):
                is_equal = False
                LOGGER.debug(
                    f"the field {comp_field} has these values {getattr(alert1, comp_field)}, and {getattr(alert2, comp_field)}"
                )
                break
        else:
            is_equal = False
            LOGGER.debug(f"missing field: {comp_field}")
            break
    if is_equal:
        # both objects should have an alert_links attribute
        if hasattr(alert1, "alert_links") and hasattr(alert2, "alert_links"):
            # now compare the related fields
            alert_1_ids = []
            for alert_link in alert1.alert_links:
                record = []
                record.append(alert_link.basin.basin_name)
                record.append(alert_link.alert_level.alert_level)
                alert_1_ids.append(record)

            alert_2_ids = []
            for alert_link in alert2.alert_links:
                record = []
                record.append(alert_link.basin.basin_name)
                record.append(alert_link.alert_level.alert_level)
                alert_2_ids.append(record)
            alert_1_ids.sort()
            alert_2_ids.sort()
            if alert_1_ids != alert_2_ids:
                is_equal = False
                LOGGER.debug("alert basin/lvls not equal")
                LOGGER.debug(f"basin/lvls alert1: {alert_1_ids}")
                LOGGER.debug(f"basin/lvls alert1: {alert_2_ids}")
        # if one has the attribute but the other does not then they are not equal
        elif (
            hasattr(alert1, "alert_links") and not hasattr(alert2, "alert_links")
        ) or (not hasattr(alert1, "alert_links") and hasattr(alert2, "alert_links")):
            is_equal = False
    return is_equal


def results_to_dict(result: sqlalchemy.engine.Result):
    """
    _summary_

    :param result: _description_
    :type result: sqlalchemy.engine.Result
    :return: _description_
    :rtype: _type_
    """
    results_list = []
    if isinstance(result, sqlalchemy.engine.Result):
        LOGGER.debug("is a result")
        result_data = result.all()
    else:
        result_data = result
        LOGGER.debug(f"result type: {type(result_data)}")

    for row in result_data:
        try:
            row_dict = row._asdict()
        except AttributeError as e:
            LOGGER.debug(f"exception: {e}")
            row_dict = row.model_dump()

        results_list.append(row_dict)
    return results_list


def get_latest_history(session: Session, alert_id: int):
    """
    retrieves the most recent history record for the specified alert_id

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :param alert_id: the primary key of the alert record to retrieve the history
    :type alert_id: int
    :return: the most recent history record
    :rtype: model.Alert_History
    """
    # find the last history id, then use that to get the last history record
    history_id_query = (
        select(alerts_models.Alert_History)
        .where(alerts_models.Alert_History.alert_id == alert_id)
        .order_by(alerts_models.Alert_History.alert_history_id.desc())
    )
    history_record = session.exec(history_id_query).first()
    LOGGER.debug(f"history_rec: {history_record}")

    # history_query = (
    #     select(
    #         alerts_models.Alert_History,
    #         alerts_models.Alert_Area_History,
    #         alerts_models.Alert_Levels,
    #         basins_model.Basins,
    #     )
    #     .where(alerts_models.Alert_History.alert_id == alert_id)
    #     .where(
    #         alerts_models.Alert_History.alert_history_id
    #         == alerts_models.Alert_Area_History.alert_history_id
    #     )
    #     .where(
    #         alerts_models.Alert_Area_History.alert_level_id
    #         == alerts_models.Alert_Levels.alert_level_id
    #     )
    #     .where(
    #         alerts_models.Alert_Area_History.basin_id == basins_model.Basins.basin_id
    #     )
    #     .where(alerts_models.Alert_History.alert_history_id == history_id_record)
    # )
    # history_query = history_query.order_by(
    #     alerts_models.Alert_History.alert_updated.desc()
    # )
    # LOGGER.debug(f"history query: {history_query}")
    # history_record_result = session.exec(history_query)
    # history_record = history_record_result.first()
    return history_record


def get_alert_levels(session: Session) -> list[alerts_models.Alert_Levels]:
    """
    retrieves all the valid alert levels as defined in the database
    alert levels table

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :return: a list of alert level records
    :rtype: list[model.Alert_Levels]
    """
    LOGGER.debug("get_alert_levels")
    alert_levels = session.exec(select(alerts_models.Alert_Levels)).all()
    LOGGER.debug(f"alert_levels: {alert_levels}")
    return alert_levels


def get_alert_level(session: Session, alert_lvl_str: str) -> alerts_models.Alert_Levels:
    alert_lvl_sql = select(alerts_models.Alert_Levels).where(
        alerts_models.Alert_Levels.alert_level == alert_lvl_str
    )
    alert_lvl = session.exec(alert_lvl_sql).first()
    return alert_lvl
