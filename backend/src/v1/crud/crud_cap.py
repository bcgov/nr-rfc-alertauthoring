import datetime
import logging
from typing import List

from sqlmodel import Session, select

import src.v1.crud.crud_alerts as crud_alerts
import src.v1.models.alerts as alerts_models
import src.v1.models.basins as basins_models
import src.v1.models.cap as cap_models

LOGGER = logging.getLogger(__name__)


def get_cap_event_status(session: Session, status: str) -> cap_models.Cap_Event_Status:
    """
    queries the cap event status lookup table for the record that corresponds
    with the supplied status string

    :param session: database sqlmodel session
    :type session: sqlmodel.Session
    :param status: the status value for the record we want to retrieve
    :type status: str
    :raises LookupError: error when status supplied cannot be found in the database
    :return: a cap event status record for the status that was queried
    :rtype: cap_models.Cap_Event_Status
    """
    select_cap_status = select(cap_models.Cap_Event_Status).where(
        cap_models.Cap_Event_Status.cap_event_status == status
    )
    LOGGER.debug(f"select_cap_status: {select_cap_status}")
    cap_status_create_record = session.exec(select_cap_status).first()
    if not cap_status_create_record:
        msg = (
            f"trying to retrieve the record for status={status}, however there"
            + " is no record with that value in the database."
        )
        raise LookupError(msg)
    LOGGER.debug(f"cap_status_create_record: {cap_status_create_record}")
    return cap_status_create_record


def create_cap_event(
    session: Session, alert: alerts_models.Alerts
) -> List[cap_models.Cap_Event]:
    """
    The alert that will be generated in the database  is recieved as a parameter.
    The method will extract out the alert areas / basins and the alert_levels from the alert
    object, and create the necessary CAP Events for the new alert.

    :param session: a database session
    :type session: Session
    :param alert: An alert that is pending to be created in the database
    :type alert: alerts_models.Alert
    """
    LOGGER.debug(f"alert used to create cap: {alert}")
    alert_levels_created = {}

    # get the cap_status record for create
    # todo: should create an enum that reads the lookup table or something like that try to make this
    # a safer more consistent query.
    cap_status_create_record = get_cap_event_status(session, "ALERT")

    # organize the alert links by alert level and the basin names that are associated
    # into a cap comp object
    cap_comp = CapCompare(session=session, alert_incomming=alert)
    cap_delta = cap_comp.get_delta()
    creates = cap_delta.getCreates()
    LOGGER.debug(f"creates: {creates}")

    # create the caps for the alert from the cap comp object
    caps = new_cap_for_alert(session=session, alert=alert, cap_comps=creates)
    return caps


def get_cap_events_for_alert(session: Session, alert_id: int):
    """
    Retrieve the CAP events associated with a specific alert

    :param session: a database session
    :type session: Session
    :param alert_id: the alert id
    :type alert_id: int
    """
    LOGGER.debug(f"getting the cap events for alert id: {alert_id}")
    cap_event = session.exec(
        select(cap_models.Cap_Event).where(cap_models.Cap_Event.alert_id == alert_id)
    ).all()
    return cap_event


def get_cap_events(session: Session):
    """
    retrieves all the cap events in the database

    :param session: _description_
    :type session: Session
    """
    cap_events_query = select(cap_models.Cap_Event)
    LOGGER.debug(f"cap query: {cap_events_query}")
    cap_events = session.exec(cap_events_query).all()
    # LOGGER.debug(f"cap_events: {cap_events}")
    return cap_events


