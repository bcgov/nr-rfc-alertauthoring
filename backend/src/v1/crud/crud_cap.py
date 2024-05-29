import datetime
import logging
from typing import List

from sqlmodel import Session, select

import src.v1.models.alerts as alerts_models
import src.v1.models.basins as basins_models
import src.v1.models.cap as cap_models

LOGGER = logging.getLogger(__name__)


def get_cap_event_status(session: Session, status: str):
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
    select_cap_status = select(cap_models.Cap_Event_Status).where(cap_models.Cap_Event_Status.cap_event_status==status)
    LOGGER.debug(f"select_cap_status: {select_cap_status}")
    cap_status_create_record = session.exec(select_cap_status).first()
    if not cap_status_create_record:
        msg = (
            f"trying to retrieve the record for status={status}, however there" +
              " is no record with that value in the database.")
        raise LookupError(msg)
    LOGGER.debug(f"cap_status_create_record: {cap_status_create_record}")
    return cap_status_create_record

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

    # get the cap_status record for create
    # todo: should create an enum that reads the lookup table or something like that try to make this
    # a safer more consistent query.
    cap_status_create_record = get_cap_event_status(session, 'ALERT')

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
                cap_event_status_id=cap_status_create_record.cap_event_status_id,
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
    LOGGER.debug(f"getting the cap events for alert id: {alert_id}")
    cap_event = session.exec(select(cap_models.Cap_Event).where(
        cap_models.Cap_Event.alert_id == alert_id)).all()
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
    #LOGGER.debug(f"cap_events: {cap_events}")
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
    #existing_caps = get_cap_events_for_alert(session, alert.alert_id)
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

    # write the history record
    record_history(session, alert)

        


    #generate_caps_struct(session, alert)
    # 2. compare generated caps against existing caps identify diffs
    

    # 3. record the diffs to 
    # 3. determine what the changes are:
    #    - new area added to alert UPDATE 
    #    - new area new alert level ALERT/UPDATE
    #    - ...
    #
    # 4. before changes are made cache existing record to history
    LOGGER.debug(f"alert: {alert}")

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
        alert_id=alert.alert_id)
    
    __write_history_for_cap_comp(
        session=session,
        cap_comps=cancels,
        caps_for_alert=cap_events,
        alert_id=alert.alert_id)
        
def __write_history_for_cap_comp(
        session: Session, 
        cap_comps: cap_models.Cap_Comparison, 
        caps_for_alert: List[cap_models.Cap_Event], 
        alert_id: int):
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

        # create a list of the basins that are in the new cap event
        basin_list = []
        for basin in cur_cap_event.event_areas:
            basin_list.append(basins_models.Basins(basin_name=basin.cap_area_basin.basin_name))

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
                basin_id=basin.basin_id
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


class CapCompare():
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

    def generate_incomming_cap_comp_from_alert(self) -> List[cap_models.Cap_Comparison]:
        """
        generates a list of cap comparison objects that can be used to compare
        existing vs future state of cap events, determine what needs to be written
        to history, what caps need to updated.

        :param alert: input alert object containing the new alert state.
        :type alert: 
        """
        levels = {} # used to keep track of which events are associated with what alert level
        for alert_level_area in self.alert.alert_links:
            #basin = alert_level_area.basin
            LOGGER.debug(f"alert_level_area: {alert_level_area}")
            LOGGER.debug(f"alert_level_area.basin: {alert_level_area.basin}")
            LOGGER.debug(f"basin_name: {alert_level_area.basin.basin_name}")
            basinBase = basins_models.BasinBase(basin_name=alert_level_area.basin.basin_name)

            current_level_str = alert_level_area.alert_level.alert_level
            LOGGER.debug(f"alert_level: {current_level_str} basin: {alert_level_area.basin}")
            if current_level_str not in levels:
                alert_lvl = alerts_models.Alert_Levels_Base(alert_level=current_level_str)
                levels[current_level_str] = cap_models.Cap_Comparison(alert_level=alert_lvl, basins=[basinBase])
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
        query = select(cap_models.Cap_Event).where(cap_models.Cap_Event.alert_id==self.alert.alert_id)
        results = self.session.exec(query).all()
        levels = {} # used to keep track of which events are associated with what alert level

        for cap in results:
            LOGGER.debug(f"cap: {cap}")
            alert_lvl_base = alerts_models.Alert_Levels_Base(alert_level=cap.alert_level.alert_level)
            for area_link in cap.event_areas:
                basinBase = basins_models.BasinBase(basin_name=area_link.cap_area_basin.basin_name)
                if alert_lvl_base.alert_level not in levels:
                    levels[cap.alert_level.alert_level] = cap_models.Cap_Comparison(alert_level=alert_lvl_base, basins=[basinBase])
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
        return CapDelta(self.existing_alert_cap_comp, self.new_alert_cap_comp)


class CapDelta:
    def __init__(self, 
                 existing_cap_struct: List[cap_models.Cap_Comparison], 
                 new_cap_struct: List[cap_models.Cap_Comparison]):
        self.existing_cap_struct = existing_cap_struct
        self.new_cap_struct = new_cap_struct
        self.deltas = [] # records the level in here so we know later which levels have changed
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
                self.log_cap(existing_cap) # utility to log whats going on
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

        if self.deltas:
            for alert_level in self.deltas:
                # alert level must exist in both structs
                if alert_level in existing_cap_lvl_dict and alert_level in new_cap_lvl_dict:
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
                            
                        LOGGER.debug(f"basins are not equal! existing: {existing_basin_names}, new: {new_basin_names}")
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
        if self.deltas:
            LOGGER.debug("deltas exist")
            # creates are identified by alert levels that are in the new_cap_struct
            for alert_level in self.deltas:
                if alert_level not in new_cap_lvl_dict:
                    cap_cancels.append(existing_cap_lvl_dict[alert_level])
                    # LOGGER.debug("")
        return cap_cancels

    def is_cap_comp_equal(self, cap_comp1: List[cap_models.Cap_Comparison], cap_comp2: List[cap_models.Cap_Comparison]):
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
