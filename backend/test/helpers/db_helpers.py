import logging

import src.v1.models.alerts as alerts_models
import src.v1.models.cap as cap_models
from sqlmodel import select

LOGGER = logging.getLogger(__name__)


class db_cleanup:

    def __init__(self, session):
        self.session = session

    def cleanup(self, alert_id: int):
        """
        finds any data that is related to the incomming alert id and deletes it
        from the database.  Returns a session object that needs to be commited
        for the cleanup to be persisted in the database

        :param alert_id: the alert id that needs to be cleaned from the database
        :type alert_id: int
        """
        self.delete_cap_events(alert_id=alert_id)
        self.delete_cap_event_history(alert_id=alert_id)
        self.delete_alert_history(alert_id=alert_id)
        self.delete_alerts(alert_id=alert_id)

    def delete_alerts(self, alert_id: int):
        """
        deletes all the alert records, and the alert area records that are
        associated with the incomming alert id.

        tables effected:
            - alerts
            - alert_areas

        :param alert_id: the alert id that needs to be cleaned from the database
        :type alert_id: int
        """
        # get the alert area records and delete those
        alert_area_query = select(alerts_models.Alert_Areas).where(
            alerts_models.Alert_Areas.alert_id == alert_id
        )
        alert_areas = self.session.exec(alert_area_query).all()
        for alert_area in alert_areas:
            self.session.delete(alert_area)
            self.session.delete(alert_area.alert)
        self.session.flush()

        # The code above should delete the alert and the alert area records
        # Below is a check to make sure that the alert records are deleted
        alerts_query = select(alerts_models.Alerts).where(
            alerts_models.Alerts.alert_id == alert_id
        )
        alerts = self.session.exec(alerts_query).all()
        for alert in alerts:
            LOGGER.info(f"Deleting alert record for alert id: {alert.alert_id}")
            alert.alert_links = []
            self.session.add(alert)
            self.session.refresh(alert)

            self.session.delete(alert)
        self.session.flush()

    def delete_alert_history(self, alert_id: int):
        """
        deletes all the alert history records that relate to the alert id

        Tables effected:
            - Alert_Areas_History
            - Alert_History

        :param alert_id: the alert_id who's related history records should be
            deleted
        :type alert_id: int
        """
        # get the alert history id for the alert id
        alert_history_query = select(alerts_models.Alert_History).where(
            alerts_models.Alert_History.alert_id == alert_id
        )
        alert_history = self.session.exec(alert_history_query).all()
        for alert_hist in alert_history:
            # now get the child records for the alert history
            alert_area_history_query = select(alerts_models.Alert_Area_History).where(
                alerts_models.Alert_Area_History.alert_history_id
                == alert_hist.alert_history_id
            )
            alert_area_history = self.session.exec(alert_area_history_query).all()
            for alert_area_rec in alert_area_history:
                self.session.delete(alert_area_rec)

            self.session.delete(alert_hist)
        self.session.flush()

    def delete_cap_events(self, alert_id: int):
        """
        deletes all the cap areas that are associated with the incomming alert
        id.  This is a helper function for the cleanup function

        :param alert_id: the alert id that needs to be cleaned from the database
        :type alert_id: int
        """
        LOGGER.info(f"deleting cap events for alert id: {alert_id}")
        # get the cap_ids records that relate the the alert id
        caps_query = select(cap_models.Cap_Event).where(
            cap_models.Cap_Event.alert_id == alert_id
        )
        caps = self.session.exec(caps_query).all()
        for cap in caps:
            LOGGER.info(f"Deleting cap areas for cap id: {cap.cap_event_id}")
            cap_area_query = select(cap_models.Cap_Event_Areas).where(
                cap_models.Cap_Event_Areas.cap_event_id == cap.cap_event_id
            )
            cap_areas = self.session.exec(cap_area_query).all()
            for cap_area in cap_areas:
                self.session.delete(cap_area)
            self.session.delete(cap)

        self.session.flush()

    def delete_cap_event_history(self, alert_id: int):
        """
        deletes all cap event history records that relate to the alert id

        Tables effected:
            - Cap_Event_Areas_History
            - Cap_Event_History

        :param alert_id: _description_
        :type alert_id: int
        """
        LOGGER.info(
            f"deleting cap event history records assocated with alert_id: {alert_id}"
        )
        # get the cap event history id for the alert id
        cap_event_history_query = select(cap_models.Cap_Event_History).where(
            cap_models.Cap_Event_History.alert_id == alert_id
        )
        cap_event_history = self.session.exec(cap_event_history_query).all()
        for cap_event_hist in cap_event_history:
            # now get the child records for the cap event history
            cap_event_area_history_query = select(
                cap_models.Cap_Event_Areas_History
            ).where(
                cap_models.Cap_Event_Areas_History.cap_event_history_id
                == cap_event_hist.cap_event_history_id
            )
            cap_event_area_history = self.session.exec(
                cap_event_area_history_query
            ).all()
            for cap_event_area_rec in cap_event_area_history:
                self.session.delete(cap_event_area_rec)

            self.session.delete(cap_event_hist)
        self.session.flush()