def update_cap_event(session: Session, alert: alerts_models.Alerts):
    """
    This method will handle the various operations that need to take place when
    an alert is edited.

    Steps taken:
        - calculate the cap events for the input alert
        - query for existing cap events in the database for the current alert
        - calculate the differences between the two sets of caps and determine
            which caps need to be updated and how
        - write existing state of caps that are to be changed to the cap history
            tables
        - write updates to the caps that have changed

    See docs/

    :param session: input database session
    :type session: sqlmodel.Session
    :param alert: The updated state to an alert object
    :type alert: alerts_models.Alerts
    """
    # 1. generate caps for the current the alert

    # caps = get_cap_events_for_alert(session, alert_id: int):
    # existing_caps = get_cap_events_for_alert(session, alert.alert_id)
    cap_comp = CapCompare(session, alert)
    cap_delta = cap_comp.get_delta()

    # from the delta we can retrieve the CREATE / UPDATE / CANCEL caps
    creates = cap_delta.getCreates()
    updates = cap_delta.getUpdates()
    cancels = cap_delta.getCancels()

    # only write history records if there are changes
    if creates or updates or cancels:
        record_history(session, alert)

        LOGGER.debug(f"creates: {creates}")
        LOGGER.debug(f"updates: {updates}")
        LOGGER.debug(f"cancels: {cancels}")

        # create new caps for new alert levels
        new_cap_for_alert(session=session, alert=alert, cap_comps=creates)
        # need a method to update existing cap - update
        update_cap_for_alert(session=session, alert=alert, cap_comps=updates)
        # need a method to cancel existing cap - cancel
        cancel_cap_for_alert(session=session, alert=alert, cap_comps=cancels)


def cancel_cap_for_alert(
    session: Session, alert: alerts_models.Alerts, cap_comps: cap_models.Cap_Comparison
):
    """
    Updates the status of existing caps to cancel when the basins associated with
    an alert drops to zero.

    For cancels the existing cap event in the database, stays the same as it was
    however the status of the cap event is updated to cancel, and the existing
    state is stored in the cap_event_history table.

    :param session: input database transaction / session
    :type session: Session
    :param alert: Incomming alert that is being cancelled
    :type alert: alerts_models.Alerts
    :param cap_comps: a cap comparison object that describes the cancels that need
        to be issued.
    :type cap_comps: cap_models.Cap_Comparison
    """
    LOGGER.debug(f"cap_comps: {cap_comps}")
    cap_cancel_event_status = get_cap_event_status(session, "CANCEL")
    for cap_comp in cap_comps:
        # getting the related alert level record, can retrieve the fk / pk relation
        # from this record.
        alert_level_record = crud_alerts.get_alert_level(
            session, alert_lvl_str=cap_comp.alert_level.alert_level
        )
        LOGGER.debug(f"alert_level_record: {alert_level_record}")

        # retrieve the cap event for the alert level and cap
        cap_query = (
            select(cap_models.Cap_Event)
            .where(cap_models.Cap_Event.alert_id == alert.alert_id)
            .where(
                cap_models.Cap_Event.alert_level_id == alert_level_record.alert_level_id
            )
        )
        LOGGER.debug(f"cap_query: {cap_query}")
        cur_cap_event = session.exec(cap_query).all()
        if len(cur_cap_event) > 1:
            msg = (
                f"more than one cap event found for the alert id: {alert.alert_id}"
                + f" and alert level: {alert_level_record.alert_level}.  There should "
                + "only ever be one cap event for a given alert level."
            )
            raise LookupError(msg)

        LOGGER.debug(f"cap: {cur_cap_event}")

        # now just update the status of the alert to 'CANCEL'
        cur_cap_event = cur_cap_event[0]

        # update the cap status to 'CANCEL'
        cur_cap_event.cap_event_status_id = cap_cancel_event_status.cap_event_status_id
        # cur_cap_event.cap_event_status = cap_cancel_event_status
        session.add(cur_cap_event)
        session.flush()  # without the flush here the changes seem to be getting overwritten
        session.refresh(
            cur_cap_event
        )  # update the related attributes after update of fk
        LOGGER.debug(f"{cur_cap_event=}")
    session.flush()


