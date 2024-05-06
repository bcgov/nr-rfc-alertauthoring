import datetime
import logging

from sqlmodel import Session, select

import src.v1.models.alerts as alerts_models
import src.v1.models.basins as basins_model
import src.v1.models.cap as cap_models

LOGGER = logging.getLogger(__name__)

def create_cap_event(session: Session,
                     alert: alerts_models.Alerts):
    """
    The alert that will be generated in the database  is recieved as a parameter.
    The method will extract out the alerts and the alert_levels from the alert
    object, and create the necessary CAP Events for the new alert.

    :param session: a database session
    :type session: Session
    :param alert: An alert that is pending to be created in the database
    :type alert: alerts_models.Alert
    """


    LOGGER.debug(f"alert used to create cap: {alert}")
    alert_levels_created = {}

    for alert_link in alert.alert_links:
        LOGGER.debug(f"alert_link to create cap: {alert_link}")
        select_stmt = alert_lvl_rec = ( 
            select(alerts_models.Alert_Levels)
            .where(alerts_models.Alert_Levels.alert_level == alert_link.alert_level.alert_level))
        alert_lvl_rec = session.exec(select_stmt).first()
        LOGGER.debug(f"select_stmt: {select_stmt}")
        LOGGER.debug(f"alert_lvl_rec: {alert_lvl_rec}")
        
        if alert_link.alert_level.alert_level not in alert_levels_created:
            # if the alert level has not been created, create it here, otherwise
            # add the basin the existing cap event for that alert level
            cap_event_area = cap_models.Cap_Event_Areas(
                basin_id=alert_link.basin_id,
            )

            # The line commented below feels like should work to build the relationship
            # between cap event and alert level, however wasn't able to make it work
            # workaround is to just populate the foreign key for alert_level_id
            cap_event = cap_models.Cap_Event(
                # alert_lvl_link=alert_link.alert_level,
                alert_level_id=alert_link.alert_level.alert_level_id,
                alert_id=alert.alert_id,
                cap_event_created_date=datetime.datetime.now(datetime.timezone.utc),
                cap_event_updated_date=datetime.datetime.now(datetime.timezone.utc),
            )
            alert_levels_created[alert_link.alert_level.alert_level] = cap_event
            session.add(cap_event)
            session.flush()
            # now add the relationship
            cap_event.event_areas.append(cap_event_area)
            LOGGER.debug(f"cap_event: {cap_event}")
        else:
            cap_event_area = cap_models.Cap_Event_Areas(
                basin_id=alert_link.basin_id,
            )
            cap_event = alert_levels_created[alert_link.alert_level.alert_level]
            cap_event.event_areas.append(cap_event_area)
            
            # add the basin to the cap_event
            pass
    session.add(cap_event)
    return alert_levels_created.values()
    
def get_cap_events_for_alert(session: Session, alert_id: int):
    """
    Retrieve the CAP events associated with a specific alert

    :param session: a database session
    :type session: Session
    :param alert_id: the alert id
    :type alert_id: int
    """
    LOGGER.debug(f"getting the cap event for alert id: {alert_id}")
    cap_event = session.exec(select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == alert_id)).all()
    return cap_event

def get_cap_events(session: Session):
    """
    retrieves all the cap events in the database

    :param session: _description_
    :type session: Session
    """
    LOGGER.debug(f"getting all the cap events")
    cap_events_query = select(cap_models.Cap_Event)
    LOGGER.debug(f"cap query: {cap_events_query}")
    cap_events = session.exec(cap_events_query).all()
    #LOGGER.debug(f"cap_events: {cap_events}")
    return cap_events

