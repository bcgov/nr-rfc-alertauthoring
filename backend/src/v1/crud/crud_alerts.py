import logging

from sqlmodel import Session, select

import src.types
import src.v1.models.alerts as alerts_model
import src.v1.models.basins as basins_model

LOGGER = logging.getLogger(__name__)


def create_alert_with_basins_and_level(
    session: Session,
    alert: alerts_model.Alerts,
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
        basin_query = select(alerts_model.Basins).where(
            alerts_model.Basins.basin_name == basin_level["basin"]
        )
        basin_data = session.exec(basin_query).one()

        alert_level_select = select(alerts_model.Alert_Levels).where(
            alerts_model.Alert_Levels.alert_level == basin_level["alert_level"]
        )
        alert_level_data = session.exec(alert_level_select).one()

        junction_table = alerts_model.Alert_Areas(
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


def create_alert(session: Session, alert: alerts_model.Alert_Basins_Write):
    LOGGER.debug(f"input data: {alert})")
    alert_write: alerts_model.Alerts = alerts_model.Alerts(
        alert_description=alert.alert_description,
        alert_hydro_conditions=alert.alert_hydro_conditions,
        alert_meteorological_conditions=alert.alert_meteorological_conditions,
        author_name=alert.author_name,
        alert_status=alert.alert_status,
    )

    LOGGER.debug(f"alert_write: {alert_write}")
    for alert_area_level in alert.alert_links:
        # get the basin object
        basin_sql = select(basins_model.Basins).where(
            basins_model.Basins.basin_name == alert_area_level.basin.basin_name
        )
        basin = session.exec(basin_sql).first()

        # get the alert level object
        alert_lvl_sql = select(alerts_model.Alert_Levels).where(
            alerts_model.Alert_Levels.alert_level
            == alert_area_level.alert_level.alert_level
        )
        alert_lvl = session.exec(alert_lvl_sql).first()

        LOGGER.debug(f"basin: {basin}")
        LOGGER.debug(f"alert level: {alert_lvl}")

        # using the alert/basin/alert_level to create a junction table
        # entry
        alert_area = alerts_model.Alert_Areas(
            alert_level=alert_lvl, basin=basin, alert=alert_write
        )
        alert_write.alert_links.append(alert_area)
    LOGGER.debug(f"alert_write before write: {alert_write}")
    session.add(alert_write)
    session.commit()
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
    alerts = session.exec(select(alerts_model.Alerts)).all()
    return alerts


def get_alert(session: Session, alert_id: int):
    """
    retrieves an alert record by the primary key

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :param alert_id: the primary key of the alert record to retrieve
    :type alert_id: int
    :return: the alert record
    :rtype: model.Alerts
    """
    alert = session.get(alerts_model.Alerts, alert_id)
    LOGGER.debug(f"single alert retrieval for id: {alert_id} {alert}")
    return alert


def update_alert(session: Session, alert: alerts_model.Alert_Basins_Write):
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
    alert_write = alerts_model.Alerts(
        alert_id=alert.alert_id,
        alert_description=alert.alert_description,
        alert_hydro_conditions=alert.alert_hydro_conditions,
        alert_meteorological_conditions=alert.alert_meteorological_conditions,
        author_name=alert.author_name,
        alert_status=alert.alert_status,
    )
    LOGGER.debug(f"current alert record: {alert_write}")

    for alert_area_level in alert.alert_links:
        # get the basin object
        basin_sql = select(basins_model.Basins).where(
            basins_model.Basins.basin_name == alert_area_level.basin.basin_name
        )
        basin = session.exec(basin_sql).first()

        # get the alert level object
        alert_lvl_sql = select(alerts_model.Alert_Levels).where(
            alerts_model.Alert_Levels.alert_level
            == alert_area_level.alert_level.alert_level
        )
        alert_lvl = session.exec(alert_lvl_sql).first()

        LOGGER.debug(f"basin: {basin}")
        LOGGER.debug(f"alert level: {alert_lvl}")

        # using the alert/basin/alert_level to create a junction table
        # entry
        alert_area = alerts_model.Alert_Areas(
            alert_level=alert_lvl, basin=basin, alert=alert_write
        )
        alert_write.alert_links.append(alert_area)
    session.add(alert_write)
    session.commit()
    session.refresh(alert_write)
    return alert_write