def update_cap_for_alert(
    session: Session, alert: alerts_models.Alerts, cap_comps: cap_models.Cap_Comparison
):
    """
    This method will modify existing alerts who's associated basins have been
    modified.

    :param session: input database transaction / session
    :type session: Session
    :param alert: the updated alert for which associated caps must be updated
    :type alert: alerts_models.Alerts
    :param cap_comps: a cap comparison object that describes the updates that
        need to be made to existing caps.
    :type cap_comps: cap_models.Cap_Comparison
    """
    # TODO: should create an enumeration for cap event status references
    # - retrieve the cap status record for an update, later attach to cap event
    cap_event_status = get_cap_event_status(session, "UPDATE")

    # iterate over the caps comps that describe the alert levels and basins
    # for updates
    for cap_comp in cap_comps:
        # get the alert level record for the cap alert level defined in
        # cap_comp
        alert_level_record = crud_alerts.get_alert_level(
            session, alert_lvl_str=cap_comp.alert_level.alert_level
        )
        LOGGER.debug(f"alert_level_record: {alert_level_record}")

        # retrieve the cap event for the alert level and cap
        cap_query = (
            select(cap_models.Cap_Event)
            .where(cap_models.Cap_Event.alert_id == alert.alert_id)
            .where(
                cap_models.Cap_Event.alert_level_id == alert_level_record.alert_level_id
            )
        )
        LOGGER.debug(f"cap_query: {cap_query}")
        cur_cap_event = session.exec(cap_query).all()
        if len(cur_cap_event) > 1:
            msg = (
                f"more than one cap event found for the alert id: {alert.alert_id}"
                + f" and alert level: {alert_level_record.alert_level}.  There should "
                + "only ever be one cap event for a given alert level."
            )
            raise LookupError(msg)

        LOGGER.debug(f"cap: {cur_cap_event}")
        # grab the record from the result set
        cur_cap_event = cur_cap_event[0]
        for relation in cur_cap_event.event_areas:
            LOGGER.debug(f"relation: {relation}")
            session.delete(relation)

        # update the cap status to 'UPDATE'
        cur_cap_event.cap_event_status_id = cap_event_status.cap_event_status_id
        session.flush()  # without the flush here the changes seem to be getting overwritten
        # ^ which is really weird as the session is flushed before it gets returned.

        # session.refresh(cur_cap_event)
        LOGGER.debug(
            f"status after update: {cur_cap_event.cap_event_status.cap_event_status}"
        )
        LOGGER.debug(f"the fk: {cap_event_status.cap_event_status_id}")
        for basin in cap_comp.basins:

            basin_inst = basins_models.Basins(basin_name=basin.basin_name)
            session.add(basin_inst)
            cap_event_area = cap_models.Cap_Event_Areas(
                cap_area_basin=basin_inst, cap_event_id=cur_cap_event.cap_event_id
            )
            session.add(cap_event_area)
            cur_cap_event.event_areas.append(cap_event_area)

        session.refresh(cur_cap_event)
        LOGGER.debug(f"areas after update: {cur_cap_event.event_areas}")
        LOGGER.debug(f"cur_cap_event: {cur_cap_event}")
    session.flush()


def new_cap_for_alert(
    session: Session, alert: alerts_models.Alerts, cap_comps: cap_models.Cap_Comparison
):
    """
    When a new alert level is added to an alert, the method will be called to
    create a new cap event for that alert level.  This method is different
    from the create_cap_event method.  The create_cap_event method is used when
    a brand new alert is created and all the alert levels in the cap are new.

    :param session: a database session / transaction
    :type session: Session
    :param alert: the alert that is being updated
    :type alert: alerts_models.Alerts
    :param cap_comp: a cap comparison object that describes the new cap events
        that need to be added.
    :type cap_comp: cap_models.Cap_Comparison
    """
    cap_event_status = get_cap_event_status(session, "ALERT")
    caps_created = []
    for cap_comp in cap_comps:
        alert_level_record = crud_alerts.get_alert_level(
            session, alert_lvl_str=cap_comp.alert_level.alert_level
        )

        cur_cap_event = cap_models.Cap_Event(
            alert_id=alert.alert_id,
            alert_level_id=alert_level_record.alert_level_id,
            cap_event_status_id=cap_event_status.cap_event_status_id,
            cap_event_created_date=datetime.datetime.now(datetime.timezone.utc),
            cap_event_updated_date=datetime.datetime.now(datetime.timezone.utc),
        )
        cap_areas_list = []
        for basin in cap_comp.basins:
            # basin_inst = basins_models.Basins(basin_name=basin.basin_name)
            basin_query = select(basins_models.Basins).where(
                basins_models.Basins.basin_name == basin.basin_name
            )
            basin_inst = session.exec(basin_query).first()

            cap_event_area = cap_models.Cap_Event_Areas(cap_area_basin=basin_inst)
            cap_areas_list.append(cap_event_area)
        cur_cap_event.event_areas = cap_areas_list
        session.add(cur_cap_event)
        caps_created.append(cur_cap_event)
    session.flush()
    return caps_created


