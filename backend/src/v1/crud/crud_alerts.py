import logging

from sqlmodel import Session, select

import src.types

LOGGER = logging.getLogger(__name__)


from src.v1.models import model


def create_alert_with_basins_and_level(
    session: Session, alert: model.Alerts, basin_levels: list[src.types.AlertAreaLevel]
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
        basin_query = select(model.Basins).where(
            model.Basins.basin_name == basin_level["basin"]
        )
        basin_data = session.exec(basin_query).one()

        alert_level_select = select(model.Alert_Levels).where(
            model.Alert_Levels.alert_level == basin_level["alert_level"]
        )
        alert_level_data = session.exec(alert_level_select).one()

        junction_table = model.Alert_Areas(
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


def get_alerts(session: Session):
    """
    retrieves all the alert records

    :param session: a SQLModel database session
    :type session: SQLModel.Session
    :return: a list of alert records
    :rtype: list[model.Alerts]
    """
    alerts = session.exec(select(model.Alerts)).all()
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
    alert = session.get(model.Alerts, alert_id)
    LOGGER.debug(f"single alert retrieval for id: {alert_id} {alert}")
    return alert