def record_history(session: Session, alert: alerts_models.Alerts):
    """
    This method will write the history records for the cap events that are going
    to be updated.  The history records will be written to the cap_event_history.

    the method does the following in order to write the history:
    * extracts the alert_id
    * compares the existing cap events in the database with the incomming alert
        and determines what has changed
    * changes are categorized into updates and cancels.
    * new cap events are ignored as they are new and therfor do not require a history
      record

    :param session: the current database session / transaction
    :type session: Session
    :param alert: the new modified alert, this alert can be compared with the alert
        that currently exists in the database
    :type alert: alerts_models.Alerts
    """
    # retrieve the caps associated with the incomming alert, need this later to figure
    # out attributes from the actual cap event, for the history records
    cap_events = get_cap_events_for_alert(session, alert.alert_id)
    LOGGER.debug(f"cap_events: {cap_events}")

    # looks at the existing alert in the database and compare with the incomming
    # alert to identify how the caps should be updated
    cap_comp = CapCompare(session=session, alert_incomming=alert)
    cap_delta = cap_comp.get_delta()
    updates = cap_delta.getUpdates()
    cancels = cap_delta.getCancels()

    __write_history_for_cap_comp(
        session=session,
        cap_comps=updates,
        caps_for_alert=cap_events,
        alert_id=alert.alert_id,
    )

    __write_history_for_cap_comp(
        session=session,
        cap_comps=cancels,
        caps_for_alert=cap_events,
        alert_id=alert.alert_id,
    )


def __write_history_for_cap_comp(
    session: Session,
    cap_comps: cap_models.Cap_Comparison,
    caps_for_alert: List[cap_models.Cap_Event],
    alert_id: int,
):
    """
    writes a history record for a cap comparison object

    :param session: input database session
    :type session: sqlmodel.Session
    :param cap_comps: a list of cap comparison objects that are used to
    """
    # write a history record for each cap event that is going to be updated
    for update in cap_comps:
        # extracts the cap event that is associated with the current alert level in
        # the update cap comp object
        cur_cap_event = __get_cap_event(caps_for_alert, update.alert_level.alert_level)

        # creating the history record
        cap_event_history = cap_models.Cap_Event_History(
            alert_id=alert_id,
            cap_event_id=cur_cap_event.cap_event_id,
            cap_event_updated_date=cur_cap_event.cap_event_updated_date,
            cap_event_hist_created_date=datetime.datetime.now(datetime.timezone.utc),
            alert_level=cur_cap_event.alert_level.alert_level_id,
            cap_event_status_id=cur_cap_event.cap_event_status.cap_event_status_id,
        )
        session.add(cap_event_history)
        session.flush()

        # now create the basin relationships
        for basin in cur_cap_event.event_areas:
            LOGGER.debug(f"basin: {basin}")
            cap_event_area_hist = cap_models.Cap_Event_Areas_History(
                cap_event_history_id=cap_event_history.cap_event_history_id,
                basin_id=basin.basin_id,
            )
            session.add(cap_event_area_hist)
            LOGGER.debug(f"cap_event_area_hist: {cap_event_area_hist}")
        session.flush()


def __get_cap_event(cap_events: List[cap_models.Cap_Event], alert_level: str):
    """
    gets a list of cap events, searches those cap events for the event that has
    the specified alert level and returns that event

    :param cap_events: a list of cap events
    :type cap_events: List[cap_models.Cap_Event]
    :param alert_level: the alert level for the cap event that we want to extract
    :type alert_level: str
    """
    for cap_event in cap_events:
        if cap_event.alert_level.alert_level == alert_level:
            return cap_event
    return None


class CapCompare:
    """
    a class that allows for the comparison of cap events.  Doesn't store the cap
    event types, those will get calculated later when the cap actually gets
    updated, but instead focuses on the the following attributes:

        * related alert id
        * alert level
        * areas impacted by the alert
    """

    def __init__(self, session: Session, alert_incomming: alerts_models.Alerts):
        self.session = session
        self.alert = alert_incomming
        # ensures the input alert relationships through sqlmodel work. Without
        # this wind up with a valid basin_id but when request the data get None
        session.flush()

        self.new_alert_cap_comp = None
        self.existing_alert_cap_comp = None

        self.generate_incomming_cap_comp_from_alert()
        self.generate_existing_cap_comp_from_alert()

        # self.alert_cancelled = alerts_models.AlertStatus.active

    def generate_incomming_cap_comp_from_alert(self) -> List[cap_models.Cap_Comparison]:
        """
        generates a list of cap comparison objects that can be used to compare
        existing vs future state of cap events, determine what needs to be written
        to history, what caps need to updated.

        :param alert: input alert object containing the new alert state.
        :type alert:
        """
        levels = (
            {}
        )  # used to keep track of which events are associated with what alert level
        for alert_level_area in self.alert.alert_links:
            # basin = alert_level_area.basin
            LOGGER.debug(f"alert_level_area: {alert_level_area}")
            LOGGER.debug(f"alert_level_area.basin: {alert_level_area.basin}")
            LOGGER.debug(f"basin_name: {alert_level_area.basin.basin_name}")
            basinBase = basins_models.BasinBase(
                basin_name=alert_level_area.basin.basin_name
            )

            current_level_str = alert_level_area.alert_level.alert_level
            LOGGER.debug(
                f"alert_level: {current_level_str} basin: {alert_level_area.basin}"
            )
            if current_level_str not in levels:
                alert_lvl = alerts_models.Alert_Levels_Base(
                    alert_level=current_level_str
                )
                levels[current_level_str] = cap_models.Cap_Comparison(
                    alert_level=alert_lvl, basins=[basinBase]
                )
            else:
                levels[current_level_str].basins.append(basinBase)
        LOGGER.debug(f"levels: {levels}")
        self.new_alert_cap_comp = levels.values()

    def generate_existing_cap_comp_from_alert(self) -> List[cap_models.Cap_Comparison]:
        """
        Using the alert_id in the alert object will query the database for the
        existing caps associated with that alert, and structure the data for
        those caps into a cap comparison object
        """
        # query for existing caps.
        query = select(cap_models.Cap_Event).where(
            cap_models.Cap_Event.alert_id == self.alert.alert_id
        )
        results = self.session.exec(query).all()
        levels = (
            {}
        )  # used to keep track of which events are associated with what alert level

        for cap in results:
            LOGGER.debug(f"cap: {cap}")
            alert_lvl_base = alerts_models.Alert_Levels_Base(
                alert_level=cap.alert_level.alert_level
            )
            for area_link in cap.event_areas:
                basinBase = basins_models.BasinBase(
                    basin_name=area_link.cap_area_basin.basin_name
                )
                if alert_lvl_base.alert_level not in levels:
                    levels[cap.alert_level.alert_level] = cap_models.Cap_Comparison(
                        alert_level=alert_lvl_base, basins=[basinBase]
                    )
                else:
                    levels[cap.alert_level.alert_level].basins.append(basinBase)
        self.existing_alert_cap_comp = levels.values()

    def get_delta(self):
        """
        Calculates the differences between the existing cap events and the cap
        events that are associated with the current state of the alert.

        Returns a delta object.  The delta object contains information about
        how the caps should be updated.

        * CREATE - a new alert level has been created that didn't previously exist
                   for this alert
        * UPDATE - an area has been added or removed from the alert
        * CANCEL - All areas associated with the alert have been removed

        The delta object will have methods that provide this information, exammple
        * getCreates()
        * getUpdates()
        * getCancels()

        For more info see the docs on the CapDelta class.
        """
        capDelta = CapDelta(
            self.existing_alert_cap_comp,
            self.new_alert_cap_comp,
            alerts_models.AlertStatus(self.alert.alert_status),
        )
        return capDelta


class CapDelta:
    def __init__(
        self,
        existing_cap_struct: List[cap_models.Cap_Comparison],
        new_cap_struct: List[cap_models.Cap_Comparison],
        incomming_alert_status: alerts_models.AlertStatus,
    ):
        self.existing_cap_struct = existing_cap_struct
        self.new_cap_struct = new_cap_struct
        self.incomming_alert_status = incomming_alert_status

        self.deltas = (
            []
        )  # records the level in here so we know later which levels have changed
        self.__calcDeltas()

    def __calcDeltas(self):
        """
        Adds the alert level string to the self.deltas list if a an alert level exists
        in either existing or new cap structs, but not in both.
        """
        # identify caps in self.new_cap_struct and not in self.existing_cap_struct
        for existing_cap in self.existing_cap_struct:
            if existing_cap in self.new_cap_struct:
                # identifies that existing_cap exists in self.new_cap_struct
                # which identifies that it has not changed.
                LOGGER.debug(f"cap in both: {existing_cap}")
            else:
                # identifies something is different
                LOGGER.debug("cap not in both:")
                self.log_cap(existing_cap)  # utility to log whats going on
                LOGGER.debug("\ncomparison cap...")
                self.deltas.append(existing_cap.alert_level.alert_level)
        for new_cap in self.new_cap_struct:
            if new_cap in self.existing_cap_struct:
                LOGGER.debug(f"cap in both: {existing_cap}")
            else:
                # in new and not in existing
                LOGGER.debug("cap in new, but not existing")
                self.log_cap(new_cap)
                if new_cap.alert_level.alert_level not in self.deltas:
                    self.deltas.append(new_cap.alert_level.alert_level)
        LOGGER.debug(f"deltas: {self.deltas}")

    def __get_cap_comp_dict(self, cap_comp: List[cap_models.Cap_Comparison]):
        """
        returns a dictionary representing the List of cap comparison objects where
        the alert level is the key for the

        :param cap_comp: _description_
        :type cap_comp: _type_
        """
        cap_lvl_dict = {}
        for new_cap in cap_comp:
            cap_lvl_dict[new_cap.alert_level.alert_level] = new_cap
        return cap_lvl_dict

    def log_cap(self, cap_struct: cap_models.Cap_Comparison):
        """
        mostly for debugging... prints the alert_level for the input cap
        and the basins associated with it.

        :param cap_struct: _description_
        :type cap_struct: _type_
        """
        LOGGER.debug(f"level: {cap_struct.alert_level.alert_level}")
        for basin in cap_struct.basins:
            LOGGER.debug(f"    basin: {basin.basin_name}")

    def getCreates(self):
        """
        returns a list of objects to send to create_cap_event method

        creates are identified by alert levels that are in the new_cap_struct and
        not in the existing_cap_struct.
        """
        cap_creates = []

        # create a dict of caps, indexed by their alert levels.
        existing_cap_lvl_dict = self.__get_cap_comp_dict(self.existing_cap_struct)
        new_cap_lvl_dict = self.__get_cap_comp_dict(self.new_cap_struct)

        if self.deltas:
            # creates are identified by alert levels that are in the new_cap_struct
            for alert_level in self.deltas:
                if alert_level not in existing_cap_lvl_dict:
                    cap_creates.append(new_cap_lvl_dict[alert_level])
        return cap_creates

    def getUpdates(self):
        """
        returns a list of objects to sent to update_cap_event method

        updates are identified by alert levels that are in both the new_cap_struct
        and the existing_cap_struct, but have different basins associated with them.

        What gets returned is a list of objects that define the changes that
        have been detected between the existing and new state of the cap
        """
        existing_cap_lvl_dict = self.__get_cap_comp_dict(self.existing_cap_struct)
        new_cap_lvl_dict = self.__get_cap_comp_dict(self.new_cap_struct)

        # updates are issued when the alert level is the same in existing and
        # new cap structs, but the basins are different

        # the updates struct will return the new state of the cap event with either
        # added basins or removed basins
        updates = []

        # if the original alert from which the caps are generated has been
        # set to 'cancelled', then regardless of any other changes, all related
        # caps should be set to cancel.
        # active / cancelled
        if (
            self.incomming_alert_status.value
            == alerts_models.AlertStatus.cancelled.value
        ):
            # don't do anything here, just need to detect that the alert has been
            # cancelled.  The method getCancels will provide the data to issue the
            # cancel.  Will return an empty updates list in this situation.
            LOGGER.debug("alert is cancelled, all caps should be cancelled")
        elif self.deltas:

            #

            for alert_level in self.deltas:
                # alert level must exist in both structs
                if (
                    alert_level in existing_cap_lvl_dict
                    and alert_level in new_cap_lvl_dict
                ):
                    existing_cap = existing_cap_lvl_dict[alert_level]
                    new_cap = new_cap_lvl_dict[alert_level]
                    LOGGER.debug(f"existing cap: {existing_cap}")
                    LOGGER.debug(f"new cap: {new_cap}")

                    if existing_cap.basins != new_cap.basins:
                        # the alert level is the same, but the basins are different
                        # so we need to update the cap event
                        existing_basin_names = []
                        for basin in existing_cap.basins:
                            existing_basin_names.append(basin.basin_name)
                        new_basin_names = []
                        for basin in new_cap.basins:
                            new_basin_names.append(basin.basin_name)

                        LOGGER.debug(
                            f"basins are not equal! existing: {existing_basin_names}, new: {new_basin_names}"
                        )
                        updates.append(new_cap)
        return updates

    def getCancels(self):
        """
        returns a list of objects to send to cancel_cap_event method.

        cancels are identified by alert levels that are in the existing_cap_struct
        and not in the new_cap_struct.
        """
        cap_cancels = []

        # create a dict of caps, indexed by their alert levels.
        existing_cap_lvl_dict = self.__get_cap_comp_dict(self.existing_cap_struct)
        new_cap_lvl_dict = self.__get_cap_comp_dict(self.new_cap_struct)

        LOGGER.debug(f"differences: {self.deltas}")
        if (
            self.incomming_alert_status.value
            == alerts_models.AlertStatus.cancelled.value
        ):
            # goint to iterate over ALL the existing cap structs, and add them
            # to the cancel list
            for alert_level in existing_cap_lvl_dict.keys():
                cap_cancels.append(existing_cap_lvl_dict[alert_level])
        elif self.deltas:
            LOGGER.debug("deltas exist")
            # creates are identified by alert levels that are in the new_cap_struct
            for alert_level in self.deltas:
                if alert_level not in new_cap_lvl_dict:
                    cap_cancels.append(existing_cap_lvl_dict[alert_level])
                    # LOGGER.debug("")
        return cap_cancels

    def is_cap_comp_equal(
        self,
        cap_comp1: List[cap_models.Cap_Comparison],
        cap_comp2: List[cap_models.Cap_Comparison],
    ):
        """
        compares two lists of cap comparison objects to determine if they are equal
        """
        equal = True
        if len(cap_comp1) != len(cap_comp2):
            equal = False
        else:
            # organize by alert level
            cap_comp1_dict = {}
            for cap in cap_comp1:
                basins = []
                for basin in cap.basins:
                    basins.append(basin.basin_name)
                basins.sort()
                cap_comp1_dict[cap.alert_level.alert_level] = basins

            cap_comp2_dict = {}
            for cap in cap_comp2:
                basins = []
                for basin in cap.basins:
                    basins.append(basin.basin_name)
                basins.sort()
                cap_comp2_dict[cap.alert_level.alert_level] = basins

            # ensure each struct has the same alert levels
            alert_lvls_1 = list(cap_comp1_dict.keys())
            alert_lvls_1.sort()
            alert_lvls_2 = list(cap_comp2_dict.keys())
            alert_lvls_2.sort()
            if alert_lvls_1 != alert_lvls_2:
                equal = False

            if equal:
                # now make sure for each alert level they have the same basins
                for lvl in alert_lvls_1:
                    if cap_comp1_dict[lvl] != cap_comp2_dict[lvl]:
                        equal = False
        return equal

    def is_alert_level_in_cap_comp(
        self, cap_comps: List[cap_models.Cap_Comparison], alert_level: str
    ):
        """
        gets a list of cap comp objects and returns true or false based on whether
        the alert level is in the cap comp object.

        :param cap_comp: _description_
        :type cap_comp: _type_
        :param alert_level: _description_
        :type alert_level: _type_
        """
        for cap_comp in cap_comps:
            if cap_comp.alert_level.alert_level == alert_level:
                return True
        return False
